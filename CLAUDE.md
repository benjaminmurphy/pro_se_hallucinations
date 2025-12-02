# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Pro Se Complaint Evaluation Framework** that evaluates how well LLMs assist self-represented litigants in drafting legal complaints, with a focus on detecting citation hallucination (citations to non-existent or misquoted cases/statutes).

**Complaint Categories:** Housing (Quiet Enjoyment), Negligence, Custody Modification
**Jurisdiction:** Massachusetts (state and federal courts)

## Commands

```bash
# Install dependencies
uv sync

# Three-stage pipeline:

# Stage 1: Hydrate - enrich fact patterns with background info
python main.py hydrate --category all              # all categories
python main.py hydrate --category housing --variants 5  # specific category

# Stage 2: Generate - create complaints from hydrated scenarios
python main.py generate --category all --output data/complaints
python main.py generate --category negligence --model gpt-4o

# Stage 3: Extract - extract citations from complaints
python main.py extract --input data/complaints

# Run tests
pytest
pytest --cov=src --cov-report=html
```

## Architecture

```
Raw Fact Patterns → [HYDRATE] → Hydrated Scenarios (JSONL)
                                       ↓
                               [GENERATE]
                                       ↓
                               Complaints (Text)
                                       ↓
                               [EXTRACT]
                                       ↓
                               Citations (Validated via CourtListener)
```

### Key Components

- **`main.py`** - CLI entry point with `hydrate`, `generate`, `extract` commands
- **`src/models.py`** - Pydantic models: `Scenario`, `Citation`, `Complaint`, `EvaluationResult`, and category-specific background info classes
- **`src/scenarios.py`** - Scenario hydration using OpenAI API
- **`src/generation.py`** - Complaint generation with category-specific prompts
- **`src/citations.py`** - Citation extraction using structured LLM output
- **`src/courtlistener.py`** - Citation validation against CourtListener API with disk caching
- **`scenarios/fact_patterns.py`** - Raw fact pattern definitions
- **`scenarios/*.jsonl`** - Generated hydrated scenarios

### Data Models

`ComplaintCategory` enum: `LANDLORD_TENANT`, `NEGLIGENCE`, `CUSTODY_MODIFICATION`

Each category has its own `*BackgroundInformation` class with category-specific fields (parties, dates, damages, venues).

## External APIs

- **OpenAI API** (`OPENAI_API_KEY`): GPT models for hydration, generation, extraction
- **CourtListener API** (`COURTLISTENER_API_TOKEN`): Citation validation against real court opinions

## Environment

- Python 3.12 required
- Uses `uv` package manager
- API keys in `.env` file
