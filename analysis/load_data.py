"""Shared data loading utilities for analysis scripts."""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Map category values to display names
CATEGORY_DISPLAY_NAMES = {
    "custody_modification": "Family Law",
    "negligence": "Torts",
    "landlord_tenant": "Housing",
}


@dataclass
class CitationData:
    """Data for a single citation."""

    raw_text: str
    citation_type: str
    proposition: str
    is_valid: Optional[bool]
    case_name: Optional[str]
    supports_proposition: Optional[bool]
    support_confidence: Optional[str]
    support_reasoning: Optional[str]
    model: str
    category: str
    complaint_file: str


@dataclass
class ModelStats:
    """Aggregated statistics for a model."""

    model: str
    total_case_citations: int = 0
    valid_citations: int = 0
    invalid_citations: int = 0
    supported: int = 0
    unsupported: int = 0
    num_complaints: int = 0
    by_category: dict = field(default_factory=lambda: defaultdict(lambda: {
        "total_case_citations": 0,
        "valid_citations": 0,
        "invalid_citations": 0,
        "supported": 0,
        "unsupported": 0,
        "num_complaints": 0,
    }))


def load_all_evaluations(data_dir: Path) -> tuple[list[CitationData], dict[str, ModelStats]]:
    """Load all evaluation data from the complaints directory.

    Args:
        data_dir: Path to data/complaints directory

    Returns:
        Tuple of (list of all citations, dict of model -> ModelStats)
    """
    all_citations: list[CitationData] = []
    model_stats: dict[str, ModelStats] = {}

    # Iterate through model subdirectories
    for model_dir in sorted(data_dir.iterdir()):
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name
        stats = ModelStats(model=model_name)

        # Load all evaluation files
        for eval_file in model_dir.glob("*_evaluation.json"):
            # Skip elements evaluation files
            if "_evaluation_elements.json" in eval_file.name:
                continue

            with open(eval_file) as f:
                data = json.load(f)

            category = data.get("category", "unknown")
            complaint_file = data.get("complaint_file", "")

            # Track complaint count
            stats.num_complaints += 1
            stats.by_category[category]["num_complaints"] += 1

            for cit_key, cit_data in data.get("citations", {}).items():
                if cit_data.get("citation_type") != "case":
                    continue

                citation = CitationData(
                    raw_text=cit_data.get("raw_text", ""),
                    citation_type=cit_data.get("citation_type", ""),
                    proposition=cit_data.get("proposition", ""),
                    is_valid=cit_data.get("is_valid"),
                    case_name=cit_data.get("case_name"),
                    supports_proposition=cit_data.get("supports_proposition"),
                    support_confidence=cit_data.get("support_confidence"),
                    support_reasoning=cit_data.get("support_reasoning"),
                    model=model_name,
                    category=category,
                    complaint_file=complaint_file,
                )
                all_citations.append(citation)

                # Update stats
                stats.total_case_citations += 1
                stats.by_category[category]["total_case_citations"] += 1

                if citation.is_valid is True:
                    stats.valid_citations += 1
                    stats.by_category[category]["valid_citations"] += 1

                    if citation.supports_proposition is True:
                        stats.supported += 1
                        stats.by_category[category]["supported"] += 1
                    elif citation.supports_proposition is False:
                        stats.unsupported += 1
                        stats.by_category[category]["unsupported"] += 1

                elif citation.is_valid is False:
                    stats.invalid_citations += 1
                    stats.by_category[category]["invalid_citations"] += 1

        model_stats[model_name] = stats

    return all_citations, model_stats


def get_data_dir() -> Path:
    """Get the data/complaints directory path."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "data" / "complaints"


def get_output_dir() -> Path:
    """Get the analysis output directory path."""
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
