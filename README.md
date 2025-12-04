# CS2881 Final Project: Sure, I Can Draft a Complaint! LLM Hallucination in Pro Se Litigation

Evaluates how well LLMs assist self-represented litigants in drafting legal complaints, with a focus on detecting citation hallucination and verifying that cited cases actually support their claimed propositions. See paper for full details.

## Setup

```bash
# Install dependencies
uv sync

# Configure API keys in .env
OPENAI_API_KEY=...
COURTLISTENER_API_TOKEN=...
```

## Pipeline

### 1. Hydrate: Generate scenario variants from fact patterns

```bash
python main.py hydrate --category all
python main.py hydrate --category housing --variants 5
```

Enriches raw fact patterns in `scenarios/fact_patterns.py` with realistic background information. Outputs to `scenarios/*.jsonl`.

### 2. Generate: Create complaints from scenarios

```bash
python main.py generate --category all --model gpt-4o
```

Generates legal complaints for each hydrated scenario. Outputs to `data/complaints/{model}/`.

### 3. Evaluate: Validate citations and check proposition support

```bash
python main.py evaluate --input data/complaints/gpt-4o-2024-11-20
```

For each complaint:
- Extracts citations with their supporting propositions
- Validates case citations against CourtListener
- Uses LLM to assess whether valid citations actually support their claimed propositions

Outputs `{complaint}_evaluation.json` files.

### 4. Evaluate Elements: Check cause of action elements

```bash
python main.py evaluate-elements --input data/complaints/gpt-4o-2024-11-20
```

Evaluates whether each complaint properly pleads the required elements for its cause of action.

Outputs `{complaint}_evaluation_elements.json` files.

## Analysis

Scripts in `analysis/` generate visualizations and reports:

```bash
cd analysis

# Run all analyses
uv run python run_all.py

# Or individually:
uv run python top_cases.py           # Top hallucinated/unsupported cases
uv run python hallucination_plots.py # Hallucination rate plots
uv run python support_plots.py       # Proposition support plots
```

Outputs saved to `analysis/output/`.

## Directory Structure

```
main.py                      # CLI entry point
- src/
  - models.py                # Pydantic data models
  - scenarios.py             # Scenario hydration
  - generation.py            # Complaint generation
  - citations.py             # Citation extraction
  - courtlistener.py         # CourtListener API client
  - evaluation.py            # Citation validation & support evaluation
  - elements_evaluation.py   # Cause of action elements evaluation
  - scenarios/
    - fact_patterns.py       # Raw fact pattern definitions
    - *.jsonl                # Hydrated scenarios
  - data/
    - complaints/{model}/    # Generated complaints & evaluations
    - cache/                 # CourtListener response cache
  - analysis/
    - load_data.py           # Shared data loading
    - top_cases.py           # Top hallucinated/unsupported cases
    - hallucination_plots.py # Hallucination rate visualizations
    - support_plots.py       # Support rate visualizations
    - output/                # Generated plots and reports
```

## Required Elements by Category

**Quiet Enjoyment:** Landlord-tenant relationship, act/omission by landlord, substantial interference, causation, damages

**Negligence:** Duty, breach, causation (but-for & proximate), damages

**Custody Modification:** Existing order, specific modification sought, material change in circumstances, best interests of child
