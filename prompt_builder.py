"""
prompt_builder.py — Framework-based prompt generation for PromptAnalyzer.

Implements the PROMPT and CROFT prompt-engineering frameworks with
automatic framework detection based on the user's stated intent.

Following the 4D Principles of AI Fluency:
  • Delegation   — identify what to hand off to the model
  • Description  — produce a clear, complete description of the task
  • Discernment  — select the right framework for the situation
  • Diligence    — fill every section thoroughly so the model can succeed

No LLM calls are made here.  All inference is rule-based and runs instantly.
"""
from __future__ import annotations

import re
from typing import Literal

FrameworkType = Literal["PROMPT", "CROFT"]

# ---------------------------------------------------------------------------
# Framework definitions
# ---------------------------------------------------------------------------

FRAMEWORKS: dict[str, dict[str, str]] = {
    "PROMPT": {
        "label": "PROMPT",
        "full":  "Persona · Request · Output · Method · Purpose · Task",
        "description": (
            "Best for technical, code-generation, and structured-output tasks. "
            "Gives the model a clear persona, exact request, output format, "
            "method constraints, purpose, and a concrete task statement."
        ),
        "color": "#7c3aed",
        "icon":  "⚙️",
    },
    "CROFT": {
        "label": "CROFT",
        "full":  "Context · Role · Objective · Format · Tone",
        "description": (
            "Best for analytical, conversational, creative, and advisory tasks. "
            "Grounds the model in rich context, assigns a domain role, states a "
            "clear objective, defines the output format, and sets the right tone."
        ),
        "color": "#0ea5e9",
        "icon":  "💬",
    },
}

# ---------------------------------------------------------------------------
# Keyword sets used for detection (Discernment principle)
# ---------------------------------------------------------------------------

# Signals → PROMPT framework (technical / structured-output tasks)
_PROMPT_SIGNALS: frozenset[str] = frozenset({
    "code", "program", "function", "script", "debug", "implement",
    "develop", "build", "deploy", "automate", "refactor", "optimize",
    "python", "javascript", "typescript", "sql", "html", "css", "json",
    "yaml", "api", "endpoint", "schema", "migration", "database",
    "algorithm", "data structure", "class", "method", "module",
    "framework", "library", "pipeline", "workflow", "system",
    "architecture", "backend", "frontend", "fullstack", "cli",
    "devops", "docker", "kubernetes", "microservice", "ci/cd",
    "test case", "unit test", "integration test", "playwright", "selenium",
    "pytest", "jest", "generate code", "write code", "create function",
    "lint", "format", "type hint", "monorepo", "package", "dependency",
    "infrastructure", "terraform", "ansible", "cloud", "aws", "azure", "gcp",
})

# Signals → CROFT framework (analytical / conversational / creative tasks)
_CROFT_SIGNALS: frozenset[str] = frozenset({
    "explain", "describe", "summarize", "summarise", "analyse", "analyze",
    "compare", "review", "advise", "recommend", "help me understand",
    "what is", "what are", "how does", "how do", "why does", "why is",
    "draft an", "draft a", "compose", "write an email", "write a letter",
    "write an article", "write a blog", "write an essay", "write a story",
    "write a report", "write a proposal",
    "letter", "blog post", "article", "essay", "story",
    "report", "proposal", "plan", "strategy", "guide", "roadmap",
    "act as", "pretend", "imagine", "be a", "role play",
    "consult", "coach", "mentor", "teach", "tutor",
    "research", "investigate", "assess", "evaluate", "critique",
    "translate", "rewrite", "edit", "proofread", "improve writing",
    "brainstorm", "suggestions", "feedback", "overview", "introduction",
    "summary", "breakdown", "walkthrough", "interview", "presentation",
    "pitch", "case study", "whitepaper", "newsletter",
})

# Strong PROMPT anchors — code-specific tokens that always lean PROMPT
# even when other CROFT signals are present
_STRONG_PROMPT_ANCHORS: frozenset[str] = frozenset({
    "python", "javascript", "typescript", "sql", "html", "css", "json",
    "yaml", "bash", "shell", "rust", "golang", "java", "c++", "c#",
    "function", "class", "method", "module", "script", "algorithm",
    "api endpoint", "unit test", "integration test", "dockerfile",
    "kubernetes", "terraform", "ci/cd", "pytest", "jest", "playwright",
})


# ---------------------------------------------------------------------------
# Heuristic component extractors
# ---------------------------------------------------------------------------

def _extract_persona(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("test", "qa", "quality assurance", "playwright", "selenium", "pytest")):
        return "You are an expert QA Engineer and software-testing specialist"
    if any(k in t for k in ("machine learning", "ml ", "ai model", "deep learning", "data science", "llm")):
        return "You are an expert Machine Learning Engineer and AI researcher"
    if any(k in t for k in ("devops", "docker", "kubernetes", "ci/cd", "deploy", "terraform", "cloud")):
        return "You are an expert DevOps Engineer and cloud-infrastructure specialist"
    if any(k in t for k in ("security", "vulnerability", "penetration", "auth", "encryption", "owasp")):
        return "You are an expert Application Security Engineer"
    if any(k in t for k in ("data", "sql", "database", "query", "analytics", "etl", "pipeline")):
        return "You are an expert Data Engineer and database architect"
    if any(k in t for k in ("frontend", "ui ", "ux ", "react", "vue", "angular", "css", "html")):
        return "You are an expert Frontend Engineer and UX specialist"
    if any(k in t for k in ("backend", "api", "server", "microservice", "endpoint", "rest", "graphql")):
        return "You are an expert Backend Engineer and API designer"
    if any(k in t for k in ("code", "program", "develop", "build", "implement", "software")):
        return "You are an expert Software Engineer with broad full-stack experience"
    return "You are a highly skilled professional with deep domain expertise"


def _infer_role(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("write", "draft", "compose", "blog", "article", "essay", "story", "email")):
        return "You are an expert writer, editor, and content strategist"
    if any(k in t for k in ("analyze", "analyse", "review", "assess", "evaluate", "critique", "audit")):
        return "You are an experienced analyst with strong critical-thinking and evaluation skills"
    if any(k in t for k in ("explain", "teach", "tutor", "help understand", "learn", "educate")):
        return "You are an expert educator who excels at making complex topics accessible"
    if any(k in t for k in ("plan", "strategy", "roadmap", "prioritize", "organize", "prioritise")):
        return "You are a strategic consultant with extensive planning and advisory experience"
    if any(k in t for k in ("research", "investigate", "explore", "discover", "study")):
        return "You are a meticulous researcher who synthesises information with precision"
    if any(k in t for k in ("translate", "localize", "localise", "language", "locale")):
        return "You are an expert linguist and translator with broad cross-cultural knowledge"
    if any(k in t for k in ("coach", "mentor", "guide", "advise", "counsel")):
        return "You are a trusted mentor with deep expertise in professional and personal development"
    return "You are a knowledgeable expert with broad experience across relevant domains"


def _extract_output_format(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("bullet", "bulleted", "list", "items", "points")):
        return "Bulleted list with concise, actionable items"
    if any(k in t for k in ("table", "comparison", "matrix", "grid")):
        return "Structured table with clearly labelled columns and rows"
    if any(k in t for k in ("code", "script", "function", "class", "module")):
        return "Well-commented code block followed by a practical usage example"
    if any(k in t for k in ("report", "document", "specification", "spec")):
        return "Structured document with titled sections and subsections"
    if any(k in t for k in ("summary", "brief", "overview", "tldr", "tl;dr")):
        return "Concise summary highlighting 3–5 key points"
    if any(k in t for k in ("json", "yaml", "xml", "schema")):
        return "Valid, schema-compliant JSON/YAML with inline comments explaining each field"
    if any(k in t for k in ("test case", "test plan", "scenario", "gherkin", "bdd")):
        return "Test cases in Gherkin format (Given / When / Then) or clearly numbered steps"
    if any(k in t for k in ("step", "steps", "how to", "tutorial", "walkthrough")):
        return "Numbered step-by-step guide with a brief explanation at each stage"
    if any(k in t for k in ("email", "letter", "message", "memo")):
        return "Properly formatted communication with subject, greeting, body, and sign-off"
    if any(k in t for k in ("plan", "roadmap", "strategy", "timeline")):
        return "Structured plan with phases, actions, owners, and success criteria"
    return "Clear, structured response using headers, bullet points, and examples where appropriate"


def _extract_tone(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("technical", "engineering", "developer", "code", "architecture")):
        return "Technical and precise — use domain-specific vocabulary"
    if any(k in t for k in ("simple", "beginner", "basic", "easy to understand", "non-technical")):
        return "Clear and jargon-free — accessible to a non-specialist audience"
    if any(k in t for k in ("formal", "professional", "business", "enterprise", "executive")):
        return "Formal and polished — appropriate for a professional or executive audience"
    if any(k in t for k in ("creative", "story", "blog", "article", "engaging", "compelling")):
        return "Engaging and narrative — conversational yet authoritative"
    if any(k in t for k in ("friendly", "casual", "informal", "conversational", "relaxed")):
        return "Friendly and conversational — warm, helpful, and approachable"
    return "Professional and concise — clear, direct, and respectful of the reader's time"


# ---------------------------------------------------------------------------
# Framework detection  (Discernment principle)
# ---------------------------------------------------------------------------

def detect_framework(text: str) -> tuple[FrameworkType, str, float]:
    """
    Detect whether PROMPT or CROFT framework best fits the user's stated intent.

    Args:
        text: Raw user input describing what they want the prompt to do.

    Returns:
        (framework, reason, confidence)
          • framework  — "PROMPT" or "CROFT"
          • reason     — Human-readable explanation shown in the badge
          • confidence — Float 0–1 representing signal strength
    """
    if not text.strip():
        return (
            "PROMPT",
            "Enter your idea above — the framework will be auto-selected as you type.",
            0.5,
        )

    tl = text.lower()
    prompt_score = sum(1 for kw in _PROMPT_SIGNALS if kw in tl)
    croft_score  = sum(1 for kw in _CROFT_SIGNALS  if kw in tl)
    total = prompt_score + croft_score

    if total == 0:
        # Heuristic tiebreak on text length
        if len(text.split()) <= 8:
            return (
                "PROMPT",
                "Short directive detected — PROMPT keeps focused tasks well-structured.",
                0.55,
            )
        return (
            "CROFT",
            "Descriptive intent detected — CROFT is the better fit for open-ended requests.",
            0.55,
        )

    if prompt_score > croft_score:
        confidence = round(prompt_score / total, 2)
        examples   = [kw for kw in _PROMPT_SIGNALS if kw in tl][:3]
        reason = (
            f"Technical signals detected ({', '.join(examples)}) — "
            "PROMPT structures code and system tasks most effectively."
        )
        return "PROMPT", reason, confidence

    if croft_score > prompt_score:
        confidence = round(croft_score / total, 2)
        examples   = [kw for kw in _CROFT_SIGNALS if kw in tl][:3]
        reason = (
            f"Analytical / creative signals detected ({', '.join(examples)}) — "
            "CROFT excels at conversational and advisory prompts."
        )
        return "CROFT", reason, confidence

    # True tie — check for strong PROMPT anchors (explicit language/code tokens)
    anchor_hits = [kw for kw in _STRONG_PROMPT_ANCHORS if kw in tl]
    if anchor_hits:
        return (
            "PROMPT",
            f"Code/language anchor detected ({', '.join(anchor_hits[:3])}) — "
            "PROMPT is chosen to structure the technical task precisely.",
            0.65,
        )

    # Final fallback → CROFT (more versatile for general tasks)
    return (
        "CROFT",
        "Mixed signals — CROFT chosen as the safer general-purpose default.",
        0.5,
    )


# ---------------------------------------------------------------------------
# Prompt builders  (Description + Diligence principles)
# ---------------------------------------------------------------------------

def build_prompt(user_input: str, framework: FrameworkType) -> str:
    """
    Generate a fully structured prompt from the user's free-text idea.

    Applies the specified framework template filled with heuristic extractions
    from the user's input.  No LLM is used.

    Args:
        user_input: Raw user idea / intent text.
        framework:  "PROMPT" or "CROFT".

    Returns:
        Structured prompt string, ready to copy, evaluate, or refine.
    """
    text = user_input.strip()
    if not text:
        return ""
    return _build_prompt_fw(text) if framework == "PROMPT" else _build_croft_fw(text)


def _build_prompt_fw(idea: str) -> str:
    """Assemble a PROMPT-framework prompt (Persona–Request–Output–Method–Purpose–Task)."""
    persona    = _extract_persona(idea)
    output_fmt = _extract_output_format(idea)
    tone       = _extract_tone(idea)

    return f"""## Persona
{persona} with a strong commitment to quality, correctness, and best practices.

## Request
{idea}

## Output
Deliver the response in the following format:
- {output_fmt}
- Include concrete, specific examples — avoid generic placeholders
- Use clear headings or dividers between distinct sections

## Method
- Reason step-by-step before writing the final answer
- Validate assumptions before proceeding
- Identify and address edge cases and potential failure points
- Prioritise accuracy and clarity over brevity

## Purpose
To deliver a precise, actionable, and well-structured response that directly addresses the request and can be applied immediately without further clarification.

## Task
Carefully analyse the request, then produce a comprehensive response that follows the output format above. Be specific, avoid vague language, ground every recommendation in best practices, and maintain this tone throughout: {tone}."""


def _build_croft_fw(idea: str) -> str:
    """Assemble a CROFT-framework prompt (Context–Role–Objective–Format–Tone)."""
    role       = _infer_role(idea)
    output_fmt = _extract_output_format(idea)
    tone       = _extract_tone(idea)

    return f"""## Context
{idea}

Draw on relevant background knowledge, common assumptions in this domain, and any implicit constraints that would help produce a high-quality response.

## Role
{role}. Bring your expertise to this task — deliver a response that reflects genuine insight and domain mastery, not generic advice.

## Objective
Fully address the request stated in the Context section. The goal is accuracy, thoroughness, and immediate actionability. Be specific and ground every point in evidence or established best practices; avoid vague generalisations.

## Format
{output_fmt}

Organise the response so it is easy to scan and act on. Use headers, bullet points, numbered steps, or tables wherever they improve readability. Include examples or illustrations for any complex points.

## Tone
{tone}. Maintain the appropriate level of rigour for the subject while keeping the response accessible and engaging throughout."""


# ---------------------------------------------------------------------------
# Badge HTML renderer  (used by app.py to show detection result in the UI)
# ---------------------------------------------------------------------------

def render_detection_badge(framework: FrameworkType, reason: str, confidence: float) -> str:
    """
    Return an HTML badge string showing the auto-detected framework and reason.

    Args:
        framework:  "PROMPT" or "CROFT"
        reason:     Human-readable explanation from detect_framework()
        confidence: 0–1 float

    Returns:
        HTML string for a gr.HTML component.
    """
    fw   = FRAMEWORKS[framework]
    pct  = int(confidence * 100)
    bar_color = fw["color"]

    # Confidence label
    if confidence >= 0.75:
        conf_label = "High confidence"
        conf_color = "#16a34a"
    elif confidence >= 0.55:
        conf_label = "Moderate confidence"
        conf_color = "#d97706"
    else:
        conf_label = "Low confidence — feel free to override"
        conf_color = "#6b7280"

    other_fw = "CROFT" if framework == "PROMPT" else "PROMPT"
    other    = FRAMEWORKS[other_fw]

    return f"""
<div style="
    border:2px solid {bar_color};
    border-radius:12px;
    padding:14px 18px;
    background:linear-gradient(135deg,{bar_color}12,{bar_color}06);
    font-family:Inter,sans-serif;
    margin-bottom:4px;
">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <span style="font-size:22px;">{fw['icon']}</span>
    <div>
      <div style="font-weight:800;font-size:15px;color:{bar_color};">
        Auto-detected: {fw['label']} Framework
      </div>
      <div style="font-size:12px;color:#64748b;">{fw['full']}</div>
    </div>
    <div style="margin-left:auto;text-align:right;">
      <span style="
        background:{conf_color}22;color:{conf_color};
        border:1px solid {conf_color}55;
        border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;
      ">{conf_label}</span>
    </div>
  </div>
  <div style="
    background:#e2e8f0;border-radius:4px;height:5px;margin-bottom:10px;
  ">
    <div style="
      background:{bar_color};height:5px;border-radius:4px;width:{pct}%;
      transition:width 0.4s ease;
    "></div>
  </div>
  <div style="font-size:12px;color:#475569;line-height:1.5;margin-bottom:10px;">
    {reason}
  </div>
  <div style="font-size:11px;color:#94a3b8;">
    <strong>Not right?</strong> Switch to
    <span style="color:{other['color']};font-weight:700;">{other_fw}</span>
    ({other['full']}) using the selector below.
  </div>
</div>
"""


def render_empty_badge() -> str:
    """Return the initial placeholder badge shown before any input is typed."""
    return """
<div style="
    border:2px dashed #c4b5fd;border-radius:12px;padding:16px 18px;
    background:linear-gradient(135deg,#ede9fe,#dbeafe);
    font-family:Inter,sans-serif;text-align:center;
">
  <div style="font-size:28px;margin-bottom:6px;">🧠</div>
  <div style="font-weight:700;color:#4c1d95;font-size:14px;margin-bottom:4px;">
    Framework Auto-Detection
  </div>
  <div style="font-size:12px;color:#6b7280;line-height:1.5;">
    Describe what you want to accomplish above.<br>
    The best framework — <strong>PROMPT</strong> or <strong>CROFT</strong> —
    will be selected automatically based on your intent.
  </div>
</div>
"""
