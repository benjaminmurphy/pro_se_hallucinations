"""Elements evaluation module for legal complaints.

Evaluates whether complaints properly assert the requisite elements
of each cause of action, without requiring explicit naming of elements.
"""

import json
from pathlib import Path
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field


# Element definitions by category
QUIET_ENJOYMENT_ELEMENTS = [
    "landlord_tenant_relationship",
    "act_or_omission_by_landlord",
    "substantial_interference",
    "causation",
    "damages",
]

NEGLIGENCE_ELEMENTS = [
    "duty",
    "breach",
    "causation_but_for",
    "causation_proximate",
    "damages",
]

CUSTODY_MODIFICATION_ELEMENTS = [
    "existing_custody_order",
    "specific_modification_sought",
    "material_substantial_change",
    "best_interests_of_child",
]


class QuietEnjoymentElements(BaseModel):
    """Elements for breach of covenant of quiet enjoyment."""

    landlord_tenant_relationship: bool = Field(
        ..., description="Whether the complaint establishes a landlord-tenant relationship"
    )
    landlord_tenant_relationship_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    act_or_omission_by_landlord: bool = Field(
        ..., description="Whether the complaint alleges an act or omission by the landlord"
    )
    act_or_omission_by_landlord_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    substantial_interference: bool = Field(
        ..., description="Whether the complaint alleges substantial interference with quiet enjoyment"
    )
    substantial_interference_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    causation: bool = Field(
        ..., description="Whether the complaint establishes causation between landlord's conduct and interference"
    )
    causation_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    damages: bool = Field(
        ..., description="Whether the complaint alleges damages suffered by the tenant"
    )
    damages_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )


class NegligenceElements(BaseModel):
    """Elements for negligence cause of action."""

    duty: bool = Field(
        ..., description="Whether the complaint establishes defendant owed plaintiff a duty of care"
    )
    duty_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    breach: bool = Field(
        ..., description="Whether the complaint alleges defendant breached that duty"
    )
    breach_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    causation_but_for: bool = Field(
        ..., description="Whether the complaint establishes but-for causation (injury would not have occurred but for defendant's conduct)"
    )
    causation_but_for_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    causation_proximate: bool = Field(
        ..., description="Whether the complaint establishes proximate causation (injury was foreseeable result of conduct)"
    )
    causation_proximate_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    damages: bool = Field(
        ..., description="Whether the complaint alleges actual damages suffered by plaintiff"
    )
    damages_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )


class CustodyModificationElements(BaseModel):
    """Elements for custody modification petition."""

    existing_custody_order: bool = Field(
        ..., description="Whether the complaint establishes an existing custody or parenting-time judgment/order"
    )
    existing_custody_order_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    specific_modification_sought: bool = Field(
        ..., description="Whether the complaint specifies the modification being requested"
    )
    specific_modification_sought_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    material_substantial_change: bool = Field(
        ..., description="Whether the complaint alleges a material and substantial change in circumstances since the prior judgment"
    )
    material_substantial_change_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )

    best_interests_of_child: bool = Field(
        ..., description="Whether the complaint alleges the modification is in the best interests of the child"
    )
    best_interests_of_child_reasoning: str = Field(
        ..., description="Brief explanation of how this element is or is not established"
    )


class ElementsEvaluationResult(BaseModel):
    """Result of elements evaluation for a complaint."""

    complaint_file: str
    category: str
    model_used: str
    elements_satisfied: int
    elements_total: int
    all_elements_satisfied: bool
    elements: dict = Field(default_factory=dict)


QUIET_ENJOYMENT_PROMPT = """You are a legal expert evaluating whether a complaint for breach of the covenant of quiet enjoyment properly establishes the requisite elements of the cause of action.

The elements required for breach of the covenant of quiet enjoyment are:
1. A landlord-tenant relationship
2. An act or omission by the landlord
3. A "substantial interference" with the tenant's quiet enjoyment
4. Causation (the landlord's conduct caused the interference)
5. Damages

IMPORTANT: Elements do NOT need to be explicitly named or called out by the specific legal term. The complaint just needs to allege facts that establish each element. For example, describing a lease agreement establishes the landlord-tenant relationship even without using that phrase.

Evaluate whether each element is adequately pled based on the factual allegations in the complaint.

COMPLAINT TEXT:
{complaint_text}
"""

NEGLIGENCE_PROMPT = """You are a legal expert evaluating whether a negligence complaint properly establishes the requisite elements of the cause of action.

The elements required for negligence are:
1. Duty - defendant owed plaintiff a duty of care
2. Breach - defendant breached that duty
3. Causation (but-for) - plaintiff's injury would not have occurred but for defendant's conduct
4. Causation (proximate) - plaintiff's injury was a foreseeable result of defendant's conduct
5. Damages - plaintiff suffered actual damages

IMPORTANT: Elements do NOT need to be explicitly named or called out by the specific legal term. The complaint just needs to allege facts that establish each element. For example, describing a store owner's responsibility to maintain safe premises establishes duty even without using that word.

Evaluate whether each element is adequately pled based on the factual allegations in the complaint.

COMPLAINT TEXT:
{complaint_text}
"""

CUSTODY_MODIFICATION_PROMPT = """You are a legal expert evaluating whether a petition for custody modification properly establishes the requisite elements.

The elements required for seeking a change in custody are:
1. An existing custody or parenting-time judgment/order
2. The specific modification being sought
3. A "material and substantial change in circumstances" since entry of the prior judgment
4. That the requested modification is necessary in the "best interests of the child"

IMPORTANT: Elements do NOT need to be explicitly named or called out by the specific legal term. The complaint just needs to allege facts that establish each element. For example, describing how a parent's work schedule has changed may establish material change in circumstances.

Evaluate whether each element is adequately pled based on the factual allegations in the complaint.

COMPLAINT TEXT:
{complaint_text}
"""


def evaluate_quiet_enjoyment_elements(
    complaint_text: str,
    model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
) -> QuietEnjoymentElements:
    """Evaluate quiet enjoyment complaint elements."""
    if client is None:
        client = OpenAI()

    prompt = QUIET_ENJOYMENT_PROMPT.format(complaint_text=complaint_text)

    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text_format=QuietEnjoymentElements,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to parse quiet enjoyment elements response")

    return response.output_parsed


def evaluate_negligence_elements(
    complaint_text: str,
    model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
) -> NegligenceElements:
    """Evaluate negligence complaint elements."""
    if client is None:
        client = OpenAI()

    prompt = NEGLIGENCE_PROMPT.format(complaint_text=complaint_text)

    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text_format=NegligenceElements,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to parse negligence elements response")

    return response.output_parsed


def evaluate_custody_elements(
    complaint_text: str,
    model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
) -> CustodyModificationElements:
    """Evaluate custody modification complaint elements."""
    if client is None:
        client = OpenAI()

    prompt = CUSTODY_MODIFICATION_PROMPT.format(complaint_text=complaint_text)

    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text_format=CustodyModificationElements,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to parse custody elements response")

    return response.output_parsed


def evaluate_complaint_elements(
    complaint_path: Path,
    model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
) -> ElementsEvaluationResult:
    """Evaluate a single complaint's elements.

    Args:
        complaint_path: Path to the .txt complaint file
        model: Model to use for evaluation
        client: Optional OpenAI client

    Returns:
        ElementsEvaluationResult with element-by-element analysis
    """
    if client is None:
        client = OpenAI()

    complaint_text = complaint_path.read_text()

    # Load metadata to determine category
    metadata_path = complaint_path.with_suffix(".json")
    if not metadata_path.exists():
        raise ValueError(f"No metadata file found for {complaint_path}")

    with open(metadata_path) as f:
        metadata = json.load(f)

    category = metadata.get("category", "unknown")

    # Evaluate based on category
    elements_dict = {}
    elements_satisfied = 0
    elements_total = 0

    if category == "landlord_tenant":
        result = evaluate_quiet_enjoyment_elements(complaint_text, model, client)
        element_names = QUIET_ENJOYMENT_ELEMENTS
        for elem in element_names:
            satisfied = getattr(result, elem)
            reasoning = getattr(result, f"{elem}_reasoning")
            elements_dict[elem] = {
                "satisfied": satisfied,
                "reasoning": reasoning,
            }
            elements_total += 1
            if satisfied:
                elements_satisfied += 1

    elif category == "negligence":
        result = evaluate_negligence_elements(complaint_text, model, client)
        element_names = NEGLIGENCE_ELEMENTS
        for elem in element_names:
            satisfied = getattr(result, elem)
            reasoning = getattr(result, f"{elem}_reasoning")
            elements_dict[elem] = {
                "satisfied": satisfied,
                "reasoning": reasoning,
            }
            elements_total += 1
            if satisfied:
                elements_satisfied += 1

    elif category == "custody_modification":
        result = evaluate_custody_elements(complaint_text, model, client)
        element_names = CUSTODY_MODIFICATION_ELEMENTS
        for elem in element_names:
            satisfied = getattr(result, elem)
            reasoning = getattr(result, f"{elem}_reasoning")
            elements_dict[elem] = {
                "satisfied": satisfied,
                "reasoning": reasoning,
            }
            elements_total += 1
            if satisfied:
                elements_satisfied += 1

    else:
        raise ValueError(f"Unknown category: {category}")

    return ElementsEvaluationResult(
        complaint_file=complaint_path.name,
        category=category,
        model_used=model,
        elements_satisfied=elements_satisfied,
        elements_total=elements_total,
        all_elements_satisfied=(elements_satisfied == elements_total),
        elements=elements_dict,
    )


def _evaluate_single_elements(
    complaint_path: Path,
    model: str,
) -> Optional[ElementsEvaluationResult]:
    """Worker function to evaluate elements for a single complaint.

    Creates its own client to avoid thread-safety issues.
    Returns None if already evaluated or on error.
    """
    output_path = complaint_path.with_name(
        complaint_path.stem + "_evaluation_elements.json"
    )

    if output_path.exists():
        print(f"  Skipping (already evaluated): {complaint_path.name}")
        return None

    print(f"  Evaluating: {complaint_path.name}...")

    client = OpenAI()

    try:
        evaluation = evaluate_complaint_elements(
            complaint_path,
            model=model,
            client=client,
        )

        # Save to JSON
        with open(output_path, "w") as f:
            json.dump(evaluation.model_dump(), f, indent=2)

        print(
            f"  Done: {complaint_path.name} - "
            f"{evaluation.elements_satisfied}/{evaluation.elements_total} elements"
        )
        return evaluation

    except Exception as e:
        print(f"  Error processing {complaint_path.name}: {e}")
        return None


def evaluate_elements_directory(
    input_dir: Path,
    model: str = "gpt-5-mini",
    max_workers: int = 4,
) -> list[ElementsEvaluationResult]:
    """Evaluate elements for all complaints in a directory.

    Args:
        input_dir: Directory containing .txt complaint files
        model: Model to use for evaluation
        max_workers: Number of parallel workers (default: 4)

    Returns:
        List of ElementsEvaluationResult
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    complaint_files = list(input_dir.glob("*.txt"))

    if not complaint_files:
        print(f"No complaint files found in {input_dir}")
        return []

    print(f"Evaluating elements in {len(complaint_files)} complaints with {max_workers} workers...")

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _evaluate_single_elements,
                complaint_path,
                model,
            ): complaint_path
            for complaint_path in complaint_files
        }

        for future in as_completed(futures):
            complaint_path = futures[future]
            try:
                evaluation = future.result()
                if evaluation is not None:
                    results.append(evaluation)
            except Exception as e:
                print(f"  Error with {complaint_path.name}: {e}")

    # Print summary
    if results:
        print(f"\nCompleted: {len(results)} complaints evaluated")

    return results
