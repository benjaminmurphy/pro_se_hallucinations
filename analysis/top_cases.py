#!/usr/bin/env python
"""Identify top hallucinated and unsupported cases.

Outputs:
1. Top 20 most-cited hallucinated cases (is_valid=False)
2. Top 20 most-cited cases that don't support their proposition (is_valid=True, supports=False)
"""

import re
from collections import Counter
from pathlib import Path

from load_data import get_data_dir, get_output_dir, load_all_evaluations


def normalize_citation(raw_text: str) -> str:
    """Normalize a citation for deduplication.

    Extracts the core case name and reporter citation.
    """
    # Remove markdown formatting
    text = raw_text.replace("*", "").replace("_", "").strip()

    # Try to extract case name pattern: "Name v. Name"
    case_match = re.search(r"([A-Z][a-zA-Z\.\s]+\s+v\.\s+[A-Z][a-zA-Z\.\s]+)", text)
    if case_match:
        case_name = case_match.group(1).strip()
        # Also try to get the reporter citation
        reporter_match = re.search(r"(\d+\s+[A-Za-z\.\s]+\d+)", text)
        if reporter_match:
            return f"{case_name}, {reporter_match.group(1).strip()}"
        return case_name

    # Fall back to first 60 chars
    return text[:60]


def main():
    data_dir = get_data_dir()
    output_dir = get_output_dir()

    print(f"Loading data from {data_dir}...")
    all_citations, model_stats = load_all_evaluations(data_dir)

    # Count hallucinated cases (is_valid=False)
    hallucinated_counter: Counter = Counter()
    hallucinated_examples: dict[str, list[str]] = {}

    # Count unsupported cases (is_valid=True, supports=False)
    unsupported_counter: Counter = Counter()
    unsupported_examples: dict[str, list[str]] = {}

    for cit in all_citations:
        normalized = normalize_citation(cit.raw_text)

        if cit.is_valid is False:
            hallucinated_counter[normalized] += 1
            if normalized not in hallucinated_examples:
                hallucinated_examples[normalized] = []
            hallucinated_examples[normalized].append(
                f"  - Model: {cit.model}, File: {cit.complaint_file}"
            )

        elif cit.is_valid is True and cit.supports_proposition is False:
            unsupported_counter[normalized] += 1
            if normalized not in unsupported_examples:
                unsupported_examples[normalized] = []
            unsupported_examples[normalized].append(
                f"  - Model: {cit.model}, Proposition: {cit.proposition[:100]}..."
            )

    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("TOP 20 MOST-CITED HALLUCINATED CASES")
    report_lines.append("(Citations to non-existent cases)")
    report_lines.append("=" * 80)
    report_lines.append("")

    for i, (case, count) in enumerate(hallucinated_counter.most_common(20), 1):
        report_lines.append(f"{i:2}. [{count} citations] {case}")
        # Show up to 3 examples
        for example in hallucinated_examples[case][:3]:
            report_lines.append(example)
        report_lines.append("")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("TOP 20 MOST-CITED UNSUPPORTED CASES")
    report_lines.append("(Real cases that don't support their cited proposition)")
    report_lines.append("=" * 80)
    report_lines.append("")

    for i, (case, count) in enumerate(unsupported_counter.most_common(20), 1):
        report_lines.append(f"{i:2}. [{count} citations] {case}")
        # Show up to 3 examples
        for example in unsupported_examples[case][:3]:
            report_lines.append(example)
        report_lines.append("")

    # Summary stats
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 80)
    report_lines.append(f"Total case citations analyzed: {len(all_citations)}")
    report_lines.append(f"Unique hallucinated cases: {len(hallucinated_counter)}")
    report_lines.append(f"Total hallucinated citations: {sum(hallucinated_counter.values())}")
    report_lines.append(f"Unique unsupported cases: {len(unsupported_counter)}")
    report_lines.append(f"Total unsupported citations: {sum(unsupported_counter.values())}")

    report = "\n".join(report_lines)

    # Print to console
    print(report)

    # Save to file
    output_file = output_dir / "top_cases_report.txt"
    with open(output_file, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
