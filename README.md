# PromptAnalyzer

Evaluate and optimize LLM prompts and **Skill/Agent definitions** for **quality and token efficiency** — using [DeepEval](https://deepeval.com/) G-Eval metrics with support for **OpenAI**, **Anthropic**, and **Google Gemini**.

**Key features:**
- **Input metrics** — Clarity, Specificity, Completeness, Coherence, Safety
- **Output metrics** — Relevancy, Hallucination, Bias, Toxicity, Conciseness, Context Precision
- **Token savings** — Compress-first refinement pipeline that optimizes for cost without losing intent
- **All-models pricing** — Compare token counts and costs across 8 models (GPT-4o, GPT-4o-mini, GPT-3.5-Turbo, Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus, Gemini 1.5 Pro, Gemini 1.5 Flash)
- **Skill/Agent refinement** — Treats uploaded files as Skill or Agent definitions, not generic prompts

---

## Quick Start

### Prerequisites

- Python >= 3.10
- **uv** — install via the scripts below, or see [Installation](https://docs.astral.sh/uv/getting-started/installation/)

### Run with scripts

| Platform                   | Command  |
|----------------------------|----------|
| **macOS / Linux / Ubuntu** | `./run.sh` |
| **Windows**                | `run.bat`  |

- **First time:** Installs uv (if missing), runs `uv sync`, then starts the app.
- **Next times:** Same command — syncs if needed and starts.

### Install & Run (manual)

```bash
cd PromptAnalyzer
uv sync
uv run python app.py
```

The app will be available at **http://localhost:7860**.

### First-Time Setup

1. Open the app → **Settings** tab.
2. Enter your **OpenAI**, **Anthropic**, and/or **Google** API key.
3. Click **Save API Keys** — stored in `.env` and auto-loaded on restart.

---

## Tabs

### Tab 1: Analyze Prompt File

Upload a **Skill**, **Agent**, or **Subagent** file (`.md`, `.txt`, `.py`, `.yaml`, `.json`) or paste content.

| Action | What it does |
|--------|-------------|
| **Analyze** | Token count + pricing card, then full evaluation: 5 input metrics + LLM response generation + 6 output metrics |
| **View & Save** | Display content for review/editing, download as file |
| **Refine** | Compress for token savings → refine for quality. Shows token saving summary (original vs refined), model badge, issues found, refined skill/agent with copy button |

Optional **Additional Context** field lets you provide a JIRA ticket URL or domain info to improve refinement accuracy.

### Tab 2: Write New Prompt

Describe your goal — the **PROMPT** or **CROFT** framework is auto-detected.

| Action | What it does |
|--------|-------------|
| **Build Structured Prompt** | Auto-generates a structured prompt using the detected framework (no LLM call) |
| **Evaluate Prompt** | Token cost card + full input/output evaluation (same pipeline as Tab 1) |
| **Refine Prompt** | Compress-first pipeline: (1) generate cheapest-token version, (2) refine compressed version for quality, (3) all-models pricing comparison table |
| **Save as .txt** | Download the prompt as a file |

**Prompt frameworks:**
- **PROMPT** — Persona · Request · Output · Method · Purpose · Task
- **CROFT** — Context · Role · Objective · Format · Tone
- **4D Principles** — Delegation · Description · Discernment · Diligence

### Tab 3: Settings

Configure API keys for OpenAI, Anthropic, and Google. Keys are validated, saved to `.env`, and loaded on startup.

---

## Evaluation Metrics

All metrics use DeepEval's **GEval** (LLM-as-a-judge with chain-of-thought).

### Input Metrics (prompt quality)

| Metric           | What It Measures |
|------------------|------------------|
| **Clarity**      | Unambiguous, precise language an LLM can interpret without guessing intent |
| **Specificity**  | Concrete constraints, format requirements, and scope-narrowing details |
| **Completeness** | All necessary context provided — no follow-up questions needed |
| **Coherence**    | Logical structure, ordering of instructions, no contradictions |
| **Safety**       | Absence of harmful, unethical, or jailbreak content |

### Output Metrics (response quality)

| Metric              | What It Measures |
|---------------------|------------------|
| **Relevancy**       | How well the LLM response addresses the prompt |
| **Hallucination**   | Whether the response contains fabricated information |
| **Bias**            | Presence of unfair or discriminatory content |
| **Toxicity**        | Harmful, offensive, or inappropriate language |
| **Conciseness**     | Whether the response is focused without unnecessary content |
| **Context Precision** | Accuracy of information relative to the provided context |

### Score Indicators

| Score Range | Color  | Meaning |
|-------------|--------|---------|
| >= 80%      | Green  | Good    |
| 50-79%      | Yellow | Needs improvement |
| < 50%       | Red    | Poor    |

---

## Supported Models & Pricing

All costs are per million tokens (input / output):

| Model | Provider | Input | Output |
|-------|----------|-------|--------|
| gpt-4o | OpenAI | $2.50 | $10.00 |
| gpt-4o-mini | OpenAI | $0.15 | $0.60 |
| gpt-3.5-turbo | OpenAI | $0.50 | $1.50 |
| claude-3-5-sonnet | Anthropic | $3.00 | $15.00 |
| claude-3-haiku | Anthropic | $0.25 | $1.25 |
| claude-3-opus | Anthropic | $15.00 | $75.00 |
| gemini-1.5-pro | Google | $1.25 | $5.00 |
| gemini-1.5-flash | Google | $0.075 | $0.30 |

---

## Architecture

### File roles

| File | Role |
|------|------|
| **`app.py`** | Gradio UI, event wiring, analysis/refinement handlers, token pricing helpers |
| **`evaluator.py`** | DeepEval metrics, `run_full_evaluation()`, `refine_prompt()`, `refine_skill()`, LLM response generation |
| **`styles.py`** | CSS, HTML renderers for cost cards, evaluation results, refinement panels, pricing tables |
| **`config/pricing.py`** | Model lists, pricing per million tokens, display names, provider lookup |
| **`services/suggestion_engine.py`** | Prompt compression — generates cheaper alternatives while preserving intent |
| **`prompt_builder.py`** | PROMPT/CROFT framework auto-detection and structured prompt generation |
| **`prompt_library.py`** | Predefined prompt categories |

### Evaluation flow

```
analyze_prompt() / evaluate_new_prompt()
    │
    ├── _pricing_for_model()          → Token count + cost card
    │
    └── run_full_evaluation()         → evaluator.py
         │
         ├── _build_input_metrics()   → 5 GEval metrics (Clarity, Specificity, ...)
         ├── _measure_metrics()       → metric.measure(test_case) for each
         │
         ├── generate_prompt_response() → LLM generates actual response
         │
         ├── _build_output_metrics()  → 6 metrics (Relevancy, Hallucination, ...)
         └── _measure_metrics()       → metric.measure(test_case) for each
              │
              └── returns { input_scores, output_scores, response_text, errors }
```

### Refinement flow

```
refine_analyzed_prompt() [Tab 1]    refine_new_prompt() [Tab 2]
    │                                    │
    ├── generate_cheaper_alternative()   ├── generate_cheaper_alternative()
    │   (compress for token savings)     │   (compress for token savings)
    │                                    │
    ├── refine_skill()                   ├── refine_prompt()
    │   (quality improvement on          │   (quality improvement on
    │    compressed text)                │    compressed text)
    │                                    │
    └── build_skill_refinement_html()    ├── build_refinement_html()
        (token savings + model badge     │   (issues + refined prompt)
         + issues + refined skill)       │
                                         └── build_all_models_pricing_html()
                                             (8-model comparison table)
```

### Project structure

```
PromptAnalyzer/
├── app.py                    # Gradio app: UI, events, handlers
├── evaluator.py              # DeepEval metrics, evaluation, refinement
├── styles.py                 # CSS + HTML renderers
├── prompt_builder.py         # PROMPT/CROFT framework builder
├── prompt_library.py         # Prompt categories
├── config/
│   └── pricing.py            # Model pricing, lists, display names
├── services/
│   └── suggestion_engine.py  # Prompt compression engine
├── run.sh                    # Run on macOS / Linux
├── run.bat                   # Run on Windows
├── install_uv.sh             # Install uv (Mac/Linux)
├── install_uv.bat            # Install uv (Windows)
├── pyproject.toml            # Dependencies
├── prompts.json              # Auto-generated prompt storage
├── .env                      # API keys (git-ignored)
└── README.md
```

---

## Token Saving Tips

1. **Use `gpt-4o-mini` or `gemini-1.5-flash`** — cheapest models for evaluation
2. **Click Refine** — the compress-first pipeline removes redundancy while preserving intent
3. **Check the all-models pricing table** (Tab 2) — compare costs across all providers at a glance
4. **Remove filler** — the compression engine trims boilerplate, repetition, and over-explanation
5. **Provide context** (Tab 1) — adding a JIRA ticket or domain info helps the AI produce a more focused refinement

---

## License

MIT
