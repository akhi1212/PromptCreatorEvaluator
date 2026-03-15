"""
PromptAnalyzer — Gradio app for evaluating LLM prompts using DeepEval.

This file is the main orchestrator.  It handles:
  - Two UI modes: predefined template (guided inputs) and new prompt (full editor)
  - Prompt persistence (JSON file) and API-key management (.env)
  - Prompt CRUD operations (user-saved prompts)
  - Predefined QA template loading (from prompt_library.py)
  - Gradio UI layout and event wiring

Evaluation logic lives in evaluator.py.
Predefined templates live in prompt_library.py.
All CSS and HTML rendering lives in styles.py.

Run:
    uv run python app.py
"""

from __future__ import annotations

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gradio as gr
from dotenv import load_dotenv

from evaluator import (
    ANTHROPIC_MODELS,
    GOOGLE_MODELS,
    OPENAI_MODELS,
    calculate_token_pricing,
    refine_prompt,
    run_evaluation,
)
from prompt_builder import (
    build_prompt,
    detect_framework,
    render_detection_badge,
    render_empty_badge,
)
from prompt_library import (
    CATEGORIES,
    VISIBLE_CATEGORIES,
    assemble_prompt,
    get_all_templates,
    get_templates_by_category,
    template_dropdown_choices,
)
from styles import (
    APP_CSS,
    EMPTY_PRICING_HTML,
    EMPTY_REFINEMENT_HTML,
    EMPTY_RESULTS_HTML,
    HEADER_HTML,
    build_metric_cards_html,
    build_pricing_table_html,
    build_refinement_html,
    build_results_html,
    build_template_description_html,
)

PROMPTS_FILE = Path("prompts.json")
ENV_FILE = Path(".env")

# Number of always-rendered input fields in the template tab.
# Set to the max input count across visible templates (currently 3).
MAX_TEMPLATE_INPUTS = 3

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def _load_prompts() -> list[dict[str, Any]]:
    """Read saved prompts from the JSON file.

    Returns:
        List of prompt dicts, or empty list if file is missing / corrupt.
    """
    if PROMPTS_FILE.exists():
        try:
            return json.loads(PROMPTS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_prompts(prompts: list[dict[str, Any]]) -> None:
    """Write the full prompts list to disk as pretty-printed JSON."""
    PROMPTS_FILE.write_text(json.dumps(prompts, indent=2, default=str))


def _load_saved_keys() -> tuple[str, str, str]:
    """Load API keys from .env into the environment.

    Returns:
        Tuple of (openai_key, anthropic_key, google_key) — empty strings if unset.
    """
    load_dotenv(ENV_FILE, override=True)
    return (
        os.getenv("OPENAI_API_KEY", ""),
        os.getenv("ANTHROPIC_API_KEY", ""),
        os.getenv("GOOGLE_API_KEY", ""),
    )


def _persist_keys(openai_key: str, anthropic_key: str, google_key: str) -> str:
    """Validate API keys, write them to .env, and load into os.environ.

    Returns:
        A user-facing status message (success or error).
    """
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
# User prompt CRUD
# ---------------------------------------------------------------------------


def _prompt_choices(prompts: list[dict]) -> list[str]:
    """Build display labels for the sidebar dropdown."""
    return [
        f"[{i}] {p.get('title', p.get('text', '')[:40])}"
        for i, p in enumerate(prompts)
    ]


def save_prompt(
    title: str, text: str, category: str, prompts_state: list[dict]
) -> tuple[list[dict], list[str], str]:
    """Append a new prompt to the user's library and persist to disk."""
    if not text.strip():
        return prompts_state, _prompt_choices(prompts_state), "⚠ Prompt text cannot be empty."

    entry = {
        "title": title.strip() or text.strip()[:40],
        "text": text.strip(),
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluations": [],
    }
    prompts_state.append(entry)
    _save_prompts(prompts_state)
    return (
        prompts_state,
        _prompt_choices(prompts_state),
        f"✓ Prompt saved ({len(prompts_state)} total).",
    )


def delete_prompt(
    selected_label: str, prompts_state: list[dict]
) -> tuple[list[dict], list[str], str]:
    """Remove the selected prompt from the user's library."""
    if not selected_label:
        return prompts_state, _prompt_choices(prompts_state), "⚠ No prompt selected."

    idx = int(selected_label.split("]")[0].replace("[", ""))
    removed = prompts_state.pop(idx)
    _save_prompts(prompts_state)
    return (
        prompts_state,
        _prompt_choices(prompts_state),
        f"✓ Deleted: {removed.get('title', 'Untitled')}",
    )


def load_selected_prompt(
    selected_label: str, prompts_state: list[dict]
) -> tuple[str, str, str, str]:
    """Populate the new-prompt editor fields from a user-saved prompt."""
    if not selected_label:
        return "", "", "cursor prompt", ""

    idx = int(selected_label.split("]")[0].replace("[", ""))
    p = prompts_state[idx]

    history = ""
    for ev in p.get("evaluations", []):
        history += f"--- {ev.get('timestamp', '?')} | {ev.get('provider', '?')} ---\n"
        for m, info in ev.get("scores", {}).items():
            history += f"  {m}: {info['score']:.2f} — {info['reason']}\n"
        history += "\n"

    return p.get("title", ""), p.get("text", ""), p.get("category", "cursor prompt"), history


# ---------------------------------------------------------------------------
# Template mode handlers
# ---------------------------------------------------------------------------


def _find_template_by_title(title: str) -> dict[str, Any] | None:
    """Look up a template by its display title."""
    if not title:
        return None
    for t in get_all_templates():
        if t["title"] == title:
            return t
    return None


_CATEGORY_MAP = {
    "Cursor Workflow": "cursor workflow",
    "Analysis": "analysis",
}


def _filter_templates(category_label: str):
    """Update the template dropdown when the category filter changes.

    Maps display labels ("Cursor Workflow", "Analysis") to internal category values.
    Returns updates for the template dropdown only; the .change on the dropdown
    will fire _on_template_selected for the first item.
    """
    cat = _CATEGORY_MAP.get(category_label, category_label)
    choices = template_dropdown_choices(cat)
    first = choices[0] if choices else None
    return gr.update(choices=choices, value=first)


def _on_template_selected(template_title: str):
    """When a template is selected, update input field labels/hints and clear values.

    Returns updates for: description_html, assembled_prompt (cleared),
    and MAX_TEMPLATE_INPUTS input fields (label + placeholder updates).
    """
    t = _find_template_by_title(template_title)

    if not t:
        updates = [
            gr.update(value=""),
            gr.update(value=""),
            gr.update(visible=True, label="Select a template above, then type here",
                      placeholder="...", value=""),
        ]
        for _ in range(MAX_TEMPLATE_INPUTS - 1):
            updates.append(gr.update(visible=False, value=""))
        return updates

    desc_html = build_template_description_html(t["description"], [])
    updates = [
        gr.update(value=desc_html),
        gr.update(value=""),
    ]

    inputs_meta = t.get("inputs", [])
    for i in range(MAX_TEMPLATE_INPUTS):
        if i < len(inputs_meta):
            inp = inputs_meta[i]
            updates.append(gr.update(
                visible=True,
                label=inp["label"],
                placeholder=inp["hint"],
                value="",
                lines=inp.get("lines", 2),
            ))
        else:
            updates.append(gr.update(visible=False, value=""))

    return updates


def _extract_user_values(template_title: str, input_values: list[str]) -> tuple[dict | None, str, str]:
    """Validate inputs and build user_values dict from template + filled fields.

    Inputs marked optional in the template may be empty; they are passed as empty string.

    Returns:
        (user_values_dict, assembled_prompt, error_message)
        If error, user_values is None.
    """
    t = _find_template_by_title(template_title)
    if not t:
        return None, "", "Please select a template first."

    inputs_meta = t.get("inputs", [])
    user_values = {}
    for i, meta in enumerate(inputs_meta):
        val = input_values[i] if i < len(input_values) else ""
        val = (val or "").strip()
        if not val and not meta.get("optional", False):
            return None, "", f"Please fill in: {meta['label']}"
        user_values[meta["key"]] = val if val else ""

    return user_values, assemble_prompt(t["id"], user_values), ""


def _generate_assembled_prompt(template_title: str, *input_values):
    """Assemble the prompt from template + user inputs and show it read-only.

    Returns the assembled prompt string for the textbox.
    """
    vals = list(input_values[:MAX_TEMPLATE_INPUTS])
    user_values, prompt, err = _extract_user_values(template_title, vals)
    if err:
        return f"⚠ {err}"
    return prompt


def _assemble_and_evaluate(template_title: str, *input_values_and_rest):
    """Assemble prompt from template + user inputs, then run evaluation.

    Args order: input_0..input_4, provider, model, prompts_state.
    """
    input_values = list(input_values_and_rest[:MAX_TEMPLATE_INPUTS])
    provider = input_values_and_rest[MAX_TEMPLATE_INPUTS]
    model = input_values_and_rest[MAX_TEMPLATE_INPUTS + 1]
    prompts_state = input_values_and_rest[MAX_TEMPLATE_INPUTS + 2]

    user_values, final_prompt, err = _extract_user_values(template_title, input_values)
    if err:
        return (
            f"<p style='color:#dc2626;font-weight:600;'>{err}</p>",
            prompts_state,
        )

    t = _find_template_by_title(template_title)
    start = time.time()
    try:
        scores = run_evaluation(final_prompt, provider, model)
    except Exception as exc:
        tb = traceback.format_exc()
        return (
            f"<pre style='color:#dc2626;'>Evaluation failed:\n{exc}\n\n{tb}</pre>",
            prompts_state,
        )
    elapsed = time.time() - start

    evaluation_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "template": t["title"],
        "scores": scores,
    }

    prompts_state.append({
        "title": f"[Template] {t['title']}",
        "text": final_prompt,
        "category": t["category"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluations": [evaluation_record],
    })
    _save_prompts(prompts_state)
    return build_results_html(scores, provider, elapsed, model), prompts_state


def _assemble_and_refine(template_title: str, *input_values_and_rest):
    """Assemble prompt from template + user inputs, then run refinement."""
    input_values = list(input_values_and_rest[:MAX_TEMPLATE_INPUTS])
    provider = input_values_and_rest[MAX_TEMPLATE_INPUTS]
    model = input_values_and_rest[MAX_TEMPLATE_INPUTS + 1]

    user_values, final_prompt, err = _extract_user_values(template_title, input_values)
    if err:
        return f"<p style='color:#dc2626;font-weight:600;'>{err}</p>"

    try:
        raw = refine_prompt(final_prompt, provider, model)
        return build_refinement_html(raw)
    except Exception as exc:
        tb = traceback.format_exc()
        return f"<pre style='color:#dc2626;'>Refinement failed:\n{exc}\n\n{tb}</pre>"


# ---------------------------------------------------------------------------
# New prompt mode handlers
# ---------------------------------------------------------------------------


def evaluate_new_prompt(
    title: str, text: str, category: str, provider: str, model: str,
    prompts_state: list[dict],
) -> tuple[str, list[dict]]:
    """Run DeepEval metrics on a user-written prompt, render results, persist."""
    if not text.strip():
        return (
            "<p style='color:#dc2626;font-weight:600;'>Please enter a prompt to evaluate.</p>",
            prompts_state,
        )

    start = time.time()
    try:
        scores = run_evaluation(text.strip(), provider, model)
    except Exception as exc:
        tb = traceback.format_exc()
        return (
            f"<pre style='color:#dc2626;'>Evaluation failed:\n{exc}\n\n{tb}</pre>",
            prompts_state,
        )
    elapsed = time.time() - start

    evaluation_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "scores": scores,
    }

    matched = False
    for p in prompts_state:
        if p.get("text", "").strip() == text.strip():
            p.setdefault("evaluations", []).append(evaluation_record)
            matched = True
            break

    if not matched:
        prompts_state.append({
            "title": title.strip() or text.strip()[:40],
            "text": text.strip(),
            "category": category,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "evaluations": [evaluation_record],
        })

    _save_prompts(prompts_state)
    return build_results_html(scores, provider, elapsed, model), prompts_state


def handle_refine_new(text: str, provider: str, model: str) -> str:
    """Call the LLM to refine a user-written prompt."""
    if not text.strip():
        return "<p style='color:#dc2626;font-weight:600;'>Please enter a prompt first.</p>"
    try:
        raw = refine_prompt(text.strip(), provider, model)
        return build_refinement_html(raw)
    except Exception as exc:
        tb = traceback.format_exc()
        return f"<pre style='color:#dc2626;'>Refinement failed:\n{exc}\n\n{tb}</pre>"


def _update_model_choices(provider: str):
    """Return the model list matching the selected provider."""
    if provider == "OpenAI":
        return gr.update(choices=OPENAI_MODELS, value=OPENAI_MODELS[0])
    if provider == "Google":
        return gr.update(choices=GOOGLE_MODELS, value=GOOGLE_MODELS[0])
    return gr.update(choices=ANTHROPIC_MODELS, value=ANTHROPIC_MODELS[0])


def _handle_calculate_pricing(prompt_text: str) -> str:
    """Calculate token counts and pricing for all configured providers.

    Returns:
        Styled HTML table with token counts and costs.
    """
    if not prompt_text or not prompt_text.strip():
        return "<p style='color:#dc2626;font-weight:600;'>Please enter a prompt first.</p>"
    try:
        results = calculate_token_pricing(prompt_text.strip())
        return build_pricing_table_html(results)
    except Exception as exc:
        tb = traceback.format_exc()
        return f"<pre style='color:#dc2626;'>Pricing calculation failed:\n{exc}\n\n{tb}</pre>"


# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------


def build_app() -> gr.Blocks:
    """Construct the Gradio Blocks application with two-mode Evaluate tab."""
    saved_prompts = _load_prompts()
    openai_key_init, anthropic_key_init, google_key_init = _load_saved_keys()
    # Initial template list = Cursor Workflow (no "all"); user picks category then template.
    default_category = "cursor workflow"
    initial_template_choices = template_dropdown_choices(default_category)
    # First template as default so dropdown has a valid selection (fixes Gradio dropdown selection).
    first_template_value = initial_template_choices[0] if initial_template_choices else None

    # Pre-compute initial state for the first template so we don't need app.load().
    _init_tpl = _find_template_by_title(first_template_value) if first_template_value else None
    _init_desc = build_template_description_html(_init_tpl["description"], []) if _init_tpl else ""
    _init_inputs = _init_tpl.get("inputs", []) if _init_tpl else []

    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    )

    with gr.Blocks(title="PromptAnalyzer") as app:

        prompts_state = gr.State(saved_prompts)

        # ── Sidebar: user-saved prompts ──
        with gr.Sidebar(label="My Saved Prompts"):
            gr.Markdown("### My Prompts")
            prompt_selector = gr.Dropdown(
                choices=_prompt_choices(saved_prompts),
                label="Select a saved prompt",
                interactive=True,
            )
            load_btn = gr.Button("Load Selected", variant="secondary", size="sm")
            delete_btn = gr.Button("Delete Selected", variant="stop", size="sm")
            sidebar_status = gr.Markdown("")

        # ── Header ──
        gr.HTML(HEADER_HTML)

        # ── Metric definitions ──
        with gr.Accordion("What do the metrics mean?  (click to expand)", open=False):
            gr.HTML(build_metric_cards_html())

        # ── Main tabs ──
        with gr.Tabs():

            # ═══════════════════════════════════════════════════════════════
            # TAB: Cursor Prompts (guided mode — user fills context fields,
            #       assembled prompt shown read-only for copy to Cursor)
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Cursor Prompts", id="tab-template"):
                gr.Markdown(
                    "Select a template, fill in the context fields, and click **Generate Prompt**. "
                    "The assembled prompt appears below — ready to copy into Cursor."
                )

                with gr.Row():
                    tpl_category_filter = gr.Dropdown(
                        choices=["Cursor Workflow", "Analysis"],
                        value="Cursor Workflow",
                        label="Filter by Category",
                        scale=1,
                        interactive=True,
                    )
                    tpl_dropdown = gr.Dropdown(
                        choices=initial_template_choices,
                        value=first_template_value,
                        label="Select a Template",
                        scale=2,
                        interactive=True,
                    )

                tpl_description = gr.HTML(value=_init_desc)

                # Input fields pre-populated from the default template.
                _i0 = _init_inputs[0] if len(_init_inputs) > 0 and isinstance(_init_inputs[0], dict) else None
                _i1 = _init_inputs[1] if len(_init_inputs) > 1 and isinstance(_init_inputs[1], dict) else None
                _i2 = _init_inputs[2] if len(_init_inputs) > 2 and isinstance(_init_inputs[2], dict) else None

                tpl_input_0 = gr.Textbox(
                    label=_i0["label"] if _i0 else "Select a template above, then type here",
                    placeholder=_i0["hint"] if _i0 else "...",
                    lines=_i0.get("lines", 4) if _i0 else 4,
                    interactive=True,
                    visible=True,
                )
                tpl_input_1 = gr.Textbox(
                    label=_i1["label"] if _i1 else "",
                    placeholder=_i1["hint"] if _i1 else "",
                    lines=_i1.get("lines", 2) if _i1 else 2,
                    interactive=True,
                    visible=bool(_i1),
                )
                tpl_input_2 = gr.Textbox(
                    label=_i2["label"] if _i2 else "",
                    placeholder=_i2["hint"] if _i2 else "",
                    lines=_i2.get("lines", 2) if _i2 else 2,
                    interactive=True,
                    visible=bool(_i2),
                )

                tpl_inputs = [tpl_input_0, tpl_input_1, tpl_input_2]

                with gr.Row():
                    tpl_generate_btn = gr.Button(
                        "Generate Prompt", variant="primary",
                    )
                    tpl_evaluate_btn = gr.Button("Evaluate Prompt", variant="secondary")
                    tpl_refine_btn = gr.Button("Refine Prompt", variant="secondary")

                # Read-only assembled prompt for copying into Cursor
                tpl_assembled = gr.Textbox(
                    label="Your Cursor Prompt (read-only — copy this into Cursor)",
                    value="",
                    lines=12,
                    interactive=False,
                    elem_id="tpl-assembled-prompt",
                )
                tpl_pricing_btn = gr.Button(
                    "💰 Calculate Pricing",
                    variant="secondary",
                    size="sm",
                )
                tpl_copy_btn = gr.Button(
                    "📋 Copy Prompt to Clipboard",
                    variant="secondary",
                    size="sm",
                    elem_id="tpl-copy-btn",
                )

                # Provider / model hidden by default — only needed for
                # Evaluate and Refine, not for Generate + Copy workflow.
                with gr.Accordion("Evaluation Settings (provider & model)", open=False):
                    with gr.Row():
                        tpl_provider = gr.Radio(
                            choices=["OpenAI", "Anthropic", "Google"],
                            value="OpenAI",
                            label="Provider",
                        )
                        tpl_model = gr.Dropdown(
                            choices=OPENAI_MODELS,
                            value=OPENAI_MODELS[0],
                            label="Model",
                        )

                tpl_results_html = gr.HTML(
                    value="",
                    elem_id="tpl-results-panel",
                )

                with gr.Accordion("AI Prompt Refinement", open=False):
                    tpl_refinement_html = gr.HTML(
                        value=EMPTY_REFINEMENT_HTML,
                        elem_id="tpl-refinement-panel",
                    )

            # ═══════════════════════════════════════════════════════════════
            # TAB: Write New Prompt (full editor mode)
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Write New Prompt", id="tab-new-prompt"):
                gr.Markdown(
                    "Describe your goal — the **PROMPT** or **CROFT** framework is "
                    "auto-detected from your input. Click **Build Structured Prompt** to "
                    "generate a well-formed prompt, then evaluate or refine it."
                )

                # ── Prompt Builder (top section) ──────────────────────────
                with gr.Group(elem_classes=["prompt-builder-section"]):
                    gr.HTML(
                        '<div class="section-title">'
                        "🧠 Prompt Builder (AI Fluency) — 4D Principles (Delegation · Description · Discernment · Diligence)"
                        "</div>"
                    )
                    new_idea = gr.Textbox(
                        label="What do you want to accomplish?",
                        placeholder=(
                            "e.g. 'Write a Python function that validates email addresses' "
                            "or 'Explain the difference between REST and GraphQL APIs'"
                        ),
                        lines=3,
                        info=(
                            "Describe your intent in plain language. "
                            "The framework is selected automatically — no LLM call needed."
                        ),
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
                            "✨ Build Structured Prompt",
                            variant="primary",
                            scale=0,
                        )

                # ── Full editor + evaluation ──────────────────────────────
                with gr.Row():
                    with gr.Column(scale=1):
                        new_title = gr.Textbox(
                            label="Prompt Title",
                            placeholder="My awesome prompt…",
                            max_lines=1,
                        )
                        new_text = gr.Textbox(
                            label="Prompt Text",
                            placeholder=(
                                "Your structured prompt will appear here after clicking "
                                "'Build Structured Prompt', or write directly from scratch…"
                            ),
                            lines=12,
                        )
                        with gr.Row():
                            new_category = gr.Dropdown(
                                choices=CATEGORIES,
                                value="cursor prompt",
                                label="Category",
                            )
                            new_provider = gr.Radio(
                                choices=["OpenAI", "Anthropic", "Google"],
                                value="OpenAI",
                                label="Provider",
                            )
                        new_model = gr.Dropdown(
                            choices=OPENAI_MODELS,
                            value=OPENAI_MODELS[0],
                            label="Model",
                        )
                        with gr.Row():
                            new_evaluate_btn = gr.Button("Evaluate Prompt", variant="primary")
                            new_refine_btn = gr.Button("Refine Prompt", variant="secondary")
                            new_save_btn = gr.Button("Save to My Prompts", variant="secondary")
                        new_status = gr.Markdown("")

                    with gr.Column(scale=1):
                        gr.Markdown("### Evaluation Results")
                        new_results_html = gr.HTML(
                            value=EMPTY_RESULTS_HTML,
                            elem_id="new-results-panel",
                        )

                with gr.Accordion("AI Prompt Refinement", open=True):
                    new_refinement_html = gr.HTML(
                        value=EMPTY_REFINEMENT_HTML,
                        elem_id="new-refinement-panel",
                    )

                new_history = gr.Textbox(
                    label="Evaluation History (for loaded prompt)",
                    lines=6,
                    interactive=False,
                )

            # ═══════════════════════════════════════════════════════════════
            # TAB: Token Pricing
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Token Pricing", id="tab-pricing"):
                gr.Markdown(
                    "Enter a prompt to see how many tokens it uses and what it "
                    "costs across all your configured providers. Only providers "
                    "with saved API keys are shown."
                )
                pricing_prompt_input = gr.Textbox(
                    label="Prompt",
                    placeholder="Paste or type a prompt here…",
                    lines=6,
                )
                pricing_calc_btn = gr.Button(
                    "💰 Calculate Pricing", variant="primary",
                )
                pricing_results_html = gr.HTML(
                    value=EMPTY_PRICING_HTML,
                    elem_id="pricing-results-panel",
                )

            # ═══════════════════════════════════════════════════════════════
            # TAB: Settings
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("Settings", id="tab-settings"):
                gr.Markdown("### API Key Configuration")
                gr.Markdown(
                    "Keys are validated, saved to `.env`, and loaded automatically "
                    "on app startup. They are **only** used when running evaluations."
                )
                openai_key_input = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-…",
                    type="password",
                    value=openai_key_init,
                )
                anthropic_key_input = gr.Textbox(
                    label="Anthropic API Key",
                    placeholder="sk-ant-…",
                    type="password",
                    value=anthropic_key_init,
                )
                google_key_input = gr.Textbox(
                    label="Google API Key",
                    placeholder="AIza…",
                    type="password",
                    value=google_key_init,
                )
                save_keys_btn = gr.Button("Save API Keys", variant="primary")
                keys_status = gr.Markdown("")

        # ══════════════════════════════════════════════════════════════════
        # Event wiring
        # ══════════════════════════════════════════════════════════════════

        # -- Settings --
        save_keys_btn.click(
            fn=_persist_keys,
            inputs=[openai_key_input, anthropic_key_input, google_key_input],
            outputs=[keys_status],
        )

        # -- Sidebar: user prompt CRUD --
        new_save_btn.click(
            fn=save_prompt,
            inputs=[new_title, new_text, new_category, prompts_state],
            outputs=[prompts_state, prompt_selector, new_status],
        )
        delete_btn.click(
            fn=delete_prompt,
            inputs=[prompt_selector, prompts_state],
            outputs=[prompts_state, prompt_selector, sidebar_status],
        )
        load_btn.click(
            fn=load_selected_prompt,
            inputs=[prompt_selector, prompts_state],
            outputs=[new_title, new_text, new_category, new_history],
        )

        # -- Template tab: template selection + dynamic inputs --
        tpl_category_filter.change(
            fn=_filter_templates,
            inputs=[tpl_category_filter],
            outputs=[tpl_dropdown],
        )
        tpl_dropdown.change(
            fn=_on_template_selected,
            inputs=[tpl_dropdown],
            outputs=[tpl_description, tpl_assembled] + tpl_inputs,
        )
        tpl_provider.change(
            fn=_update_model_choices,
            inputs=[tpl_provider],
            outputs=[tpl_model],
        )

        # -- Template tab: generate assembled prompt (read-only for copy) --
        tpl_generate_btn.click(
            fn=_generate_assembled_prompt,
            inputs=[tpl_dropdown] + tpl_inputs,
            outputs=[tpl_assembled],
        )

        # -- Template tab: copy assembled prompt to clipboard via JS --
        # Uses execCommand fallback for non-HTTPS (0.0.0.0) origins where
        # navigator.clipboard is unavailable.
        tpl_copy_btn.click(
            fn=None,
            inputs=[tpl_assembled],
            outputs=[],
            js="""(x) => {
              var t = '';
              if (typeof x === 'string') t = x;
              if (!t) {
                var el = document.querySelector('#tpl-assembled-prompt textarea');
                if (el) t = el.value || '';
              }
              if (!t) return [];
              var ta = document.createElement('textarea');
              ta.value = t;
              ta.style.position = 'fixed';
              ta.style.left = '-9999px';
              document.body.appendChild(ta);
              ta.select();
              try { document.execCommand('copy'); } catch(e) {}
              document.body.removeChild(ta);
              var btn = document.querySelector('#tpl-copy-btn button') || document.querySelector('#tpl-copy-btn');
              if (btn) {
                var orig = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(function(){ btn.textContent = orig; }, 2000);
              }
              return [];
            }""",
        )

        # -- Template tab: evaluate + refine --
        tpl_evaluate_btn.click(
            fn=_assemble_and_evaluate,
            inputs=[tpl_dropdown] + tpl_inputs + [tpl_provider, tpl_model, prompts_state],
            outputs=[tpl_results_html, prompts_state],
        )
        tpl_refine_btn.click(
            fn=_assemble_and_refine,
            inputs=[tpl_dropdown] + tpl_inputs + [tpl_provider, tpl_model],
            outputs=[tpl_refinement_html],
        )

        # -- New prompt tab: framework auto-detection (no LLM) --
        def _detect_and_update(idea: str) -> tuple[str, str]:
            """Return (badge_html, framework_value) based on typed idea."""
            fw, reason, confidence = detect_framework(idea)
            badge = render_detection_badge(fw, reason, confidence)
            return badge, fw

        new_idea.change(
            fn=_detect_and_update,
            inputs=[new_idea],
            outputs=[new_framework_badge, new_framework_radio],
        )

        # -- New prompt tab: build structured prompt (no LLM) --
        def _build_structured_prompt(idea: str, framework: str) -> str:
            """Generate a PROMPT or CROFT structured prompt from the user's idea."""
            return build_prompt(idea, framework)  # type: ignore[arg-type]

        new_build_btn.click(
            fn=_build_structured_prompt,
            inputs=[new_idea, new_framework_radio],
            outputs=[new_text],
        )

        # -- New prompt tab: provider/model --
        new_provider.change(
            fn=_update_model_choices,
            inputs=[new_provider],
            outputs=[new_model],
        )

        # -- New prompt tab: evaluate + refine --
        new_evaluate_btn.click(
            fn=evaluate_new_prompt,
            inputs=[new_title, new_text, new_category, new_provider, new_model, prompts_state],
            outputs=[new_results_html, prompts_state],
        )
        new_refine_btn.click(
            fn=handle_refine_new,
            inputs=[new_text, new_provider, new_model],
            outputs=[new_refinement_html],
        )

        # -- Token Pricing tab --
        pricing_calc_btn.click(
            fn=_handle_calculate_pricing,
            inputs=[pricing_prompt_input],
            outputs=[pricing_results_html],
        )

        # -- Template tab: Calculate Pricing button --
        tpl_pricing_btn.click(
            fn=_handle_calculate_pricing,
            inputs=[tpl_assembled],
            outputs=[tpl_results_html],
        )

    app._theme = theme
    app._css = APP_CSS
    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Build and launch the Gradio server."""
    app = build_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=app._theme,
        css=app._css,
        ssr_mode=False,
    )


if __name__ == "__main__":
    main()
