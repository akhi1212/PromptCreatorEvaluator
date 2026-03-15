"""
styles.py — CSS and HTML rendering for PromptAnalyzer.

Keeps all visual presentation out of app.py so the main file
stays focused on logic and wiring.
"""

from __future__ import annotations

from typing import Any

from evaluator import METRIC_DEFS

# ---------------------------------------------------------------------------
# Quick lookup: metric name -> its definition dict
# ---------------------------------------------------------------------------
_METRIC_LOOKUP: dict[str, dict[str, Any]] = {m["name"]: m for m in METRIC_DEFS}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

APP_CSS = """
/* ── Base ── */
.gradio-container {
    background: linear-gradient(160deg, #f8f7ff 0%, #f0f4ff 40%, #fdf2f8 100%) !important;
}
.dark .gradio-container {
    background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 40%, #1a1a2e 100%) !important;
}

/* ── Header ── */
#app-header { text-align: center; padding: 30px 20px 12px; }
#app-header h1 {
    font-size: 2.6rem !important; font-weight: 900 !important; margin: 0 !important;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
#app-header .subtitle {
    color: #475569 !important; font-size: 1.05rem; margin-top: 8px; line-height: 1.6;
}
#app-header .subtitle strong { color: #7c3aed; }
.dark #app-header .subtitle { color: #cbd5e1 !important; }

/* ── Metric definition cards ── */
.metric-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px; padding: 10px 0;
}
.metric-card {
    border-radius: 14px; padding: 20px 22px;
    background: #ffffff; border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.dark .metric-card { background: #1e293b; border-color: #334155; }
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(124,58,237,0.12);
}
.metric-card .mc-icon { font-size: 30px; margin-bottom: 8px; }
.metric-card .mc-name { font-weight: 800; font-size: 17px; margin-bottom: 4px; }
.metric-card .mc-question { font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.metric-card .mc-desc { font-size: 13px; color: #64748b; line-height: 1.65; }
.dark .metric-card .mc-desc { color: #94a3b8; }

/* ── Score threshold legend ── */
.threshold-legend {
    display: flex; gap: 24px; justify-content: center;
    padding: 16px 0 6px; flex-wrap: wrap;
}
.threshold-legend .tl-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; color: #475569;
}
.dark .threshold-legend .tl-item { color: #94a3b8; }
.threshold-legend .tl-dot {
    width: 12px; height: 12px; border-radius: 50%; display: inline-block;
}

/* ── Results panel ── */
#results-panel { min-height: 200px; }

/* ── Buttons ── */
button.primary {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    border: none !important; font-weight: 700 !important;
}
button.primary:hover {
    background: linear-gradient(135deg, #6d28d9, #5b21b6) !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.35) !important;
}

/* ── Sidebar ── */
.sidebar { border-right: 2px solid #e2e8f0 !important; }
.dark .sidebar { border-right: 2px solid #334155 !important; }

/* ── Prompt Builder section ── */
.prompt-builder-section {
    border: 2px solid #c4b5fd;
    border-radius: 14px;
    padding: 18px 20px 14px;
    background: linear-gradient(135deg, #faf5ff, #eff6ff);
    margin-bottom: 14px;
}
.dark .prompt-builder-section {
    background: linear-gradient(135deg, #1e1b4b22, #1e3a5f22);
    border-color: #4c1d95;
}
.prompt-builder-section .section-title {
    font-weight: 800; font-size: 14px; color: #7c3aed;
    margin-bottom: 4px; display: flex; align-items: center; gap: 6px;
}
.dark .prompt-builder-section .section-title { color: #a78bfa; }

/* ── Framework radio buttons ── */
.framework-radio label { font-weight: 700 !important; }

/* ── Copy to clipboard button ── */
#tpl-copy-btn {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: #fff !important; border: none !important;
    font-weight: 700 !important; font-size: 14px !important;
}
#tpl-copy-btn:hover {
    background: linear-gradient(135deg, #15803d, #166534) !important;
    box-shadow: 0 4px 12px rgba(22,163,74,0.35) !important;
}
"""

# ---------------------------------------------------------------------------
# Static HTML fragments
# ---------------------------------------------------------------------------

HEADER_HTML = (
    '<div id="app-header">'
    "<h1>PromptAnalyzer</h1>"
    '<p class="subtitle">Evaluate your LLM prompts on '
    "<strong>Clarity</strong>, <strong>Specificity</strong>, "
    "<strong>Completeness</strong>, <strong>Coherence</strong>, and "
    "<strong>Safety</strong> using DeepEval's G-Eval metrics.</p>"
    "</div>"
)

EMPTY_RESULTS_HTML = (
    '<div style="text-align:center; padding:48px 24px;'
    " border:2px dashed #c4b5fd; border-radius:16px;"
    ' background: linear-gradient(135deg, #ede9fe, #dbeafe);">'
    '<div style="font-size:42px; margin-bottom:12px;">📊</div>'
    '<div style="font-size:16px; font-weight:700; color:#4c1d95;">'
    "Run an evaluation to see results here</div>"
    '<div style="font-size:13px; margin-top:8px; color:#6b7280;">'
    "Enter a prompt on the left, choose a provider, and click "
    '<strong style="color:#7c3aed;">Evaluate Prompt</strong></div>'
    "</div>"
)


def build_metric_cards_html() -> str:
    """Build the HTML grid shown inside the 'What do the metrics mean?' accordion.

    Returns:
        Complete HTML string with one card per metric plus a score-threshold legend.
    """
    bg_tints = {
        "#6366f1": "#eef2ff",
        "#f59e0b": "#fffbeb",
        "#10b981": "#ecfdf5",
        "#3b82f6": "#eff6ff",
        "#ef4444": "#fef2f2",
    }

    html = '<div class="metric-grid">'
    for mdef in METRIC_DEFS:
        c = mdef["color"]
        bg = bg_tints.get(c, "#f8fafc")
        html += (
            f'<div class="metric-card" style="border-left:5px solid {c}; background:{bg};">'
            f'  <div class="mc-icon">{mdef["icon"]}</div>'
            f'  <div class="mc-name" style="color:{c};">{mdef["name"]}</div>'
            f'  <div class="mc-question" style="color:#334155;">{mdef["short_def"]}</div>'
            f'  <div class="mc-desc">{mdef["description"]}</div>'
            f"</div>"
        )
    html += "</div>"

    html += (
        '<div class="threshold-legend">'
        '  <div class="tl-item"><span class="tl-dot" style="background:#16a34a;"></span> >= 80% Strong</div>'
        '  <div class="tl-item"><span class="tl-dot" style="background:#d97706;"></span> 50–79% Needs work</div>'
        '  <div class="tl-item"><span class="tl-dot" style="background:#dc2626;"></span> < 50% Problematic</div>'
        "</div>"
    )
    return html


# ---------------------------------------------------------------------------
# Dynamic HTML — evaluation results
# ---------------------------------------------------------------------------

def _score_color(score: float) -> str:
    """Map a 0-1 score to a traffic-light hex color."""
    if score >= 0.8:
        return "#16a34a"
    if score >= 0.5:
        return "#d97706"
    return "#dc2626"


def _score_bg(score: float) -> str:
    """Map a 0-1 score to a light tint background for the reason box."""
    if score >= 0.8:
        return "#f0fdf4"
    if score >= 0.5:
        return "#fffbeb"
    return "#fef2f2"


def build_results_html(
    scores: dict[str, dict], provider: str, elapsed: float, model: str = ""
) -> str:
    """Render evaluation scores as a styled HTML panel.

    Args:
        scores:   Dict mapping metric name -> {score, reason, passed}.
        provider: "OpenAI" or "Anthropic".
        elapsed:  Wall-clock seconds the evaluation took.
        model:    Model identifier used for evaluation.

    Returns:
        Complete HTML string ready to drop into a gr.HTML component.
    """
    avg = sum(s["score"] for s in scores.values()) / max(len(scores), 1)
    avg_color = _score_color(avg)
    avg_pct = int(avg * 100)

    model_label = f" / {model}" if model else ""
    ring = f"background: conic-gradient({avg_color} {avg_pct}%, #e2e8f0 {avg_pct}%);"

    html = f"""
    <div style="font-family:'Inter',system-ui,sans-serif;">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:22px;
                  padding:22px 26px;border-radius:16px;
                  background:linear-gradient(135deg,#ede9fe,#dbeafe,#fce7f3);
                  border:1px solid #c4b5fd;box-shadow:0 4px 20px rgba(124,58,237,0.1);">
        <div style="width:84px;height:84px;border-radius:50%;{ring}
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;
                    box-shadow:0 0 0 4px rgba(255,255,255,0.7);">
          <div style="width:62px;height:62px;border-radius:50%;background:#fff;
                      display:flex;align-items:center;justify-content:center;
                      font-size:22px;font-weight:900;color:{avg_color};">
            {avg_pct}%
          </div>
        </div>
        <div>
          <div style="font-size:21px;font-weight:800;color:#1e1b4b;">Overall Prompt Score</div>
          <div style="color:#6b7280;font-size:13px;margin-top:5px;">
            Provider: <strong style="color:#7c3aed;">{provider}{model_label}</strong> &middot; {elapsed:.1f}s
          </div>
        </div>
      </div>
    """

    for name, info in scores.items():
        sc = info["score"]
        sc_color = _score_color(sc)
        sc_bg = _score_bg(sc)
        bar_w = max(int(sc * 100), 2)
        icon = "✓" if info["passed"] else "✗"

        mdef = _METRIC_LOOKUP.get(name, {})
        m_icon = mdef.get("icon", "")
        accent = mdef.get("color", "#7c3aed")
        short = mdef.get("short_def", "")
        desc = mdef.get("description", "")

        badge_bg = "#dcfce7" if info["passed"] else "#fee2e2"
        badge_fg = "#15803d" if info["passed"] else "#b91c1c"

        html += f"""
      <div style="margin-bottom:14px;padding:18px 20px;border-radius:14px;
                  background:#fff;border:1px solid #e2e8f0;border-left:5px solid {accent};
                  box-shadow:0 2px 8px rgba(0,0,0,0.04);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-weight:800;font-size:16px;color:{accent};">{m_icon} {name}</span>
          <span style="color:{badge_fg};font-weight:800;font-size:14px;
                       background:{badge_bg};padding:4px 14px;border-radius:20px;">
            {icon} {sc:.0%}
          </span>
        </div>
        <div style="font-size:12.5px;color:#64748b;margin-top:4px;font-style:italic;">{short}</div>
        <div style="background:#f1f5f9;border-radius:6px;height:10px;margin:12px 0;overflow:hidden;">
          <div style="background:linear-gradient(90deg,{accent},{sc_color});
                      width:{bar_w}%;height:100%;border-radius:6px;"></div>
        </div>
        <div style="font-size:13.5px;color:#334155;line-height:1.6;margin-bottom:8px;
                    padding:10px 14px;background:{sc_bg};border-radius:8px;
                    border-left:3px solid {sc_color};">
          {info['reason']}
        </div>
        <details style="cursor:pointer;margin-top:6px;">
          <summary style="font-size:12.5px;font-weight:700;color:{accent};">
            Learn more about this metric
          </summary>
          <p style="margin:8px 0 0;font-size:12.5px;color:#64748b;line-height:1.65;
                    padding:8px 12px;background:#f8fafc;border-radius:8px;">
            {desc}
          </p>
        </details>
      </div>
        """

    html += "</div>"
    return html


# ---------------------------------------------------------------------------
# Refined prompt panel
# ---------------------------------------------------------------------------

EMPTY_REFINEMENT_HTML = (
    '<div style="text-align:center; padding:36px 24px;'
    " border:2px dashed #a5b4fc; border-radius:16px;"
    ' background: linear-gradient(135deg, #eef2ff, #ede9fe);">'
    '<div style="font-size:36px; margin-bottom:10px;">✨</div>'
    '<div style="font-size:15px; font-weight:700; color:#4338ca;">'
    "AI-refined prompt will appear here</div>"
    '<div style="font-size:13px; margin-top:6px; color:#6b7280;">'
    "After evaluation, click "
    '<strong style="color:#7c3aed;">Refine Prompt</strong> '
    "to get an improved version with suggestions</div>"
    "</div>"
)


def build_refinement_html(refinement_text: str) -> str:
    """Render the LLM's refinement response as styled HTML.

    The LLM returns markdown with three sections:
      - ### Issues Found
      - ### Refined Prompt
      - ### What Changed

    This function parses those sections and renders them as
    color-coded cards.

    Args:
        refinement_text: Raw markdown from the LLM.

    Returns:
        Styled HTML string.
    """
    import re

    sections = {
        "issues": "",
        "refined": "",
        "changes": "",
    }

    current = None
    for line in refinement_text.split("\n"):
        lower = line.strip().lower()
        if "issues found" in lower:
            current = "issues"
            continue
        elif "refined prompt" in lower:
            current = "refined"
            continue
        elif "what changed" in lower:
            current = "changes"
            continue
        if current:
            sections[current] += line + "\n"

    def _md_bullets(text: str) -> str:
        """Convert markdown bullet lines to HTML list items."""
        items = []
        for ln in text.strip().split("\n"):
            ln = ln.strip()
            if ln.startswith("- ") or ln.startswith("* "):
                ln = ln[2:]
            if ln:
                items.append(f"<li>{_escape(ln)}</li>")
        return "<ul style='margin:6px 0;padding-left:20px;'>" + "".join(items) + "</ul>" if items else ""

    def _escape(text: str) -> str:
        """Basic HTML-escape for user-generated content."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    refined_text = sections["refined"].strip()
    refined_escaped = _escape(refined_text)
    refined_display = refined_escaped.replace("\n", "<br>") if refined_escaped else "<em>No refined prompt generated.</em>"

    html = '<div style="font-family:\'Inter\',system-ui,sans-serif;">'

    if sections["issues"].strip():
        html += f"""
      <div style="margin-bottom:14px;padding:16px 20px;border-radius:12px;
                  background:#fef2f2;border:1px solid #fecaca;border-left:5px solid #ef4444;">
        <div style="font-weight:800;font-size:15px;color:#dc2626;margin-bottom:8px;">
          🔴 Issues Found
        </div>
        <div style="font-size:13.5px;color:#7f1d1d;line-height:1.7;">
          {_md_bullets(sections["issues"])}
        </div>
      </div>
        """

    copy_id = f"refined-copy-{id(refined_text) % 100000}"
    html += f"""
      <div style="margin-bottom:14px;padding:18px 20px;border-radius:12px;
                  background:#f0fdf4;border:1px solid #bbf7d0;border-left:5px solid #16a34a;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-weight:800;font-size:15px;color:#16a34a;">
            ✅ Refined Prompt
          </span>
          <button onclick="
            var el = document.getElementById('{copy_id}');
            var t = el ? (el.innerText || el.textContent || '').trim() : '';
            if (!t) return;
            var ta = document.createElement('textarea');
            ta.value = t;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            try {{ document.execCommand('copy'); }} catch(e) {{}}
            document.body.removeChild(ta);
            var btn = event.target;
            btn.textContent = '✓ Copied!';
            setTimeout(function(){{ btn.textContent = '📋 Copy'; }}, 2000);
          " style="background:#16a34a;color:#fff;border:none;border-radius:8px;
                   padding:6px 16px;font-size:13px;font-weight:700;cursor:pointer;">
            📋 Copy
          </button>
        </div>
        <div id="{copy_id}" style="font-size:14px;color:#14532d;line-height:1.7;
                    padding:12px 16px;background:#ffffff;border-radius:8px;
                    border:1px solid #dcfce7;white-space:pre-wrap;">
          {refined_display}
        </div>
      </div>
    """

    if sections["changes"].strip():
        html += f"""
      <div style="margin-bottom:8px;padding:16px 20px;border-radius:12px;
                  background:#eff6ff;border:1px solid #bfdbfe;border-left:5px solid #3b82f6;">
        <div style="font-weight:800;font-size:15px;color:#2563eb;margin-bottom:8px;">
          🔄 What Changed
        </div>
        <div style="font-size:13.5px;color:#1e3a5f;line-height:1.7;">
          {_md_bullets(sections["changes"])}
        </div>
      </div>
        """

    html += "</div>"
    return html


# ---------------------------------------------------------------------------
# Template description preview
# ---------------------------------------------------------------------------


def build_template_description_html(description: str, placeholders: list[str]) -> str:
    """Render a template's description and placeholder list as styled HTML.

    Shown below the template dropdown when a template is selected.

    Args:
        description:  One-liner describing what the template does.
        placeholders: List of placeholder names the user needs to fill in.

    Returns:
        Styled HTML string.
    """
    ph_html = ""
    if placeholders:
        tags = " ".join(
            f'<span style="display:inline-block;background:#ede9fe;color:#6d28d9;'
            f'font-size:12px;font-weight:600;padding:2px 10px;border-radius:12px;'
            f'margin:2px 4px 2px 0;">{{{{' + p + '}}}}</span>'
            for p in placeholders
        )
        ph_html = (
            f'<div style="margin-top:8px;">'
            f'<span style="font-size:12px;font-weight:700;color:#475569;">Placeholders to fill in: </span>'
            f"{tags}</div>"
        )

    return (
        f'<div style="padding:12px 16px;border-radius:10px;background:#f8fafc;'
        f'border:1px solid #e2e8f0;margin-top:8px;">'
        f'<div style="font-size:14px;color:#334155;line-height:1.6;">{description}</div>'
        f"{ph_html}"
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Token pricing table
# ---------------------------------------------------------------------------

EMPTY_PRICING_HTML = (
    '<div style="text-align:center; padding:48px 24px;'
    " border:2px dashed #a5b4fc; border-radius:16px;"
    ' background: linear-gradient(135deg, #eef2ff, #ede9fe);">'
    '<div style="font-size:42px; margin-bottom:12px;">💰</div>'
    '<div style="font-size:16px; font-weight:700; color:#4338ca;">'
    "Enter a prompt and click Calculate Pricing</div>"
    '<div style="font-size:13px; margin-top:8px; color:#6b7280;">'
    "Token counts and costs will appear here for all configured providers</div>"
    "</div>"
)

NO_KEYS_PRICING_HTML = (
    '<div style="text-align:center; padding:36px 24px;'
    " border:2px dashed #fca5a5; border-radius:16px;"
    ' background: linear-gradient(135deg, #fef2f2, #fff1f2);">'
    '<div style="font-size:36px; margin-bottom:10px;">🔑</div>'
    '<div style="font-size:15px; font-weight:700; color:#dc2626;">'
    "No API keys configured</div>"
    '<div style="font-size:13px; margin-top:6px; color:#6b7280;">'
    'Go to the <strong style="color:#7c3aed;">Settings</strong> tab to add '
    "your OpenAI, Anthropic, or Google API keys first.</div>"
    "</div>"
)


def build_pricing_table_html(results: list[dict]) -> str:
    """Render token pricing results as a styled HTML table.

    Args:
        results: List of dicts from calculate_token_pricing(), each with
                 provider, model, tokens, input_cost, output_cost, and
                 optional error key.

    Returns:
        Styled HTML string with a comparison table.
    """
    if not results:
        return NO_KEYS_PRICING_HTML

    # Provider accent colors — high-contrast, industry-standard palette
    provider_colors = {
        "OpenAI": ("#059669", "#ecfdf5", "#065f46"),     # emerald
        "Anthropic": ("#d97706", "#fffbeb", "#92400e"),  # amber
        "Google": ("#2563eb", "#eff6ff", "#1e40af"),     # blue
    }

    html = '<div style="font-family:\'Inter\',\'Segoe UI\',system-ui,sans-serif;">'

    # Summary header
    total_models = len(results)
    providers = sorted(set(r["provider"] for r in results))
    provider_tags = " ".join(
        f'<span style="display:inline-block;background:{provider_colors.get(p, ("#7c3aed","#ede9fe","#5b21b6"))[1]};'
        f'color:{provider_colors.get(p, ("#7c3aed","#ede9fe","#5b21b6"))[2]};font-size:12px;font-weight:800;'
        f'padding:4px 14px;border-radius:20px;margin:0 3px;'
        f'border:1px solid {provider_colors.get(p, ("#7c3aed","#ede9fe","#5b21b6"))[0]}40;">{p}</span>'
        for p in providers
    )
    html += (
        '<div style="display:flex;align-items:center;gap:18px;margin-bottom:20px;'
        "padding:20px 24px;border-radius:16px;"
        'background:linear-gradient(135deg,#1e1b4b,#312e81);'
        'border:1px solid #4338ca;box-shadow:0 8px 32px rgba(30,27,75,0.25);">'
        '<div style="font-size:36px;">💰</div>'
        "<div>"
        '<div style="font-size:20px;font-weight:800;color:#ffffff;letter-spacing:-0.02em;">'
        f"Token Pricing Comparison</div>"
        '<div style="color:#c4b5fd;font-size:13px;margin-top:6px;">'
        f"{total_models} models across {provider_tags}</div>"
        "</div></div>"
    )

    # Table
    html += (
        '<div style="overflow-x:auto;border-radius:14px;border:1px solid #e2e8f0;'
        'box-shadow:0 4px 16px rgba(0,0,0,0.06);">'
        '<table style="width:100%;border-collapse:collapse;font-size:14px;'
        'font-family:\'Inter\',\'Segoe UI\',system-ui,sans-serif;">'
        "<thead>"
        '<tr style="background:linear-gradient(135deg,#7c3aed,#6d28d9);">'
        '<th style="padding:16px 18px;text-align:left;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Provider</th>'
        '<th style="padding:16px 18px;text-align:left;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Model</th>'
        '<th style="padding:16px 18px;text-align:right;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Input Tokens</th>'
        '<th style="padding:16px 18px;text-align:right;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Rate ($/M)</th>'
        '<th style="padding:16px 18px;text-align:right;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Input Cost</th>'
        '<th style="padding:16px 18px;text-align:right;font-weight:700;font-size:13px;'
        'color:#fff;letter-spacing:0.03em;text-transform:uppercase;">Output Cost (est.)</th>'
        "</tr></thead><tbody>"
    )

    from evaluator import MODEL_PRICING

    for i, r in enumerate(results):
        p_color, p_bg, p_dark = provider_colors.get(
            r["provider"], ("#7c3aed", "#f8fafc", "#5b21b6")
        )
        row_bg = "#ffffff" if i % 2 == 0 else "#fafafe"
        error = r.get("error", "")
        is_approx = r.get("source") == "approx"
        approx_badge = (' <span style="font-size:10px;color:#a78bfa;font-weight:600;'
                        'background:#ede9fe;padding:1px 6px;border-radius:6px;margin-left:4px;"'
                        ' title="Estimated via tiktoken (add API key for exact count)">≈ est.</span>'
                        if is_approx else "")

        pricing = MODEL_PRICING.get(r["model"], {})
        rate_str = f'${pricing.get("input", 0):.3f}'

        if error:
            html += (
                f'<tr style="background:{row_bg};">'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;">'
                f'<span style="color:{p_dark};font-weight:800;font-size:13px;">{r["provider"]}</span></td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;'
                f'color:#0f172a;font-weight:700;font-size:14px;">{r["model"]}</td>'
                f'<td colspan="4" style="padding:14px 18px;border-bottom:1px solid #f1f5f9;'
                f'color:#dc2626;font-size:13px;font-weight:600;">⚠ {error}</td>'
                "</tr>"
            )
        else:
            html += (
                f'<tr style="background:{row_bg};transition:all 0.15s ease;"'
                f' onmouseover="this.style.background=\'{p_bg}\';this.style.transform=\'scale(1.002)\'"'
                f' onmouseout="this.style.background=\'{row_bg}\';this.style.transform=\'scale(1)\'">'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;">'
                f'<span style="color:{p_dark};font-weight:800;font-size:13px;">{r["provider"]}</span></td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;'
                f'color:#0f172a;font-weight:700;font-size:14px;">'
                f'{r["model"]}</td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;text-align:right;'
                f'font-weight:800;font-size:15px;color:#1e1b4b;">{r["tokens"]:,}{approx_badge}</td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;text-align:right;'
                f'font-weight:600;font-size:13px;color:#64748b;">{rate_str}</td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;text-align:right;'
                f'color:#059669;font-weight:800;font-size:14px;">${r["input_cost"]:.6f}</td>'
                f'<td style="padding:14px 18px;border-bottom:1px solid #f1f5f9;text-align:right;'
                f'color:#d97706;font-weight:800;font-size:14px;">${r["output_cost"]:.6f}</td>'
                "</tr>"
            )

    html += "</tbody></table></div>"

    # Footnote with explanation
    html += (
        '<div style="margin-top:14px;padding:12px 18px;border-radius:10px;'
        'background:#f8fafc;border:1px solid #e2e8f0;">'
        '<div style="font-size:12px;color:#475569;line-height:1.7;">'
        '<strong style="color:#1e1b4b;">How costs are calculated:</strong> '
        '<strong>Input Tokens</strong> = number of tokens in your prompt. '
        '<strong>Input Cost</strong> = tokens × rate per million. '
        '<strong>Output Cost</strong> = estimated assuming output is same length as input '
        '(actual output length varies by response). '
        '<strong>Rate ($/M)</strong> = price per million input tokens. '
        '<br><span style="color:#7c3aed;font-weight:600;">≈ est.</span> = approximate '
        "token count via tiktoken — add API key in Settings for exact count."
        "</div></div>"
    )

    html += "</div>"
    return html
