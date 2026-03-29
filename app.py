"""
PromptAnalyzer — Gradio app for evaluating LLM prompts using DeepEval.

Tabs:
  1. Analyze Prompt File  — upload/paste, token cost, INPUT + OUTPUT metrics, save/refine, cheaper alt
  2. Write New Prompt     — free-form editor with PROMPT/CROFT framework auto-detection
  3. Settings             — API key configuration

Evaluation logic      → evaluator.py
Prompt builder        → prompt_builder.py
Pricing config        → config/pricing.py
Suggestion engine     → services/suggestion_engine.py
CSS + HTML rendering  → styles.py

Run:
    uv run python app.py
"""

from __future__ import annotations

import os
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

import gradio as gr
from dotenv import load_dotenv

from config.pricing import (
    ALL_MODELS,
    ANTHROPIC_MODELS,
    GOOGLE_MODELS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    OPENAI_MODELS,
    PROVIDER_FOR_MODEL,
)
from evaluator import (
    refine_prompt,
    refine_skill,
    run_full_evaluation,
)
from prompt_builder import (
    build_prompt,
    detect_framework,
    render_detection_badge,
    render_empty_badge,
)
from services.suggestion_engine import generate_cheaper_alternative
from styles import (
    APP_CSS,
    EMPTY_RESULTS_HTML,
    HEADER_HTML,
    build_all_models_pricing_html,
    build_combined_results_html,
    build_cost_card_html,
    build_metric_cards_html,
    build_output_metric_cards_html,
    build_refinement_html,
    build_skill_refinement_html,
    build_token_saving_suggestion_html,
)

ENV_FILE = Path(".env")

# ---------------------------------------------------------------------------
# API key helpers
# ---------------------------------------------------------------------------


def _load_saved_keys() -> tuple[str, str, str]:
    load_dotenv(ENV_FILE, override=True)
    return (
        os.getenv("OPENAI_API_KEY", ""),
        os.getenv("ANTHROPIC_API_KEY", ""),
        os.getenv("GOOGLE_API_KEY", ""),
    )


def _persist_keys(openai_key: str, anthropic_key: str, google_key: str) -> str:
    openai_key = openai_key.strip()
    anthropic_key = anthropic_key.strip()
    google_key = google_key.strip()

    if not openai_key and not anthropic_key and not google_key:
        return "⚠ Please provide at least one API key."

    errors: list[str] = []
    if openai_key and not openai_key.startswith("sk-"):
        errors.append("OpenAI key should start with 'sk-'.")
    if anthropic_key and not anthropic_key.startswith("sk-ant-"):
        errors.append("Anthropic key should start with 'sk-ant-'.")
    if google_key and not google_key.startswith("AIza"):
        errors.append("Google key should start with 'AIza'.")
    if errors:
        return "⚠ Validation failed: " + " ".join(errors)

    lines: list[str] = []
    if openai_key:
        lines.append(f'OPENAI_API_KEY="{openai_key}"')
        os.environ["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        lines.append(f'ANTHROPIC_API_KEY="{anthropic_key}"')
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    if google_key:
        lines.append(f'GOOGLE_API_KEY="{google_key}"')
        os.environ["GOOGLE_API_KEY"] = google_key

    ENV_FILE.write_text("\n".join(lines) + "\n")
    return "✓ API keys saved to .env and loaded into environment."


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".md", ".txt", ".py", ".yaml", ".yml", ".json"}


def _load_prompt_text(uploaded_file: Any, pasted_text: str) -> tuple[str, str]:
    """Resolve prompt text from whichever input was used."""
    if uploaded_file is not None:
        try:
            path = Path(
                uploaded_file if isinstance(uploaded_file, str) else uploaded_file.name
            )
            return path.read_text(encoding="utf-8", errors="replace"), ""
        except Exception as exc:
            return "", f"Could not read uploaded file: {exc}"

    if pasted_text and pasted_text.strip():
        return pasted_text.strip(), ""

    return "", "Please upload a file or paste content."


# ---------------------------------------------------------------------------
# Token pricing (inline, no separate tab)
# ---------------------------------------------------------------------------


def _count_tokens_single(text: str, model: str) -> int:
    import tiktoken
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))


def _pricing_for_model(text: str, model: str) -> dict[str, Any]:
    pricing = MODEL_PRICING[model]
    tokens = _count_tokens_single(text, model)
    return {
        "model": model,
        "provider": PROVIDER_FOR_MODEL[model],
        "tokens": tokens,
        "input_cost": round(tokens * pricing["input"] / 1_000_000, 6),
        "output_cost": round(tokens * pricing["output"] / 1_000_000, 6),
    }


# ---------------------------------------------------------------------------
# State: store the last analyzed prompt text per session
# ---------------------------------------------------------------------------


_last_prompt_text: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Main analysis pipeline
# ---------------------------------------------------------------------------


def analyze_prompt(
    uploaded_file: Any,
    pasted_text: str,
    selected_model: str,
) -> tuple[str, str]:
    """Full analysis pipeline.

    Steps:
        1. Load prompt text
        2. Token count + pricing (cost card)
        3. Full evaluation (input + output metrics)

    The cheaper-alternative comparison is handled separately by
    the Refine button, so we don't duplicate it here.

    Returns:
        (cost_html, combined_quality_html)
    """
    text, err = _load_prompt_text(uploaded_file, pasted_text)
    if err:
        error_html = f"<p style='color:#dc2626;font-weight:600;'>{err}</p>"
        return error_html, ""

    provider = PROVIDER_FOR_MODEL.get(selected_model, "OpenAI")

    _last_prompt_text["analyze"] = text

    # Step 1: Token cost card
    orig_pricing = _pricing_for_model(text, selected_model)
    cost_html = build_cost_card_html(
        model=selected_model,
        provider=provider,
        tokens=orig_pricing["tokens"],
        input_cost=orig_pricing["input_cost"],
        output_cost=orig_pricing["output_cost"],
    )

    # Step 2: Full evaluation (input metrics + LLM response + output metrics)
    eval_result = run_full_evaluation(text, provider, selected_model)

    for e in eval_result["errors"]:
        cost_html += (
            f"<pre style='color:#dc2626;font-size:12px;'>{e}</pre>"
        )

    combined_html = build_combined_results_html(
        input_scores=eval_result["input_scores"],
        output_scores=eval_result["output_scores"],
        provider=provider,
        input_elapsed=eval_result["input_elapsed"],
        output_elapsed=eval_result["output_elapsed"],
        model=selected_model,
        response_preview=eval_result["response_text"],
    )

    return cost_html, combined_html


# ---------------------------------------------------------------------------
# Analyze tab: Refine handler
# ---------------------------------------------------------------------------


def refine_analyzed_prompt(
    uploaded_file: Any,
    pasted_text: str,
    selected_model: str,
    context: str = "",
) -> str:
    """Refine the skill/agent file from the Analyze tab.

    Pipeline:
      1. Compress — generate a token-efficient version of the skill
      2. Refine  — improve quality of the compressed version
      3. Display — show token savings + refined skill

    Treats the uploaded content as a Skill or Agent definition — not a
    generic prompt.
    """
    text, err = _load_prompt_text(uploaded_file, pasted_text)
    if err:
        return f"<p style='color:#dc2626;font-weight:600;'>{err}</p>"

    original = text.strip()
    provider = PROVIDER_FOR_MODEL.get(selected_model, "OpenAI")

    # Step 1: Compress for token savings
    compressed = original
    try:
        compressed, _reason = generate_cheaper_alternative(
            original, provider, selected_model,
        )
    except Exception:
        pass

    orig_pricing = _pricing_for_model(original, selected_model)
    comp_pricing = _pricing_for_model(compressed, selected_model)

    # Step 2: Refine the compressed version
    try:
        raw = refine_skill(
            compressed, provider, selected_model, context=context.strip(),
        )
        return build_skill_refinement_html(
            raw,
            model=selected_model,
            provider=provider,
            original_tokens=orig_pricing["tokens"],
            refined_tokens=comp_pricing["tokens"],
            original_cost=orig_pricing["input_cost"] + orig_pricing["output_cost"],
            refined_cost=comp_pricing["input_cost"] + comp_pricing["output_cost"],
        )
    except Exception as exc:
        tb = traceback.format_exc()
        return f"<pre style='color:#dc2626;'>Refinement failed:\n{exc}\n\n{tb}</pre>"


# ---------------------------------------------------------------------------
# Analyze tab: Save handler
# ---------------------------------------------------------------------------


def view_skill_content(
    uploaded_file: Any, pasted_text: str,
) -> tuple[str, str, Any, str]:
    """Display the full skill/agent content for viewing/copying.

    Returns:
        (content_text, preview_html, save_btn_update, status_msg)
    """
    text, err = _load_prompt_text(uploaded_file, pasted_text)
    if err:
        return (
            gr.update(value="", visible=False),
            f"<p style='color:#dc2626;font-weight:600;'>{err}</p>",
            gr.update(visible=False),
            "",
        )
    if not text.strip():
        return (
            gr.update(value="", visible=False),
            "<p style='color:#dc2626;font-weight:600;'>No content to display.</p>",
            gr.update(visible=False),
            "",
        )

    line_count = len(text.strip().splitlines())
    char_count = len(text.strip())
    preview_html = (
        f'<div style="display:flex;align-items:center;gap:10px;padding:12px 18px;'
        f'border-radius:10px;background:linear-gradient(135deg,#f0fdf4,#ecfdf5);'
        f'border:1px solid #bbf7d0;margin-bottom:8px;">'
        f'<span style="font-size:18px;">📄</span>'
        f'<span style="font-weight:700;font-size:14px;color:#166534;">Full Content</span>'
        f'<span style="margin-left:auto;font-size:12px;color:#6b7280;">'
        f'{line_count} lines · {char_count:,} characters</span>'
        f'</div>'
    )

    return (
        gr.update(value=text.strip(), visible=True),
        preview_html,
        gr.update(visible=True),
        "Select all text above to copy, or edit and click **Save & Download**.",
    )


def save_skill_to_file(content: str) -> tuple[Any, str]:
    """Write the content box text to a downloadable file.

    Returns:
        (file_update, status_msg)
    """
    if not content or not content.strip():
        return gr.update(visible=False), "⚠ Nothing to save — content is empty."

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="skill_agent_",
        delete=False, encoding="utf-8",
    )
    tmp.write(content.strip())
    tmp.close()

    return gr.update(value=tmp.name, visible=True), "✓ File saved — click the link above to download."


# ---------------------------------------------------------------------------
# Write New Prompt handlers
# ---------------------------------------------------------------------------


def evaluate_new_prompt(
    title: str, text: str, category: str, provider: str, model: str,
) -> tuple[str, str]:
    """Run full evaluation on a user-written prompt.

    Performs the same pipeline as the Analyze tab:
      1. Token count + pricing (cost card)
      2. Input evaluation  — 5 prompt quality metrics
      3. Generate LLM response
      4. Output evaluation — 6 response quality metrics

    Returns:
        (cost_html, combined_results_html)
    """
    if not text.strip():
        err = "<p style='color:#dc2626;font-weight:600;'>Please enter a prompt to evaluate.</p>"
        return err, ""

    prompt = text.strip()

    # Token cost card
    cost_info = _pricing_for_model(prompt, model)
    cost_html = build_cost_card_html(
        model=model,
        provider=provider,
        tokens=cost_info["tokens"],
        input_cost=cost_info["input_cost"],
        output_cost=cost_info["output_cost"],
    )

    # Full evaluation (input + LLM response + output)
    eval_result = run_full_evaluation(prompt, provider, model)

    for e in eval_result["errors"]:
        cost_html += f"<pre style='color:#dc2626;font-size:12px;'>{e}</pre>"

    combined_html = build_combined_results_html(
        input_scores=eval_result["input_scores"],
        output_scores=eval_result["output_scores"],
        provider=provider,
        input_elapsed=eval_result["input_elapsed"],
        output_elapsed=eval_result["output_elapsed"],
        model=model,
        response_preview=eval_result["response_text"],
    )

    return cost_html, combined_html


def _available_providers() -> set[str]:
    """Return the set of providers whose API key is configured."""
    providers: set[str] = set()
    if os.environ.get("OPENAI_API_KEY", "").strip():
        providers.add("OpenAI")
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        providers.add("Anthropic")
    if os.environ.get("GOOGLE_API_KEY", "").strip():
        providers.add("Google")
    return providers


def _all_models_pricing(text: str) -> list[dict[str, Any]]:
    """Compute token count + cost for every model in ALL_MODELS.

    Marks each row as available/unavailable based on whether the
    provider's API key is configured.
    """
    available = _available_providers()
    rows: list[dict[str, Any]] = []
    for m in ALL_MODELS:
        prov = PROVIDER_FOR_MODEL[m]
        p = _pricing_for_model(text, m)
        total = p["input_cost"] + p["output_cost"]
        rows.append({
            "model": m,
            "provider": prov,
            "tokens": p["tokens"],
            "input_cost": p["input_cost"],
            "output_cost": p["output_cost"],
            "total_cost": total,
            "available": prov in available,
        })
    return rows


def refine_new_prompt(
    title: str, text: str, category: str, provider: str, model: str,
) -> tuple[str, str, str]:
    """Refine + compress the prompt, then show all-models pricing.

    Pipeline:
      1. Compress — generate a cheaper, token-efficient version
      2. Refine  — improve quality of the compressed version
      3. Table   — show token/cost comparison across ALL models

    Returns:
        (saving_html, refine_html, pricing_table_html)
    """
    if not text.strip():
        err = "<p style='color:#dc2626;font-weight:600;'>Please enter a prompt to refine.</p>"
        return err, "", ""

    prompt = text.strip()
    saving_html = ""
    refine_html = ""
    table_html = ""

    # Step 1: Compress for cheapest tokens
    compressed_text = prompt
    reason = ""
    try:
        compressed_text, reason = generate_cheaper_alternative(
            prompt, provider, model,
        )
    except Exception as exc:
        reason = f"Compression unavailable: {exc}"

    orig_pricing = _pricing_for_model(prompt, model)
    comp_pricing = _pricing_for_model(compressed_text, model)
    orig_total = orig_pricing["input_cost"] + orig_pricing["output_cost"]
    comp_total = comp_pricing["input_cost"] + comp_pricing["output_cost"]

    saving_html = build_token_saving_suggestion_html(
        original_tokens=orig_pricing["tokens"],
        original_cost=orig_total,
        compressed_tokens=comp_pricing["tokens"],
        compressed_cost=comp_total,
        compressed_text=compressed_text,
        reason=reason,
    )

    # Step 2: Refine the compressed prompt for quality
    try:
        raw = refine_prompt(compressed_text, provider, model)
        refine_html = build_refinement_html(raw, model=model, provider=provider)
    except Exception as exc:
        tb = traceback.format_exc()
        refine_html = (
            f"<pre style='color:#dc2626;'>Refinement failed:\n{exc}\n\n{tb}</pre>"
        )

    # Step 3: All-models pricing table for the refined/compressed prompt
    model_rows = _all_models_pricing(compressed_text)
    table_html = build_all_models_pricing_html(model_rows, model)

    return saving_html, refine_html, table_html


def save_prompt_as_txt(title: str, text: str) -> tuple[str | None, str]:
    """Write prompt to a .txt file and return (path, status_message)."""
    if not text.strip():
        return None, "⚠ Prompt text is empty."
    safe_name = "".join(
        c if c.isalnum() or c in "_ -" else "_"
        for c in (title.strip() or "prompt")
    )[:60] or "prompt"
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", prefix=f"{safe_name}_",
        delete=False, encoding="utf-8",
    )
    tmp.write(text.strip())
    tmp.close()
    return tmp.name, "✓ Ready to download."


def _update_model_choices(provider: str):
    if provider == "OpenAI":
        return gr.update(choices=OPENAI_MODELS, value=OPENAI_MODELS[0])
    if provider == "Google":
        return gr.update(choices=GOOGLE_MODELS, value=GOOGLE_MODELS[0])
    return gr.update(choices=ANTHROPIC_MODELS, value=ANTHROPIC_MODELS[0])


# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------

_ANALYZER_CHOICES = [MODEL_DISPLAY_NAMES[m] for m in ALL_MODELS]
_DISPLAY_TO_MODEL = {v: k for k, v in MODEL_DISPLAY_NAMES.items()}

_EVAL_HEADER = (
    '<div style="display:flex;align-items:center;gap:12px;padding:14px 20px;'
    'border-radius:12px;background:linear-gradient(135deg,#ede9fe,#dbeafe);'
    'border:1px solid #c4b5fd;margin-bottom:16px;">'
    '<span style="font-size:22px;">📊</span>'
    '<div>'
    '<div style="font-size:15px;font-weight:800;color:#4c1d95;">Evaluation Results</div>'
    '<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
    '<strong>Input</strong> (Clarity · Specificity · Completeness · Coherence · Safety) + '
    '<strong>Output</strong> (Relevancy · Hallucination · Bias · Toxicity · Conciseness · Precision)'
    '</div></div></div>'
)


def build_app() -> gr.Blocks:
    from prompt_library import CATEGORIES as PROMPT_CATEGORIES

    openai_key_init, anthropic_key_init, google_key_init = _load_saved_keys()

    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    )

    with gr.Blocks(title="PromptAnalyzer") as app:

        gr.HTML(HEADER_HTML)

        with gr.Accordion("📥 Input Metrics — what do they mean?  (click to expand)", open=False):
            gr.HTML(build_metric_cards_html())

        with gr.Accordion("📤 Output Metrics — what do they mean?  (click to expand)", open=False):
            gr.HTML(build_output_metric_cards_html())

        with gr.Tabs():

            # ═══════════════════════════════════════════════════════════════
            # TAB 1: Analyze Prompt File
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Analyze Prompt File", id="tab-analyze"):
                gr.Markdown(
                    "Upload a **Skill**, **Agent**, or **Subagent** file (or paste content), "
                    "pick a model, and click **Analyze** for token cost + quality scores. "
                    "Then click **Refine** for an optimized version with token savings."
                )

                with gr.Tabs():
                    with gr.Tab("Upload File"):
                        file_upload = gr.File(
                            label="Drag & drop or click to upload (.md .txt .py .yaml .json)",
                            file_types=[".md", ".txt", ".py", ".yaml", ".yml", ".json"],
                            file_count="single",
                        )
                    with gr.Tab("Paste Content"):
                        paste_input = gr.Textbox(
                            label="Paste prompt / agent / skill content here",
                            placeholder="Paste any text content…",
                            lines=10,
                        )

                # Additional context field
                analyze_context = gr.Textbox(
                    label="Additional Context (optional)",
                    placeholder=(
                        "Provide extra context to improve refinement accuracy. "
                        "e.g. JIRA ticket URL, requirements, domain info:\n"
                        "https://company.atlassian.net/browse/PROJ-123\n"
                        "This agent should handle login flows for the Pantheon app…"
                    ),
                    lines=3,
                    info=(
                        "Used during Refine — helps the AI understand the real-world "
                        "use case for this skill/agent."
                    ),
                )

                with gr.Row():
                    model_selector = gr.Dropdown(
                        choices=_ANALYZER_CHOICES,
                        value=_ANALYZER_CHOICES[0],
                        label="Model — controls tokenizer, pricing, and which AI judge runs evaluations",
                        scale=3,
                        interactive=True,
                    )
                    analyze_btn = gr.Button("Analyze", variant="primary", scale=1)

                # Cost card
                analyze_cost_html = gr.HTML(value="", elem_id="analyze-cost-panel")

                # Combined evaluation results (input + output)
                gr.HTML(_EVAL_HEADER)
                analyze_results_html = gr.HTML(value="", elem_id="analyze-results-panel")

                # Action buttons
                with gr.Row():
                    analyze_view_btn = gr.Button(
                        "📄 View & Save Skill / Agent", variant="secondary",
                    )
                    analyze_refine_btn = gr.Button(
                        "✨ Refine Skill / Agent", variant="primary",
                    )

                # View & Save section
                analyze_preview_html = gr.HTML(value="", elem_id="analyze-preview-header")
                analyze_content_box = gr.Textbox(
                    label="Skill / Agent Content (select all → copy, or edit before saving)",
                    lines=15,
                    max_lines=40,
                    visible=False,
                    interactive=True,
                )
                with gr.Row():
                    analyze_save_download_btn = gr.Button(
                        "💾 Save & Download as File", variant="secondary", visible=False,
                    )
                analyze_status = gr.Markdown("")
                analyze_download = gr.File(
                    label="Downloaded file", visible=False, interactive=False,
                )

                # Refine output
                analyze_refine_html = gr.HTML(value="", elem_id="analyze-refine-panel")

            # ═══════════════════════════════════════════════════════════════
            # TAB 2: Write New Prompt
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Write New Prompt", id="tab-new-prompt"):
                gr.Markdown(
                    "Describe your goal — the **PROMPT** or **CROFT** framework is "
                    "auto-detected. Click **Build Structured Prompt**, then **Evaluate** "
                    "to get token cost + **Input** and **Output** quality scores. "
                    "**Refine** or **Save** when ready."
                )

                # ── Prompt builder section ─────────────────────────────
                with gr.Group(elem_classes=["prompt-builder-section"]):
                    gr.HTML(
                        '<div class="section-title">'
                        "🧠 Prompt Builder — 4D Principles "
                        "(Delegation · Description · Discernment · Diligence)"
                        "</div>"
                    )
                    new_idea = gr.Textbox(
                        label="What do you want to accomplish?",
                        placeholder=(
                            "e.g. 'Write a Python function that validates email addresses' "
                            "or 'Explain the difference between REST and GraphQL APIs'"
                        ),
                        lines=3,
                        info="Framework is auto-detected — no LLM call needed.",
                    )
                    new_framework_badge = gr.HTML(value=render_empty_badge())
                    with gr.Row():
                        new_framework_radio = gr.Radio(
                            choices=["PROMPT", "CROFT"],
                            value="PROMPT",
                            label="Framework Override (auto-selected above)",
                            elem_classes=["framework-radio"],
                            info=(
                                "PROMPT — Persona · Request · Output · Method · Purpose · Task  |  "
                                "CROFT — Context · Role · Objective · Format · Tone"
                            ),
                        )
                        new_build_btn = gr.Button(
                            "✨ Build Structured Prompt", variant="primary", scale=0,
                        )

                # ── Prompt editor + controls ───────────────────────────
                with gr.Row():
                    with gr.Column(scale=1):
                        new_title = gr.Textbox(
                            label="Prompt Title", placeholder="My awesome prompt…", max_lines=1,
                        )
                        new_text = gr.Textbox(
                            label="Prompt Text",
                            placeholder="Your structured prompt appears here…",
                            lines=12,
                        )
                    with gr.Column(scale=1):
                        with gr.Row():
                            new_category = gr.Dropdown(
                                choices=PROMPT_CATEGORIES, value="cursor prompt",
                                label="Category",
                            )
                            new_provider = gr.Radio(
                                choices=["OpenAI", "Anthropic", "Google"],
                                value="OpenAI", label="Provider",
                            )
                        new_model = gr.Dropdown(
                            choices=OPENAI_MODELS, value=OPENAI_MODELS[0], label="Model",
                        )
                        with gr.Row():
                            new_evaluate_btn = gr.Button(
                                "Evaluate Prompt", variant="primary",
                            )
                            new_refine_btn = gr.Button(
                                "✨ Refine Prompt", variant="secondary",
                            )
                            new_save_btn = gr.Button(
                                "💾 Save as .txt", variant="secondary",
                            )
                        new_status = gr.Markdown("")
                        new_download = gr.File(
                            label="Download your prompt", visible=False,
                            interactive=False,
                        )

                # ── Results (full width below editor) ─────────────────
                new_cost_html = gr.HTML(value="", elem_id="new-cost-panel")

                gr.HTML(_EVAL_HEADER)
                new_results_html = gr.HTML(
                    value=EMPTY_RESULTS_HTML, elem_id="new-results-panel",
                )

                new_saving_html = gr.HTML(
                    value="", elem_id="new-saving-panel",
                )
                new_refine_html = gr.HTML(
                    value="", elem_id="new-refine-panel",
                )
                new_pricing_table_html = gr.HTML(
                    value="", elem_id="new-pricing-table-panel",
                )

            # ═══════════════════════════════════════════════════════════════
            # TAB 3: Settings
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Settings", id="tab-settings"):
                gr.Markdown("### API Key Configuration")
                gr.Markdown(
                    "Keys are validated, saved to `.env`, and loaded automatically on startup."
                )
                openai_key_input = gr.Textbox(
                    label="OpenAI API Key", placeholder="sk-…",
                    type="password", value=openai_key_init,
                )
                anthropic_key_input = gr.Textbox(
                    label="Anthropic API Key", placeholder="sk-ant-…",
                    type="password", value=anthropic_key_init,
                )
                google_key_input = gr.Textbox(
                    label="Google API Key", placeholder="AIza…",
                    type="password", value=google_key_init,
                )
                save_keys_btn = gr.Button("Save API Keys", variant="primary")
                keys_status = gr.Markdown("")

        # ══════════════════════════════════════════════════════════════════
        # Event wiring
        # ══════════════════════════════════════════════════════════════════

        # Settings
        save_keys_btn.click(
            fn=_persist_keys,
            inputs=[openai_key_input, anthropic_key_input, google_key_input],
            outputs=[keys_status],
        )

        # Analyze tab — main analysis
        def _run_analyze(uploaded_file, pasted_text, display_name):
            model = (
                _DISPLAY_TO_MODEL.get(display_name)
                or (display_name if display_name in ALL_MODELS else ALL_MODELS[0])
            )
            return analyze_prompt(uploaded_file, pasted_text, model)

        analyze_btn.click(
            fn=_run_analyze,
            inputs=[file_upload, paste_input, model_selector],
            outputs=[
                analyze_cost_html,
                analyze_results_html,
            ],
            api_name="analyze_prompt_api",
        )

        # Analyze tab — view content
        analyze_view_btn.click(
            fn=view_skill_content,
            inputs=[file_upload, paste_input],
            outputs=[
                analyze_content_box,
                analyze_preview_html,
                analyze_save_download_btn,
                analyze_status,
            ],
        )

        # Analyze tab — save & download (from the content box)
        analyze_save_download_btn.click(
            fn=save_skill_to_file,
            inputs=[analyze_content_box],
            outputs=[analyze_download, analyze_status],
        )

        # Analyze tab — refine (with context)
        def _refine_analyzed(uploaded_file, pasted_text, display_name, context):
            model = (
                _DISPLAY_TO_MODEL.get(display_name)
                or (display_name if display_name in ALL_MODELS else ALL_MODELS[0])
            )
            return refine_analyzed_prompt(
                uploaded_file, pasted_text, model, context=context,
            )

        analyze_refine_btn.click(
            fn=_refine_analyzed,
            inputs=[file_upload, paste_input, model_selector, analyze_context],
            outputs=[analyze_refine_html],
        )

        # Write New Prompt: framework detection
        def _detect_and_update(idea: str) -> tuple[str, str]:
            fw, reason, confidence = detect_framework(idea)
            return render_detection_badge(fw, reason, confidence), fw

        new_idea.change(
            fn=_detect_and_update,
            inputs=[new_idea],
            outputs=[new_framework_badge, new_framework_radio],
        )

        new_build_btn.click(
            fn=lambda idea, fw: build_prompt(idea, fw),
            inputs=[new_idea, new_framework_radio],
            outputs=[new_text],
        )

        new_provider.change(
            fn=_update_model_choices,
            inputs=[new_provider],
            outputs=[new_model],
        )

        new_evaluate_btn.click(
            fn=evaluate_new_prompt,
            inputs=[new_title, new_text, new_category, new_provider, new_model],
            outputs=[new_cost_html, new_results_html],
        )

        # Write New Prompt — refine + token saving + all-models pricing
        new_refine_btn.click(
            fn=refine_new_prompt,
            inputs=[new_title, new_text, new_category, new_provider, new_model],
            outputs=[new_saving_html, new_refine_html, new_pricing_table_html],
        )

        # Save as .txt
        def _save_and_show(title: str, text: str):
            path, msg = save_prompt_as_txt(title, text)
            visible = path is not None
            return gr.update(visible=visible, value=path), msg

        new_save_btn.click(
            fn=_save_and_show,
            inputs=[new_title, new_text],
            outputs=[new_download, new_status],
        )

    app._theme = theme
    app._css = APP_CSS
    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    app = build_app()
    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=app._theme,
        css=app._css,
        ssr_mode=False,
    )


if __name__ == "__main__":
    main()
