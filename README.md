# PromptAnalyzer

Evaluate LLM prompts on **Clarity, Specificity, Completeness, Coherence, and Safety** using [DeepEval](https://deepeval.com/) G-Eval metrics — with support for both **OpenAI** and **Anthropic** as evaluation providers.

---

## Where DeepEval Is Used

DeepEval is used **only** in **`evaluator.py`**. The rest of the app (Gradio UI, templates, persistence) does not import DeepEval directly.

| File        | Role |
|------------|------|
| **`evaluator.py`** | Defines metrics, builds `GEval` instances, runs evaluation via `LLMTestCase` and `metric.measure()`. Imports `deepeval` only when evaluation or refinement runs. |
| **`app.py`**       | Calls `run_evaluation()` and `refine_prompt()` from `evaluator` when the user clicks **Evaluate Prompt** or **Refine Prompt**. No DeepEval imports. |
| **`styles.py`**   | Renders evaluation results (scores, progress bars) and refinement HTML. References "DeepEval" only in user-facing copy. |

---

## How DeepEval Evaluation Is Organized

### 1. Entry points (who calls DeepEval)

All evaluation goes through **`evaluator.run_evaluation(prompt_text, provider, model)`**:

| Call site in `app.py` | When it runs |
|------------------------|--------------|
| **`_assemble_and_evaluate()`** (around line 339) | User is on **Cursor Prompts** tab, selects a template, fills inputs, clicks **Evaluate Prompt**. The assembled prompt is passed to `run_evaluation()`. |
| **`evaluate_new_prompt()`** (around line 403) | User is on **Write New Prompt** tab, enters or edits prompt text, clicks **Evaluate Prompt**. The prompt text is passed to `run_evaluation()`. |

Refinement (improved prompt suggestions) uses **`evaluator.refine_prompt()`**, which uses the **OpenAI or Anthropic** API directly (not DeepEval):

| Call site in `app.py` | When it runs |
|------------------------|--------------|
| **`_assemble_and_refine()`** (around line 378) | **Cursor Prompts** tab → **Refine Prompt**. |
| **`handle_refine_new()`** (around line 444) | **Write New Prompt** tab → **Refine Prompt**. |

So: **DeepEval = scoring only.** Refinement = plain LLM calls from `evaluator.py`.

### 2. Flow inside `evaluator.py`

```
run_evaluation(prompt_text, provider, model)
    |
    +-- _check_api_key(provider)           # Raises if key missing
    +-- _resolve_model(provider, model)    # Picks e.g. gpt-4o-mini
    |
    +-- LLMTestCase(input=prompt_text, actual_output=prompt_text)
    |     # DeepEval needs a "test case"; we treat the prompt as both input and output.
    |
    +-- _build_metrics(model_str)
    |     # For each of the 5 metrics (Clarity, Specificity, Completeness, Coherence, Safety):
    |     #   - Imports deepeval.metrics.GEval, deepeval.test_case.LLMTestCaseParams
    |     #   - Creates GEval(name=..., criteria=..., evaluation_steps=..., ...)
    |     #   - evaluation_params = [INPUT, ACTUAL_OUTPUT] so the judge sees the prompt
    |     # Returns list of GEval instances.
    |
    +-- For each metric:
          metric.measure(test_case)   # <-- DeepEval calls the LLM (OpenAI/Anthropic) to score
          results[metric.name] = { score, reason, passed }
    |
    +-- return results   # Dict[str, Dict] -> used by app.py to render HTML (styles.build_results_html)
```

### 3. What DeepEval APIs are used

| API | Where | Purpose |
|-----|--------|---------|
| **`deepeval.metrics.GEval`** | `evaluator._build_metrics()` | One GEval per metric (Clarity, Specificity, etc.). Each has `name`, `criteria`, `evaluation_steps`, `evaluation_params=[INPUT, ACTUAL_OUTPUT]`, `model`, `threshold`. |
| **`deepeval.test_case.LLMTestCase`** | `evaluator.run_evaluation()` | Wraps the prompt as `input` and `actual_output` (same text) for the judge. |
| **`deepeval.test_case.LLMTestCaseParams`** | `evaluator._build_metrics()` | Used as `evaluation_params` so GEval receives the prompt text. |
| **`metric.measure(test_case)`** | `evaluator.run_evaluation()` | Runs the LLM-as-judge; sets `metric.score`, `metric.reason`, and threshold `passed`. |

Imports from `deepeval` are **lazy** (inside functions). That way the app can start without an API key; DeepEval is only loaded when the user runs an evaluation.

### 4. Metric definitions

The five metrics are defined in **`evaluator.METRIC_DEFS`**. Each entry has:

- **`name`** → GEval `name` and result key
- **`criteria`** → GEval `criteria` (what the judge evaluates)
- **`steps`** → GEval `evaluation_steps` (chain-of-thought steps)
- **`short_def`**, **`description`**, **`icon`**, **`color`** → Used by the UI in `styles.build_metric_cards_html()` and `build_results_html()`

So: **one source of truth** in `evaluator.py` for both DeepEval and the UI.

---

## UI Wireframe

```
+-------------------------------------------------------------------------------+
|                         PromptAnalyzer                                        |
|  Evaluate your LLM prompts on Clarity, Specificity, Completeness,             |
|  Coherence, and Safety using DeepEval's G-Eval metrics.                       |
+----------------+----------------------------------------------------------------+
|  SIDEBAR       |  [Evaluate]  [Settings]                                      |
|                |--------------------------------------------------------------|
| +------------+ |                                                              |
| |Prompt      | |  +---------------------+   +-----------------------------+   |
| |Library     | |  | Prompt Title [____]  |   |  Evaluation Results         |   |
| |            | |  |                      |   |                             |   |
| | [Dropdown] | |  | Prompt Text          |   |  +---+                     |   |
| | v select   | |  | +------------------+ |   |  |72%| Overall Score        |   |
| |            | |  | |                  | |   |  +---+ Provider: OpenAI      |   |
| | [Load]     | |  | |   (8 lines)     | |   |                             |   |
| | [Delete]   | |  | |                  | |   |  Clarity        ********  78%|   |
| |            | |  | +------------------+ |   |  (check) Clear language...  |   |
| +------------+ |  |                      |   |                             |   |
|                |  | Category [general v] |   |  Specificity    ****    52%|   |
|                |  | Provider (.) OpenAI  |   |  (warn) Could add constraints|   |
|                |  |          ( ) Anthro  |   |                             |   |
|                |  |                      |   |  Completeness   ******  80%|   |
|                |  | [Evaluate] [Save]    |   |  (check) Sufficient context |   |
|                |  +---------------------+   |                             |   |
|                |                            |  Coherence      ******* 90%|   |
|                |                            |  Safety         ********98%|   |
|                |                            +-----------------------------+   |
+----------------+----------------------------------------------------------------+
```

### Score Indicators

| Score Range | Color  | Icon |
|-------------|--------|------|
| >= 80%      | Green  | (check) |
| 50-79%      | Yellow | (warn) |
| < 50%       | Red    | (cross) |

---

## Quick Start

### Prerequisites

- Python >= 3.10 (uv will use or install a compatible Python)
- **uv** — install once using the scripts below, or see [Installation](https://docs.astral.sh/uv/getting-started/installation/)

### Run with scripts (Windows / Mac / Ubuntu)

| Platform   | Command |
|------------|--------|
| **macOS / Linux / Ubuntu** | `./run.sh` |
| **Windows**                | `run.bat` (double-click or run from Command Prompt/PowerShell) |

- **First time:** The script installs uv (if missing), runs `uv sync` (creates `.venv` and installs deps), then starts the app.
- **Next times:** Same command — syncs if needed and starts the app. No need to activate `.venv`; `uv run` uses it.

Optional — install uv only: `./install_uv.sh` (Mac/Linux) or `install_uv.bat` (Windows).

### Install & Run (manual)

```bash
cd PromptAnalyzer
uv sync
uv run python app.py
```

The app will be available at **http://localhost:7860**.

### First-Time Setup

1. Open the app and go to the **Settings** tab.
2. Enter your **OpenAI** and/or **Anthropic** API key.
3. Click **Save API Keys** — they will be stored in `.env` and auto-loaded on restart.

### Usage

1. **Cursor Prompts** tab: pick a template (e.g. Jira TC Generator), fill fields, click **Generate Prompt**, then **Evaluate Prompt** or **Refine Prompt**.
2. **Write New Prompt** tab: type a prompt, choose category and provider, click **Evaluate Prompt** or **Refine Prompt**.
3. **Evaluate Prompt** -> calls `evaluator.run_evaluation()` -> DeepEval GEval scores the prompt.
4. **Refine Prompt** -> calls `evaluator.refine_prompt()` -> OpenAI/Anthropic returns issues + improved prompt (no DeepEval).
5. Save prompts via **Save to My Prompts**; load/delete from the sidebar.

---

## Evaluation Metrics

All metrics use DeepEval's **GEval** (LLM-as-a-judge with chain-of-thought). Definitions live in **`evaluator.METRIC_DEFS`** and drive both GEval and the UI:

| Metric         | What It Measures |
|----------------|------------------|
| **Clarity**    | Unambiguous, precise language that an LLM can interpret without guessing intent |
| **Specificity**| Concrete constraints, format requirements, and scope-narrowing details |
| **Completeness**| All necessary context provided — no follow-up questions needed |
| **Coherence**  | Logical structure, ordering of instructions, no contradictions |
| **Safety**     | Absence of harmful, unethical, or jailbreak content |

---

## Project Structure

```
PromptAnalyzer/
├── app.py            # Gradio app: UI, events, calls evaluator.run_evaluation / refine_prompt
├── evaluator.py      # DeepEval: METRIC_DEFS, run_evaluation(), refine_prompt(), GEval + LLMTestCase
├── styles.py         # CSS and HTML for results, refinement cards, metric definitions
├── prompt_library.py # Predefined templates (Cursor Workflow, Analysis)
├── run.sh            # Run app on macOS / Linux / Ubuntu (installs uv if needed, then uv sync + run)
├── run.bat           # Run app on Windows (installs uv if needed, then uv sync + run)
├── install_uv.sh     # Optional: install uv only (Mac/Linux)
├── install_uv.bat    # Optional: install uv only (Windows)
├── pyproject.toml    # Dependencies: gradio, deepeval, openai, anthropic, python-dotenv
├── README.md         # This file
├── prompts.json      # Auto-generated prompt storage
└── .env              # Auto-generated API key storage (git-ignored)
```

---

## Summary: DeepEval Call Chain

1. User clicks **Evaluate Prompt** (template tab or write-new tab).
2. **`app.py`** builds the prompt (template + inputs or raw text), then calls **`evaluator.run_evaluation(prompt, provider, model)`**.
3. **`evaluator.run_evaluation()`** checks API key, resolves model, creates **`LLMTestCase(input=prompt, actual_output=prompt)`**, builds **five `GEval` metrics** from `METRIC_DEFS`, and runs **`metric.measure(test_case)`** for each (each call uses the chosen LLM to score the prompt).
4. **`evaluator`** returns `{ "Clarity": { score, reason, passed }, ... }`.
5. **`app.py`** passes that dict to **`styles.build_results_html()`** and displays the result panel.

Refinement does **not** use DeepEval; it uses **`evaluator.refine_prompt()`**, which calls OpenAI or Anthropic directly with a system prompt that asks for issues, a refined prompt, and a "what changed" section.

---

## License

MIT
