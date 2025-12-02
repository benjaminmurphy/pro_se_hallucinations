"""Scenario hydration - generate background info from raw fact patterns."""

import json
import re
from pathlib import Path
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from .models import (
    ComplaintCategory,
    CustodyBackgroundInformation,
    HousingBackgroundInformation,
    Jurisdiction,
    NegligenceBackgroundInformation,
    Scenario,
)

T = TypeVar("T", bound=BaseModel)
_client = OpenAI()

# =============================================================================
# Hydration prompts for each category
# =============================================================================

HOUSING_HYDRATION_PROMPT = """You are assisting in creating evaluation data for an experiment evaluating model usefulness for pro se litigants. You will be given a description of a landlord-tenant dispute, and must generate the necessary background information to allow a model to draft a complaint for breach of the covenant of quiet enjoyment.

Be concise, and do not include more information than needed to enable a different model to draft a complaint. You should make up any names, dates, addresses, or monetary amounts needed. Use realistic Massachusetts locations and courts.

IMPORTANT: Generate UNIQUE and DIVERSE names, addresses, dates, and amounts. Vary the demographics, neighborhoods, and specific details each time. Do not reuse the same names or details across different requests."""

NEGLIGENCE_HYDRATION_PROMPT = """You are assisting in creating evaluation data for an experiment evaluating model usefulness for pro se litigants. You will be given a description of an incident where someone was injured due to another's negligence, and must generate the necessary background information to allow a model to draft a negligence complaint.

Be concise, and do not include more information than needed to enable a different model to draft a complaint. You should make up any names, dates, addresses, or monetary amounts needed. Use realistic Massachusetts locations and courts.

IMPORTANT: Generate UNIQUE and DIVERSE names, addresses, dates, and amounts. Vary the demographics, neighborhoods, and specific details each time. Do not reuse the same names or details across different requests."""

CUSTODY_HYDRATION_PROMPT = """You are assisting in creating evaluation data for an experiment evaluating model usefulness for pro se litigants. You will be given a description of a custody situation where a parent wants to modify an existing custody order, and must generate the necessary background information to allow a model to draft a Complaint for Modification of custody.

Be concise, and do not include more information than needed to enable a different model to draft a complaint. You should make up any names, dates, and court information needed. Use realistic Massachusetts Probate and Family Court venues.

IMPORTANT: Generate UNIQUE and DIVERSE names, dates, and details. Vary the demographics and specific details each time. Do not reuse the same names or details across different requests."""


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in a fact pattern.

    Removes leading/trailing whitespace, collapses multiple spaces,
    and joins lines properly.
    """
    # Split into lines, strip each line, filter empty lines
    lines = [line.strip() for line in text.strip().split("\n")]
    lines = [line for line in lines if line]
    # Join with single spaces, collapse multiple spaces
    result = " ".join(lines)
    result = re.sub(r"\s+", " ", result)
    return result


# =============================================================================
# Category-specific hydration functions
# =============================================================================


def _hydrate_scenario(
    fact_pattern: str,
    background_model: Type[T],
    prompt: str,
    model: str = "gpt-5-mini",
) -> T:
    """Generic hydration function for any scenario type."""
    response = _client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": fact_pattern},
        ],
        text_format=background_model,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to hydrate scenario - no parsed output")

    return response.output_parsed


def generate_housing_scenarios(
    fact_patterns: list[str],
    output_path: Path = Path("scenarios/housing.jsonl"),
    model: str = "gpt-5-mini",
    num_variants: int = 10,
) -> list[Scenario]:
    """Generate hydrated housing/quiet enjoyment scenarios.

    Args:
        fact_patterns: List of raw fact pattern strings
        output_path: Path to save JSONL output
        model: OpenAI model to use
        num_variants: Number of variants to generate per fact pattern
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenarios = []

    with open(output_path, "w") as f:
        for i, raw_fact_pattern in enumerate(fact_patterns):
            fact_pattern = normalize_whitespace(raw_fact_pattern)
            base_id = f"qe_{i + 1:03d}"

            for v in range(num_variants):
                scenario_id = f"{base_id}_{v + 1:02d}"
                print(f"Hydrating {scenario_id}...")

                background = _hydrate_scenario(
                    fact_pattern,
                    HousingBackgroundInformation,
                    HOUSING_HYDRATION_PROMPT,
                    model,
                )

                scenario = Scenario(
                    id=scenario_id,
                    category=ComplaintCategory.LANDLORD_TENANT,
                    jurisdiction=Jurisdiction.MA_STATE,
                    fact_pattern=fact_pattern,
                    housing_background_info=background,
                    custody_background_info=None,
                    negligence_background_info=None,
                )
                scenarios.append(scenario)

                record = {
                    "id": scenario_id,
                    "category": "landlord_tenant",
                    "fact_pattern": fact_pattern,
                    "background": background.model_dump(),
                }
                f.write(json.dumps(record) + "\n")

                print(f"  {background.plaintiff_name} v. {background.defendant_name}")

    print(f"\nSaved {len(scenarios)} housing scenarios to {output_path}")
    return scenarios


def generate_negligence_scenarios(
    fact_patterns: list[str],
    output_path: Path = Path("scenarios/negligence.jsonl"),
    model: str = "gpt-5-mini",
    num_variants: int = 10,
) -> list[Scenario]:
    """Generate hydrated negligence/personal injury scenarios.

    Args:
        fact_patterns: List of raw fact pattern strings
        output_path: Path to save JSONL output
        model: OpenAI model to use
        num_variants: Number of variants to generate per fact pattern
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenarios = []

    with open(output_path, "w") as f:
        for i, raw_fact_pattern in enumerate(fact_patterns):
            fact_pattern = normalize_whitespace(raw_fact_pattern)
            base_id = f"ng_{i + 1:03d}"

            for v in range(num_variants):
                scenario_id = f"{base_id}_{v + 1:02d}"
                print(f"Hydrating {scenario_id}...")

                background = _hydrate_scenario(
                    fact_pattern,
                    NegligenceBackgroundInformation,
                    NEGLIGENCE_HYDRATION_PROMPT,
                    model,
                )

                scenario = Scenario(
                    id=scenario_id,
                    category=ComplaintCategory.NEGLIGENCE,
                    jurisdiction=Jurisdiction.MA_STATE,
                    fact_pattern=fact_pattern,
                    negligence_background_info=background,
                    housing_background_info=None,
                    custody_background_info=None,
                )
                scenarios.append(scenario)

                record = {
                    "id": scenario_id,
                    "category": "negligence",
                    "fact_pattern": fact_pattern,
                    "background": background.model_dump(),
                }
                f.write(json.dumps(record) + "\n")

                print(f"  {background.plaintiff_name} v. {background.defendant_name}")

    print(f"\nSaved {len(scenarios)} negligence scenarios to {output_path}")
    return scenarios


def generate_custody_scenarios(
    fact_patterns: list[str],
    output_path: Path = Path("scenarios/custody.jsonl"),
    model: str = "gpt-5-mini",
    num_variants: int = 10,
) -> list[Scenario]:
    """Generate hydrated custody modification scenarios.

    Args:
        fact_patterns: List of raw fact pattern strings
        output_path: Path to save JSONL output
        model: OpenAI model to use
        num_variants: Number of variants to generate per fact pattern
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenarios = []

    with open(output_path, "w") as f:
        for i, raw_fact_pattern in enumerate(fact_patterns):
            fact_pattern = normalize_whitespace(raw_fact_pattern)
            base_id = f"cm_{i + 1:03d}"

            for v in range(num_variants):
                scenario_id = f"{base_id}_{v + 1:02d}"
                print(f"Hydrating {scenario_id}...")

                background = _hydrate_scenario(
                    fact_pattern,
                    CustodyBackgroundInformation,
                    CUSTODY_HYDRATION_PROMPT,
                    model,
                )

                scenario = Scenario(
                    id=scenario_id,
                    category=ComplaintCategory.CUSTODY_MODIFICATION,
                    jurisdiction=Jurisdiction.MA_STATE,
                    fact_pattern=fact_pattern,
                    custody_background_info=background,
                    negligence_background_info=None,
                    housing_background_info=None,
                )
                scenarios.append(scenario)

                record = {
                    "id": scenario_id,
                    "category": "custody_modification",
                    "fact_pattern": fact_pattern,
                    "background": background.model_dump(),
                }
                f.write(json.dumps(record) + "\n")

                print(f"  {background.petitioner_name} v. {background.respondent_name}")

    print(f"\nSaved {len(scenarios)} custody scenarios to {output_path}")
    return scenarios


# =============================================================================
# Loading functions
# =============================================================================


def load_housing_scenarios(
    path: Path = Path("scenarios/housing.jsonl"),
) -> list[Scenario]:
    """Load hydrated housing scenarios from JSONL file."""
    scenarios = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            background = HousingBackgroundInformation(**record["background"])
            scenario = Scenario(
                id=record["id"],
                category=ComplaintCategory.LANDLORD_TENANT,
                jurisdiction=Jurisdiction.MA_STATE,
                fact_pattern=record["fact_pattern"],
                housing_background_info=background,
                custody_background_info=None,
                negligence_background_info=None,
            )
            scenarios.append(scenario)
    return scenarios


def load_negligence_scenarios(
    path: Path = Path("scenarios/negligence.jsonl"),
) -> list[Scenario]:
    """Load hydrated negligence scenarios from JSONL file."""
    scenarios = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            background = NegligenceBackgroundInformation(**record["background"])
            scenario = Scenario(
                id=record["id"],
                category=ComplaintCategory.NEGLIGENCE,
                jurisdiction=Jurisdiction.MA_STATE,
                fact_pattern=record["fact_pattern"],
                negligence_background_info=background,
                housing_background_info=None,
                custody_background_info=None,
            )
            scenarios.append(scenario)
    return scenarios


def load_custody_scenarios(
    path: Path = Path("scenarios/custody.jsonl"),
) -> list[Scenario]:
    """Load hydrated custody scenarios from JSONL file."""
    scenarios = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            background = CustodyBackgroundInformation(**record["background"])
            scenario = Scenario(
                id=record["id"],
                category=ComplaintCategory.CUSTODY_MODIFICATION,
                jurisdiction=Jurisdiction.MA_STATE,
                fact_pattern=record["fact_pattern"],
                custody_background_info=background,
                negligence_background_info=None,
                housing_background_info=None,
            )
            scenarios.append(scenario)
    return scenarios


def load_all_scenarios() -> list[Scenario]:
    """Load all hydrated scenarios from all category files."""
    scenarios = []

    for loader, path in [
        (load_housing_scenarios, Path("scenarios/housing.jsonl")),
        (load_negligence_scenarios, Path("scenarios/negligence.jsonl")),
        (load_custody_scenarios, Path("scenarios/custody.jsonl")),
    ]:
        if path.exists():
            scenarios.extend(loader(path))

    return scenarios
