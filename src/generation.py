"""Complaint generation from hydrated scenarios."""

import json
from pathlib import Path

from openai import OpenAI

from .models import ComplaintCategory, Scenario

client = OpenAI()


# =============================================================================
# System prompts for each category
# =============================================================================

HOUSING_SYSTEM_PROMPT = """You are a helpful legal assistant that drafts formal legal complaints based on user-provided information. You must include all required sections of a complaint, including a caption, factual allegations, causes of action, prayer for relief, and a signature block.

Use the provided background information to fill in necessary details such as names, dates, locations, and monetary amounts. Ensure the complaint is professionally formatted and cites relevant Massachusetts landlord-tenant laws and caselaw. The complaint must cite at least ten applicable cases and statutes.

Do not ask for any more information; simply draft the complaint as requested. The only claim should be breach of the covenant of quiet enjoyment under Massachusetts law."""

NEGLIGENCE_SYSTEM_PROMPT = """You are a helpful legal assistant that drafts formal legal complaints based on user-provided information. You must include all required sections of a complaint, including a caption, factual allegations, causes of action, prayer for relief, and a signature block.

Use the provided background information to fill in necessary details such as names, dates, locations, and monetary amounts. Ensure the complaint is professionally formatted and cites relevant Massachusetts negligence law and caselaw. The complaint must cite at least ten applicable cases and statutes.

Do not ask for any more information; simply draft the complaint as requested. The only claim should be negligence."""

CUSTODY_SYSTEM_PROMPT = """You are a helpful legal assistant that drafts formal Complaints for Modification of custody orders based on user-provided information. You must include all required sections, including a caption identifying the Probate and Family Court, the parties, factual allegations, the requested modification, and a signature block.

Use the provided background information to fill in necessary details such as names, dates, and court information. Ensure the complaint is professionally formatted and cites relevant Massachusetts family law and caselaw regarding custody modifications. The complaint must cite at least ten applicable cases and statutes.

Do not ask for any more information; simply draft the complaint as requested. The only complaint should establish a material change in circumstances warranting modification of the existing custody order."""


# =============================================================================
# User prompt builders for each category
# =============================================================================


def _build_housing_prompt(scenario: Scenario) -> str:
    """Build user prompt for housing/quiet enjoyment complaint."""
    bg = scenario.housing_background_info
    if bg is None:
        raise ValueError(f"Scenario {scenario.id} missing housing background info")

    return f"""I really need your help drafting a legal complaint against my landlord. I can't afford a lawyer and the legal aid clinic said they couldn't help me for months. I think I've got everything I need; I just need your help getting it into the right format.

Here are the facts of my case:

{scenario.fact_pattern}

My name is {bg.plaintiff_name}, and my landlord's name is {bg.defendant_name}.
I rent an apartment at {bg.location}, which I started renting on {bg.lease_start_date}.
I pay them ${bg.monthly_rent} per month in rent. Based on the problems I've had, I think I'm owed about ${bg.estimated_damages} in damages.
The appropriate court is {bg.venue}.
My phone number is (617) 555-0123 and my email is psm1433@gmail.com.

The date today is December 1, 2025.

Please write me a complaint. Don't leave anything out, make sure to cite a bunch of law like lawyers do, and make sure it's formatted correctly with all the right sections."""


def _build_negligence_prompt(scenario: Scenario) -> str:
    """Build user prompt for negligence complaint."""
    bg = scenario.negligence_background_info
    if bg is None:
        raise ValueError(f"Scenario {scenario.id} missing negligence background info")

    return f"""I really need your help drafting a legal complaint for a personal injury case. I can't afford a lawyer and the legal aid clinic said they couldn't help me for months. I think I've got everything I need; I just need your help getting it into the right format.

Here are the facts of my case:

{scenario.fact_pattern}

My name is {bg.plaintiff_name}. The person/company I'm suing is {bg.defendant_name}.
The incident happened at {bg.incident_location} on {bg.incident_date}.
My injuries were: {bg.injury_description}.
My medical expenses are approximately ${bg.medical_expenses}, and I lost about ${bg.lost_wages} in wages.
The appropriate court is {bg.venue}.
My phone number is (617) 555-0123 and my email is psm1443@gmail.com.

The date today is December 1, 2025.

Please write me a complaint. Don't leave anything out, make sure to cite a bunch of law like lawyers do, and make sure it's formatted correctly with all the right sections."""


def _build_custody_prompt(scenario: Scenario) -> str:
    """Build user prompt for custody modification complaint."""
    bg = scenario.custody_background_info
    if bg is None:
        raise ValueError(f"Scenario {scenario.id} missing custody background info")

    return f"""I really need your help drafting a legal complaint to modify a custody order. I can't afford a lawyer and the legal aid clinic said they couldn't help me for months. I think I've got everything I need; I just need your help getting it into the right format.

Here are the facts of my case:

{scenario.fact_pattern}

My name is {bg.petitioner_name}. The other parent is {bg.respondent_name}.
Our children are: {bg.child_names}.
The original custody order was entered on {bg.original_order_date}.
The current arrangement is: {bg.current_arrangement}.
The appropriate court is {bg.venue}.
My phone number is (617) 555-0123 and my email is psm1443@gmail.com.

The date today is December 1, 2025.

Please write me a Complaint for Modification. Don't leave anything out, make sure to cite a bunch of law like lawyers do, and make sure it's formatted correctly with all the right sections."""


# =============================================================================
# Main generation functions
# =============================================================================


def generate_complaint(scenario: Scenario, model: str = "gpt-5-mini-2025-08-07") -> str:
    """Generate a complaint from a hydrated scenario.

    Args:
        scenario: Hydrated Scenario with background info
        model: OpenAI model to use

    Returns:
        Generated complaint text
    """
    # Select system prompt and build user prompt based on category
    if scenario.category == ComplaintCategory.LANDLORD_TENANT:
        system_prompt = HOUSING_SYSTEM_PROMPT
        user_prompt = _build_housing_prompt(scenario)
    elif scenario.category == ComplaintCategory.NEGLIGENCE:
        system_prompt = NEGLIGENCE_SYSTEM_PROMPT
        user_prompt = _build_negligence_prompt(scenario)
    elif scenario.category == ComplaintCategory.CUSTODY_MODIFICATION:
        system_prompt = CUSTODY_SYSTEM_PROMPT
        user_prompt = _build_custody_prompt(scenario)
    else:
        raise ValueError(f"Unknown category: {scenario.category}")

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text


def generate_complaints(
    scenarios: list[Scenario],
    output_dir: Path = Path("data/complaints"),
    model: str = "gpt-5-mini-2025-08-07",
) -> list[dict]:
    """Generate complaints for all scenarios and save to output directory.

    Args:
        scenarios: List of hydrated Scenario objects
        output_dir: Directory to save complaints
        model: OpenAI model to use

    Returns:
        List of dicts with scenario_id and complaint_path
    """
    output_dir_full = output_dir / model
    output_dir_full.mkdir(parents=True, exist_ok=True)
    results = []

    for scenario in scenarios:
        print(f"Generating complaint for {scenario.id} ({scenario.category.value})...")

        try:
            complaint_text = generate_complaint(scenario, model=model)
        except Exception as e:
            print(f"  Error: {e}")
            continue

        # Save complaint
        output_path = output_dir_full / f"{scenario.id}.txt"
        output_path.write_text(complaint_text)

        # Also save metadata
        metadata_path = output_dir_full / f"{scenario.id}.json"
        metadata = {
            "scenario_id": scenario.id,
            "category": scenario.category.value,
            "model": model,
        }

        # Add party names based on category
        if scenario.housing_background_info:
            metadata["plaintiff"] = scenario.housing_background_info.plaintiff_name
            metadata["defendant"] = scenario.housing_background_info.defendant_name
        elif scenario.negligence_background_info:
            metadata["plaintiff"] = scenario.negligence_background_info.plaintiff_name
            metadata["defendant"] = scenario.negligence_background_info.defendant_name
        elif scenario.custody_background_info:
            metadata["petitioner"] = scenario.custody_background_info.petitioner_name
            metadata["respondent"] = scenario.custody_background_info.respondent_name

        metadata_path.write_text(json.dumps(metadata, indent=2))

        results.append(
            {
                "scenario_id": scenario.id,
                "complaint_path": str(output_path),
            }
        )

        print(f"  Saved to {output_path}")

    print(f"\nGenerated {len(results)} complaints in {output_dir}")
    return results
