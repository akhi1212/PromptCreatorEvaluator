"""
styles.py — CSS and HTML rendering for PromptAnalyzer.

Keeps all visual presentation out of app.py so the main file
stays focused on logic and wiring.
"""

from __future__ import annotations

from typing import Any

from evaluator import METRIC_DEFS, OUTPUT_METRIC_DEFS

# ---------------------------------------------------------------------------
# Quick lookup: metric name -> its definition dict
# ---------------------------------------------------------------------------
_METRIC_LOOKUP: dict[str, dict[str, Any]] = {m["name"]: m for m in METRIC_DEFS}
_OUTPUT_METRIC_LOOKUP: dict[str, dict[str, Any]] = {m["name"]: m for m in OUTPUT_METRIC_DEFS}

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


def build_output_metric_cards_html() -> str:
    """Build the HTML grid for output metric definitions."""
    html = '<div class="metric-grid">'
    for mdef in OUTPUT_METRIC_DEFS:
        c = mdef["color"]
        html += (
            f'<div class="metric-card" style="border-left:5px solid {c}; background:#f8fafc;">'
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


def _escape(text: str) -> str:
    """Basic HTML-escape for user-generated content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


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


def build_output_results_html(
    scores: dict[str, dict],
    provider: str,
    elapsed: float,
    model: str = "",
    actual_output_preview: str = "",
) -> str:
    """Render output evaluation scores as a styled HTML panel.

    Visually distinct from input metrics — uses a teal/blue gradient header
    so users can instantly tell the sections apart.

    Args:
        scores:                Dict mapping metric name -> {score, reason, passed}.
        provider:              "OpenAI", "Anthropic", or "Google".
        elapsed:               Wall-clock seconds the evaluation took.
        model:                 Model identifier used for evaluation.
        actual_output_preview: First 300 chars of the LLM response (shown as preview).
    """
    if not scores:
        return ""

    avg = sum(s["score"] for s in scores.values()) / max(len(scores), 1)
    avg_color = _score_color(avg)
    avg_pct = int(avg * 100)
    model_label = f" / {model}" if model else ""
    ring = f"background: conic-gradient({avg_color} {avg_pct}%, #e2e8f0 {avg_pct}%);"

    preview_block = ""
    if actual_output_preview:
        preview = _escape(actual_output_preview[:300])
        if len(actual_output_preview) > 300:
            preview += "…"
        preview_block = (
            f'<div style="margin-bottom:18px;padding:14px 18px;border-radius:12px;'
            f'background:#f0fdfa;border:1px solid #99f6e4;">'
            f'<div style="font-size:12px;font-weight:700;color:#0d9488;margin-bottom:6px;">'
            f'LLM RESPONSE PREVIEW</div>'
            f'<pre style="font-size:12px;color:#134e4a;white-space:pre-wrap;'
            f'word-break:break-word;margin:0;">{preview}</pre>'
            f'</div>'
        )

    html = f"""
    <div style="font-family:'Inter',system-ui,sans-serif;">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:22px;
                  padding:22px 26px;border-radius:16px;
                  background:linear-gradient(135deg,#ccfbf1,#cffafe,#e0f2fe);
                  border:1px solid #67e8f9;box-shadow:0 4px 20px rgba(6,182,212,0.1);">
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
          <div style="font-size:21px;font-weight:800;color:#164e63;">
            📤 Output Quality Score
          </div>
          <div style="color:#6b7280;font-size:13px;margin-top:5px;">
            Provider: <strong style="color:#0891b2;">{provider}{model_label}</strong>
            &middot; {elapsed:.1f}s
          </div>
        </div>
      </div>
      {preview_block}
    """

    for name, info in scores.items():
        sc = info["score"]
        sc_color = _score_color(sc)
        sc_bg = _score_bg(sc)
        bar_w = max(int(sc * 100), 2)
        icon = "✓" if info["passed"] else "✗"

        mdef = _OUTPUT_METRIC_LOOKUP.get(name, {})
        m_icon = mdef.get("icon", "")
        accent = mdef.get("color", "#06b6d4")
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
# Combined results panel (input + output in one view)
# ---------------------------------------------------------------------------


def build_combined_results_html(
    input_scores: dict[str, dict],
    output_scores: dict[str, dict],
    provider: str,
    input_elapsed: float,
    output_elapsed: float,
    model: str = "",
    response_preview: str = "",
) -> str:
    """Render input and output evaluation scores in a single unified panel.

    Shows an overall score ring, then input metrics section, then output
    metrics section with the LLM response preview.
    """
    all_scores = {**input_scores, **output_scores}
    if not all_scores:
        return ""

    total_elapsed = input_elapsed + output_elapsed
    avg = sum(s["score"] for s in all_scores.values()) / max(len(all_scores), 1)
    avg_color = _score_color(avg)
    avg_pct = int(avg * 100)
    model_label = f" / {model}" if model else ""
    ring = f"background: conic-gradient({avg_color} {avg_pct}%, #e2e8f0 {avg_pct}%);"

    html = f"""
    <div style="font-family:'Inter',system-ui,sans-serif;">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:22px;
                  padding:22px 26px;border-radius:16px;
                  background:linear-gradient(135deg,#ede9fe,#dbeafe,#ccfbf1);
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
          <div style="font-size:21px;font-weight:800;color:#1e1b4b;">Overall Score</div>
          <div style="color:#6b7280;font-size:13px;margin-top:5px;">
            Provider: <strong style="color:#7c3aed;">{provider}{model_label}</strong>
            &middot; {total_elapsed:.1f}s
            &middot; {len(input_scores)} input + {len(output_scores)} output metrics
          </div>
        </div>
      </div>
    """

    # ── Input metrics section ──
    if input_scores:
        input_avg = sum(s["score"] for s in input_scores.values()) / max(len(input_scores), 1)
        input_avg_pct = int(input_avg * 100)
        input_color = _score_color(input_avg)
        html += f"""
      <div style="display:flex;align-items:center;gap:10px;padding:12px 18px;margin-bottom:14px;
                  border-radius:10px;background:linear-gradient(135deg,#ede9fe,#dbeafe);
                  border:1px solid #c4b5fd;">
        <span style="font-size:18px;">📥</span>
        <span style="font-weight:800;font-size:14px;color:#4c1d95;">Input Quality</span>
        <span style="margin-left:auto;font-weight:800;font-size:14px;color:{input_color};">{input_avg_pct}%</span>
        <span style="font-size:11px;color:#6b7280;">{input_elapsed:.1f}s</span>
      </div>
        """
        for name, info in input_scores.items():
            html += _render_metric_card(name, info, _METRIC_LOOKUP)

    # ── Output metrics section ──
    if output_scores:
        output_avg = sum(s["score"] for s in output_scores.values()) / max(len(output_scores), 1)
        output_avg_pct = int(output_avg * 100)
        output_color = _score_color(output_avg)

        # Response preview
        preview_block = ""
        if response_preview:
            preview = _escape(response_preview[:400])
            if len(response_preview) > 400:
                preview += "…"
            preview_block = (
                f'<div style="margin-bottom:14px;padding:14px 18px;border-radius:12px;'
                f'background:#f0fdfa;border:1px solid #99f6e4;">'
                f'<div style="font-size:12px;font-weight:700;color:#0d9488;margin-bottom:6px;">'
                f'LLM RESPONSE PREVIEW</div>'
                f'<pre style="font-size:12px;color:#134e4a;white-space:pre-wrap;'
                f'word-break:break-word;margin:0;max-height:200px;overflow:auto;">{preview}</pre>'
                f'</div>'
            )

        html += f"""
      <div style="display:flex;align-items:center;gap:10px;padding:12px 18px;margin-bottom:14px;
                  margin-top:20px;border-radius:10px;
                  background:linear-gradient(135deg,#ccfbf1,#cffafe);
                  border:1px solid #67e8f9;">
        <span style="font-size:18px;">📤</span>
        <span style="font-weight:800;font-size:14px;color:#164e63;">Output Quality</span>
        <span style="margin-left:auto;font-weight:800;font-size:14px;color:{output_color};">{output_avg_pct}%</span>
        <span style="font-size:11px;color:#6b7280;">{output_elapsed:.1f}s</span>
      </div>
      {preview_block}
        """
        for name, info in output_scores.items():
            html += _render_metric_card(name, info, _OUTPUT_METRIC_LOOKUP)

    html += "</div>"
    return html


def _render_metric_card(
    name: str,
    info: dict[str, Any],
    lookup: dict[str, dict[str, Any]],
) -> str:
    """Render a single metric score card (used by both input and output sections)."""
    sc = info["score"]
    sc_color = _score_color(sc)
    sc_bg = _score_bg(sc)
    bar_w = max(int(sc * 100), 2)
    icon = "✓" if info["passed"] else "✗"

    mdef = lookup.get(name, {})
    m_icon = mdef.get("icon", "")
    accent = mdef.get("color", "#7c3aed")
    short = mdef.get("short_def", "")
    desc = mdef.get("description", "")

    badge_bg = "#dcfce7" if info["passed"] else "#fee2e2"
    badge_fg = "#15803d" if info["passed"] else "#b91c1c"

    return f"""
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


def build_refinement_html(
    refinement_text: str,
    model: str = "",
    provider: str = "",
) -> str:
    """Render the LLM's refinement response as styled HTML.

    The LLM returns markdown with three sections:
      - ### Issues Found
      - ### Refined Prompt
      - ### What Changed

    This function parses those sections and renders them as
    color-coded cards.

    Args:
        refinement_text: Raw markdown from the LLM.
        model:           Model used for refinement (shown as badge).
        provider:        Provider name (controls badge color).

    Returns:
        Styled HTML string.
    """
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

    refined_text = sections["refined"].strip()
    refined_escaped = _escape(refined_text)
    refined_display = refined_escaped.replace("\n", "<br>") if refined_escaped else "<em>No refined prompt generated.</em>"

    provider_colors = {
        "OpenAI": "#10a37f",
        "Anthropic": "#d97706",
        "Google": "#4285f4",
    }
    badge_color = provider_colors.get(provider, "#7c3aed")
    model_badge = ""
    if model and provider:
        model_badge = (
            f'<span style="background:{badge_color};color:#fff;padding:3px 10px;'
            f'border-radius:12px;font-size:11px;font-weight:700;margin-left:8px;">'
            f'{provider} · {model}</span>'
        )

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
            ✅ Refined Prompt {model_badge}
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


def build_skill_refinement_html(
    refinement_text: str,
    model: str = "",
    provider: str = "",
    original_tokens: int = 0,
    refined_tokens: int = 0,
    original_cost: float = 0.0,
    refined_cost: float = 0.0,
) -> str:
    """Render the LLM's skill/agent refinement response as styled HTML.

    Similar to build_refinement_html but with skill-specific labels,
    token-saving summary, and model badge.

    Args:
        refinement_text: Raw markdown from the LLM.
        model:           Model used (shown as badge).
        provider:        Provider name (controls badge color).
        original_tokens: Token count of the original skill.
        refined_tokens:  Token count after compression.
        original_cost:   Estimated total cost of the original.
        refined_cost:    Estimated total cost after compression.
    """
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
        elif "refined skill" in lower or "refined agent" in lower:
            current = "refined"
            continue
        elif "what changed" in lower:
            current = "changes"
            continue
        if current:
            sections[current] += line + "\n"

    def _md_bullets(text: str) -> str:
        items = []
        for ln in text.strip().split("\n"):
            ln = ln.strip()
            if ln.startswith("- ") or ln.startswith("* "):
                ln = ln[2:]
            if ln:
                items.append(f"<li>{_escape(ln)}</li>")
        return "<ul style='margin:6px 0;padding-left:20px;'>" + "".join(items) + "</ul>" if items else ""

    refined_text = sections["refined"].strip()
    refined_escaped = _escape(refined_text)
    refined_display = refined_escaped.replace("\n", "<br>") if refined_escaped else "<em>No refined skill generated.</em>"

    # Model badge
    provider_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706", "Google": "#4285f4"}
    badge_color = provider_colors.get(provider, "#7c3aed")
    model_badge = ""
    if model and provider:
        model_badge = (
            f'<span style="background:{badge_color};color:#fff;padding:3px 10px;'
            f'border-radius:12px;font-size:11px;font-weight:700;">'
            f'{provider} · {model}</span>'
        )

    html = '<div style="font-family:\'Inter\',system-ui,sans-serif;">'

    # Header badge
    html += f"""
      <div style="display:flex;align-items:center;gap:10px;padding:14px 20px;margin-bottom:16px;
                  border-radius:12px;background:linear-gradient(135deg,#faf5ff,#ede9fe);
                  border:2px solid #a78bfa;">
        <span style="font-size:24px;">🤖</span>
        <div style="flex:1;">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span style="font-size:15px;font-weight:800;color:#6d28d9;">
              Skill / Agent Refinement
            </span>
            {model_badge}
          </div>
          <div style="font-size:12px;color:#6b7280;margin-top:2px;">
            Refined for quality <strong>&amp;</strong> token efficiency — optimized to save tokens without losing intent
          </div>
        </div>
      </div>
    """

    # Token saving summary (only if we have data)
    saved_tokens = original_tokens - refined_tokens
    if original_tokens > 0 and saved_tokens > 0:
        pct = saved_tokens / original_tokens * 100
        saved_cost = original_cost - refined_cost
        html += f"""
      <div style="margin-bottom:16px;padding:16px 20px;border-radius:12px;
                  background:linear-gradient(135deg,#ecfdf5,#f0fdf4);
                  border:2px solid #86efac;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
          <span style="font-size:18px;">💰</span>
          <span style="font-size:14px;font-weight:800;color:#166534;">
            Token Savings
          </span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
          <div style="text-align:center;padding:8px;background:#fff;border-radius:8px;
                      border:1px solid #bbf7d0;">
            <div style="font-size:18px;font-weight:900;color:#6b7280;">{original_tokens:,}</div>
            <div style="font-size:10px;color:#64748b;font-weight:600;margin-top:2px;">ORIGINAL</div>
          </div>
          <div style="text-align:center;padding:8px;background:#fff;border-radius:8px;
                      border:1px solid #bbf7d0;">
            <div style="font-size:18px;font-weight:900;color:#059669;">{refined_tokens:,}</div>
            <div style="font-size:10px;color:#64748b;font-weight:600;margin-top:2px;">REFINED</div>
          </div>
          <div style="text-align:center;padding:8px;background:#fff;border-radius:8px;
                      border:1px solid #bbf7d0;">
            <div style="font-size:18px;font-weight:900;color:#059669;">▼ {saved_tokens:,} ({pct:.1f}%)</div>
            <div style="font-size:10px;color:#64748b;font-weight:600;margin-top:2px;">TOKENS SAVED</div>
          </div>
          <div style="text-align:center;padding:8px;background:#fff;border-radius:8px;
                      border:1px solid #bbf7d0;">
            <div style="font-size:18px;font-weight:900;color:#059669;">${saved_cost:.6f}</div>
            <div style="font-size:10px;color:#64748b;font-weight:600;margin-top:2px;">COST SAVED</div>
          </div>
        </div>
      </div>
        """

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

    copy_id = f"skill-copy-{id(refined_text) % 100000}"
    html += f"""
      <div style="margin-bottom:14px;padding:18px 20px;border-radius:12px;
                  background:#f5f3ff;border:1px solid #c4b5fd;border-left:5px solid #7c3aed;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-weight:800;font-size:15px;color:#7c3aed;">
            ✅ Refined Skill / Agent
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
          " style="background:#7c3aed;color:#fff;border:none;border-radius:8px;
                   padding:6px 16px;font-size:13px;font-weight:700;cursor:pointer;">
            📋 Copy
          </button>
        </div>
        <div id="{copy_id}" style="font-size:13px;color:#1e1b4b;line-height:1.7;
                    padding:14px 18px;background:#ffffff;border-radius:8px;
                    border:1px solid #e9e5f5;white-space:pre-wrap;
                    max-height:500px;overflow:auto;font-family:'JetBrains Mono','Fira Code',monospace;">
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


# ---------------------------------------------------------------------------
# File analyzer: cost card for a single model
# ---------------------------------------------------------------------------


def build_cost_card_html(
    model: str,
    provider: str,
    tokens: int,
    input_cost: float,
    output_cost: float,
) -> str:
    """Render a compact cost summary card for a single model selection."""
    total = input_cost + output_cost
    provider_colors = {
        "OpenAI":    ("#10a37f", "#f0fdf4"),
        "Anthropic": ("#d97706", "#fffbeb"),
        "Google":    ("#4285f4", "#eff6ff"),
    }
    accent, bg = provider_colors.get(provider, ("#7c3aed", "#f5f3ff"))

    return (
        f'<div style="border-radius:14px;padding:22px 26px;background:{bg};'
        f'border:2px solid {accent}44;margin-bottom:16px;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">'
        f'<span style="background:{accent};color:#fff;padding:3px 12px;border-radius:20px;'
        f'font-size:12px;font-weight:700;">{provider}</span>'
        f'<span style="color:#0f172a;font-weight:700;font-size:15px;">{model}</span>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;">'
        f'<div style="text-align:center;">'
        f'<div style="font-size:22px;font-weight:900;color:{accent};">{tokens:,}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">INPUT TOKENS</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:22px;font-weight:900;color:#059669;">${input_cost:.6f}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">INPUT COST</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:22px;font-weight:900;color:#d97706;">${output_cost:.6f}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">OUTPUT COST*</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:22px;font-weight:900;color:#7c3aed;">${total:.6f}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">TOTAL EST.</div>'
        f'</div>'
        f'</div>'
        f'<div style="margin-top:12px;font-size:11px;color:#94a3b8;">'
        f'* Output cost estimated assuming response length ≈ input length</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Token-saving suggestion card (used by Write New Prompt → Refine)
# ---------------------------------------------------------------------------


def build_token_saving_suggestion_html(
    original_tokens: int,
    original_cost: float,
    compressed_tokens: int,
    compressed_cost: float,
    compressed_text: str,
    reason: str,
) -> str:
    """Render a compact card showing the cheaper-prompt suggestion.

    Displayed beneath the Refine output in the Write New Prompt tab.
    Shows token/cost savings and the compressed prompt with a copy button.
    """
    saved_tokens = original_tokens - compressed_tokens
    saved_cost = original_cost - compressed_cost
    pct = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

    if saved_tokens <= 0:
        return (
            '<div style="padding:16px 20px;border-radius:12px;background:#f0fdf4;'
            'border:1px solid #bbf7d0;margin-top:16px;font-size:13px;color:#166534;'
            'font-weight:600;">'
            '✅ Your prompt is already concise — no further compression available.'
            '</div>'
        )

    copy_id = f"cheaper-copy-{id(compressed_text) % 100000}"
    escaped = _escape(compressed_text)
    display = escaped.replace("\n", "<br>") if escaped else ""

    return (
        f'<div style="margin-top:20px;border-radius:14px;padding:22px 26px;'
        f'background:linear-gradient(135deg,#ecfdf5,#f0fdf4);'
        f'border:2px solid #86efac;">'

        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
        f'<span style="font-size:20px;">💰</span>'
        f'<span style="font-size:15px;font-weight:800;color:#166534;">'
        f'Token Saving Summary</span>'
        f'</div>'

        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;'
        f'margin-bottom:16px;">'

        f'<div style="text-align:center;padding:10px;background:#fff;border-radius:10px;'
        f'border:1px solid #bbf7d0;">'
        f'<div style="font-size:20px;font-weight:900;color:#059669;">▼ {saved_tokens:,}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">'
        f'TOKENS SAVED</div></div>'

        f'<div style="text-align:center;padding:10px;background:#fff;border-radius:10px;'
        f'border:1px solid #bbf7d0;">'
        f'<div style="font-size:20px;font-weight:900;color:#059669;">{pct:.1f}%</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">'
        f'REDUCTION</div></div>'

        f'<div style="text-align:center;padding:10px;background:#fff;border-radius:10px;'
        f'border:1px solid #bbf7d0;">'
        f'<div style="font-size:20px;font-weight:900;color:#059669;">'
        f'${saved_cost:.6f}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;margin-top:2px;">'
        f'COST SAVED</div></div>'

        f'</div>'

        f'<div style="font-size:12px;color:#475569;margin-bottom:14px;'
        f'padding:8px 12px;background:#fff;border-radius:8px;border:1px solid #e5e7eb;">'
        f'<strong>What changed:</strong> {_escape(reason)}</div>'

        f'<div style="padding:16px 20px;border-radius:12px;background:#fff;'
        f'border:1px solid #bbf7d0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:8px;">'
        f'<span style="font-weight:700;font-size:13px;color:#166534;">'
        f'Optimized Prompt (ready to use)</span>'
        f'<button onclick="'
        f"var el=document.getElementById('{copy_id}');"
        f"var t=el?(el.innerText||el.textContent||'').trim():'';"
        f"if(!t)return;"
        f"var ta=document.createElement('textarea');"
        f"ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';"
        f"document.body.appendChild(ta);ta.select();"
        f"try{{document.execCommand('copy');}}catch(e){{}}"
        f"document.body.removeChild(ta);"
        f"var btn=event.target;btn.textContent='✓ Copied!';"
        f"setTimeout(function(){{btn.textContent='📋 Copy';}},2000);"
        f'" style="background:#059669;color:#fff;border:none;border-radius:8px;'
        f'padding:5px 14px;font-size:12px;font-weight:700;cursor:pointer;">'
        f'📋 Copy</button></div>'
        f'<div id="{copy_id}" style="font-size:13px;color:#14532d;line-height:1.7;'
        f'white-space:pre-wrap;max-height:300px;overflow:auto;">'
        f'{display}</div>'
        f'</div>'

        f'</div>'
    )


# ---------------------------------------------------------------------------
# All-models pricing comparison table (Write New Prompt → Refine)
# ---------------------------------------------------------------------------


def build_all_models_pricing_html(
    model_rows: list[dict],
    selected_model: str,
) -> str:
    """Render a comparison table showing token costs across all available models.

    Each row: model name, provider badge, input tokens, input cost, output cost,
    total cost, and a savings indicator vs the selected model.

    Args:
        model_rows: List of dicts, each with keys:
            model, provider, tokens, input_cost, output_cost, total_cost, available
        selected_model: The model the user chose (highlighted row).
    """
    rows_html = ""
    cheapest_total = min(
        (r["total_cost"] for r in model_rows if r["available"]),
        default=0,
    )

    provider_colors = {
        "OpenAI":    "#10a37f",
        "Anthropic": "#d97706",
        "Google":    "#4285f4",
    }

    for r in model_rows:
        accent = provider_colors.get(r["provider"], "#7c3aed")
        is_selected = r["model"] == selected_model
        is_cheapest = r["available"] and r["total_cost"] == cheapest_total

        bg = "#ede9fe" if is_selected else ("#f0fdf4" if is_cheapest else "#fff")
        border = f"2px solid {accent}" if is_selected else "1px solid #e5e7eb"

        badge = (
            f'<span style="background:{accent};color:#fff;padding:2px 8px;'
            f'border-radius:12px;font-size:10px;font-weight:700;">'
            f'{r["provider"]}</span>'
        )

        if not r["available"]:
            cost_cells = (
                '<td style="padding:8px 12px;color:#94a3b8;font-size:12px;" '
                'colspan="4"><em>API key not configured</em></td>'
            )
        else:
            labels = []
            if is_selected:
                labels.append(
                    '<span style="background:#7c3aed;color:#fff;padding:1px 6px;'
                    'border-radius:8px;font-size:9px;font-weight:700;">SELECTED</span>'
                )
            if is_cheapest:
                labels.append(
                    '<span style="background:#059669;color:#fff;padding:1px 6px;'
                    'border-radius:8px;font-size:9px;font-weight:700;">CHEAPEST</span>'
                )
            label_html = " ".join(labels)

            cost_cells = (
                f'<td style="padding:8px 12px;text-align:right;font-size:13px;'
                f'font-weight:700;color:#0f172a;">{r["tokens"]:,}</td>'
                f'<td style="padding:8px 12px;text-align:right;font-size:13px;'
                f'color:#059669;">${r["input_cost"]:.6f}</td>'
                f'<td style="padding:8px 12px;text-align:right;font-size:13px;'
                f'color:#d97706;">${r["output_cost"]:.6f}</td>'
                f'<td style="padding:8px 12px;text-align:right;font-size:13px;'
                f'font-weight:800;color:#7c3aed;">${r["total_cost"]:.6f} {label_html}</td>'
            )

        rows_html += (
            f'<tr style="background:{bg};border-bottom:{border};">'
            f'<td style="padding:8px 12px;font-size:13px;font-weight:600;">'
            f'{badge} {_escape(r["model"])}</td>'
            f'{cost_cells}'
            f'</tr>'
        )

    return (
        f'<div style="margin-top:20px;border-radius:14px;padding:22px 26px;'
        f'background:linear-gradient(135deg,#faf5ff,#eff6ff);'
        f'border:2px solid #c4b5fd;">'

        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">'
        f'<span style="font-size:20px;">📊</span>'
        f'<div>'
        f'<span style="font-size:15px;font-weight:800;color:#4c1d95;">'
        f'All Models — Token & Cost Comparison</span>'
        f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
        f'Costs calculated for the <strong>refined prompt</strong> across every model</div>'
        f'</div></div>'

        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%;border-collapse:collapse;border-radius:10px;'
        f'overflow:hidden;font-family:Inter,system-ui,sans-serif;">'
        f'<thead><tr style="background:#4c1d95;color:#ffffff;">'
        f'<th style="padding:12px 14px;text-align:left;font-size:13px;font-weight:800;'
        f'color:#ffffff;letter-spacing:0.5px;">Model</th>'
        f'<th style="padding:12px 14px;text-align:right;font-size:13px;font-weight:800;'
        f'color:#ffffff;letter-spacing:0.5px;">Tokens</th>'
        f'<th style="padding:12px 14px;text-align:right;font-size:13px;font-weight:800;'
        f'color:#ffffff;letter-spacing:0.5px;">Input Cost</th>'
        f'<th style="padding:12px 14px;text-align:right;font-size:13px;font-weight:800;'
        f'color:#ffffff;letter-spacing:0.5px;">Output Cost*</th>'
        f'<th style="padding:12px 14px;text-align:right;font-size:13px;font-weight:800;'
        f'color:#ffffff;letter-spacing:0.5px;">Total Est.</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'

        f'<div style="margin-top:10px;font-size:11px;color:#94a3b8;">'
        f'* Output cost estimated assuming response length ≈ input length. '
        f'Configure missing API keys in the Settings tab.</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# File analyzer: side-by-side comparison panel
# ---------------------------------------------------------------------------


def _avg_score(scores: dict) -> float:
    """Compute average score from a deepeval results dict."""
    if not scores:
        return 0.0
    vals = [v.get("score", 0.0) for v in scores.values()]
    return sum(vals) / len(vals) if vals else 0.0


def _delta_token_badge(delta: int) -> str:
    color = "#059669" if delta < 0 else "#dc2626"
    sign = "▼" if delta < 0 else "▲"
    return (
        f'<span style="background:{color}22;color:{color};padding:2px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:700;">{sign} {abs(delta):,} tokens</span>'
    )


def _delta_cost_badge(delta: float) -> str:
    color = "#059669" if delta < 0 else "#dc2626"
    sign = "▼" if delta < 0 else "▲"
    return (
        f'<span style="background:{color}22;color:{color};padding:2px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:700;">{sign} ${abs(delta):.6f}</span>'
    )


def _score_delta_badge(delta: float) -> str:
    color = "#059669" if delta >= 0 else "#dc2626"
    sign = "+" if delta >= 0 else ""
    return (
        f'<span style="background:{color}22;color:{color};padding:2px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:700;">{sign}{delta:.2f}</span>'
    )


def _half_panel(
    label: str,
    accent: str,
    text_preview: str,
    tokens: int,
    total_cost: float,
    avg_score: float,
    token_delta_html: str = "",
    cost_delta_html: str = "",
    score_delta_html: str = "",
    reason: str = "",
) -> str:
    preview = _escape(text_preview[:300]) + ("…" if len(text_preview) > 300 else "")
    score_color = _score_color(avg_score)
    score_pct = int(avg_score * 100)

    reason_block = (
        f'<div style="margin-top:12px;padding:10px 14px;border-radius:8px;'
        f'background:#f0fdf4;border-left:3px solid #059669;font-size:12px;color:#166534;">'
        f'<strong>What was trimmed:</strong> {_escape(reason)}</div>'
        if reason else ""
    )

    return (
        f'<div style="flex:1;min-width:280px;border-radius:14px;padding:20px;'
        f'background:#ffffff;border:2px solid {accent}44;">'
        f'<div style="font-size:13px;font-weight:800;color:{accent};margin-bottom:14px;'
        f'text-transform:uppercase;letter-spacing:0.05em;">{label}</div>'
        f'<pre style="background:#f8fafc;border-radius:8px;padding:12px;font-size:12px;'
        f'color:#334155;overflow:auto;max-height:160px;white-space:pre-wrap;'
        f'word-break:break-word;border:1px solid #e2e8f0;">{preview}</pre>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px;">'
        f'<div style="text-align:center;">'
        f'<div style="font-size:20px;font-weight:900;color:#1e1b4b;">{tokens:,}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;">TOKENS</div>'
        f'<div style="margin-top:4px;">{token_delta_html}</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:20px;font-weight:900;color:#7c3aed;">${total_cost:.6f}</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;">TOTAL COST</div>'
        f'<div style="margin-top:4px;">{cost_delta_html}</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:20px;font-weight:900;color:{score_color};">{score_pct}%</div>'
        f'<div style="font-size:11px;color:#64748b;font-weight:600;">QUALITY SCORE</div>'
        f'<div style="margin-top:4px;">{score_delta_html}</div>'
        f'</div>'
        f'</div>'
        f'{reason_block}'
        f'</div>'
    )


def build_comparison_html(
    original_text: str,
    original_tokens: int,
    original_input_cost: float,
    original_output_cost: float,
    original_scores: dict,
    alt_text: str,
    alt_tokens: int,
    alt_input_cost: float,
    alt_output_cost: float,
    alt_scores: dict,
    reason: str,
) -> str:
    """Render a side-by-side comparison: original vs cheaper alternative."""
    orig_total = original_input_cost + original_output_cost
    alt_total = alt_input_cost + alt_output_cost

    token_delta = alt_tokens - original_tokens
    cost_delta = alt_total - orig_total
    orig_avg = _avg_score(original_scores)
    alt_avg = _avg_score(alt_scores)
    score_delta = alt_avg - orig_avg

    tok_badge = _delta_token_badge(token_delta) if token_delta != 0 else ""
    cost_badge = _delta_cost_badge(cost_delta) if cost_delta != 0 else ""
    score_badge = _score_delta_badge(score_delta)

    orig_panel = _half_panel(
        label="Original Prompt",
        accent="#6366f1",
        text_preview=original_text,
        tokens=original_tokens,
        total_cost=orig_total,
        avg_score=orig_avg,
    )

    alt_panel = _half_panel(
        label="Cheaper Alternative",
        accent="#059669",
        text_preview=alt_text,
        tokens=alt_tokens,
        total_cost=alt_total,
        avg_score=alt_avg,
        token_delta_html=tok_badge,
        cost_delta_html=cost_badge,
        score_delta_html=score_badge,
        reason=reason,
    )

    savings_pct = (1 - alt_total / orig_total) * 100 if orig_total > 0 else 0
    summary = ""
    if token_delta < 0:
        summary = (
            f'<div style="padding:14px 20px;background:linear-gradient(135deg,#f0fdf4,#ecfdf5);'
            f'border-radius:12px;border:1px solid #bbf7d0;margin-bottom:16px;'
            f'display:flex;align-items:center;gap:16px;flex-wrap:wrap;">'
            f'<span style="font-size:15px;font-weight:800;color:#166534;">Savings Summary</span>'
            f'<span style="color:#374151;font-size:13px;">Tokens saved: '
            f'<strong style="color:#059669;">{abs(token_delta):,}</strong></span>'
            f'<span style="color:#374151;font-size:13px;">Cost saved: '
            f'<strong style="color:#059669;">${abs(cost_delta):.6f} ({savings_pct:.1f}%)</strong></span>'
            f'<span style="color:#374151;font-size:13px;">Quality: '
            f'<strong style="color:{"#059669" if score_delta >= -0.05 else "#dc2626"};">'
            f'{"maintained" if score_delta >= -0.05 else "reduced"}</strong></span>'
            f'</div>'
        )

    return (
        f'<div style="margin-top:24px;">'
        f'<div style="font-size:18px;font-weight:800;color:#1e1b4b;margin-bottom:16px;">'
        f'Cost vs Quality Comparison</div>'
        f'{summary}'
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        f'{orig_panel}{alt_panel}'
        f'</div>'
        f'<div style="margin-top:16px;font-size:12px;color:#94a3b8;">'
        f'Quality scores averaged across Clarity, Specificity, Completeness, Coherence, and Safety.'
        f'</div>'
        f'</div>'
    )
