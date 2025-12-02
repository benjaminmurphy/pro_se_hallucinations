"""Pro Se Complaint Evaluation Framework

Pipeline:
1. hydrate  - Generate background info from raw fact patterns → JSONL
2. generate - Generate complaints from hydrated scenarios
3. extract  - Extract citations from generated complaints
4. evaluate - Validate citations and check proposition support
5. evaluate-elements - Check if complaints assert required elements

Usage:
    python main.py hydrate --category all
    python main.py generate --category housing
    python main.py extract
    python main.py evaluate --input data/complaints/gpt-4o-2024-11-20
    python main.py evaluate-elements --input data/complaints/gpt-4o-2024-11-20
"""

import argparse
from pathlib import Path


def cmd_hydrate(args):
    """Hydrate scenarios with background information."""
    from scenarios import (
        CUSTODY_MODIFICATION_SCENARIOS,
        NEGLIGENCE_SCENARIOS,
        QUIET_ENJOYMENT_SCENARIOS,
    )
    from src.scenarios import (
        generate_custody_scenarios,
        generate_housing_scenarios,
        generate_negligence_scenarios,
    )

    category = args.category
    num_variants = args.variants

    if category in ("housing", "all"):
        print("=" * 60)
        print(f"HOUSING / QUIET ENJOYMENT SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_housing_scenarios(
            QUIET_ENJOYMENT_SCENARIOS, model=args.model, num_variants=num_variants
        )

    if category in ("negligence", "all"):
        print("\n" + "=" * 60)
        print(f"NEGLIGENCE SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_negligence_scenarios(
            NEGLIGENCE_SCENARIOS, model=args.model, num_variants=num_variants
        )

    if category in ("custody", "all"):
        print("\n" + "=" * 60)
        print(f"CUSTODY MODIFICATION SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_custody_scenarios(
            CUSTODY_MODIFICATION_SCENARIOS, model=args.model, num_variants=num_variants
        )


def cmd_generate(args):
    """Generate complaints from hydrated scenarios."""
    from src.generation import generate_complaints
    from src.scenarios import (
        load_all_scenarios,
        load_custody_scenarios,
        load_housing_scenarios,
        load_negligence_scenarios,
    )

    output_dir = Path(args.output)
    category = args.category

    if category == "all":
        print("Loading all scenarios...")
        scenarios = load_all_scenarios()
    elif category == "housing":
        print("Loading housing scenarios...")
        scenarios = load_housing_scenarios()
    elif category == "negligence":
        print("Loading negligence scenarios...")
        scenarios = load_negligence_scenarios()
    elif category == "custody":
        print("Loading custody scenarios...")
        scenarios = load_custody_scenarios()
    else:
        print(f"Unknown category: {category}")
        return

    print(f"Loaded {len(scenarios)} scenarios")

    if not scenarios:
        print("No scenarios found. Run 'hydrate' first.")
        return

    results = generate_complaints(
        scenarios,
        output_dir=output_dir,
        model=args.model,
    )

    print(f"Done. {len(results)} complaints generated.")


def cmd_extract(args):
    """Extract citations from generated complaints."""
    from src.citations import extract_citations_with_llm

    input_dir = Path(args.input)
    complaint_files = list(input_dir.glob("*.txt"))

    if not complaint_files:
        print(f"No complaint files found in {input_dir}")
        return

    print(f"Extracting citations from {len(complaint_files)} complaints...")

    for complaint_path in complaint_files:
        complaint_text = complaint_path.read_text()
        citations = extract_citations_with_llm(complaint_text, model=args.model)

        print(f"\n{complaint_path.name}: {len(citations)} citations")
        for cit in citations:
            print(f"  [{cit.citation_type}] {cit.raw_text}")


def cmd_evaluate(args):
    """Evaluate citations in generated complaints."""
    from src.evaluation import evaluate_complaints_directory

    input_dir = Path(args.input)

    if not input_dir.exists():
        print(f"Directory not found: {input_dir}")
        return

    results = evaluate_complaints_directory(
        input_dir,
        extraction_model=args.extraction_model,
        evaluation_model=args.evaluation_model,
    )

    # Print summary
    if results:
        total_citations = sum(r.total_citations for r in results)
        total_valid = sum(r.valid_citations for r in results)
        total_invalid = sum(r.invalid_citations for r in results)
        total_supported = sum(r.supported_propositions for r in results)
        total_unsupported = sum(r.unsupported_propositions for r in results)

        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Complaints evaluated: {len(results)}")
        print(f"Total citations: {total_citations}")
        print(f"Valid citations: {total_valid}")
        print(f"Invalid citations: {total_invalid}")
        if total_valid > 0:
            print(f"Supported propositions: {total_supported}")
            print(f"Unsupported propositions: {total_unsupported}")
            hallucination_rate = (total_invalid / (total_valid + total_invalid)) * 100
            print(f"Citation hallucination rate: {hallucination_rate:.1f}%")


def cmd_evaluate_elements(args):
    """Evaluate whether complaints assert required elements."""
    from src.elements_evaluation import evaluate_elements_directory

    input_dir = Path(args.input)

    if not input_dir.exists():
        print(f"Directory not found: {input_dir}")
        return

    results = evaluate_elements_directory(
        input_dir,
        model=args.model,
    )

    # Print summary
    if results:
        total_complaints = len(results)
        all_satisfied = sum(1 for r in results if r.all_elements_satisfied)
        total_elements = sum(r.elements_total for r in results)
        satisfied_elements = sum(r.elements_satisfied for r in results)

        print("\n" + "=" * 60)
        print("ELEMENTS EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Complaints evaluated: {total_complaints}")
        print(f"Complaints with all elements satisfied: {all_satisfied} ({all_satisfied/total_complaints*100:.1f}%)")
        print(f"Total elements across all complaints: {total_elements}")
        print(f"Elements satisfied: {satisfied_elements} ({satisfied_elements/total_elements*100:.1f}%)")

        # Per-category breakdown
        by_category: dict[str, list] = {}
        for r in results:
            if r.category not in by_category:
                by_category[r.category] = []
            by_category[r.category].append(r)

        print("\nBy category:")
        for cat, cat_results in sorted(by_category.items()):
            cat_total = len(cat_results)
            cat_all_satisfied = sum(1 for r in cat_results if r.all_elements_satisfied)
            print(f"  {cat}: {cat_all_satisfied}/{cat_total} complaints with all elements ({cat_all_satisfied/cat_total*100:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Pro Se Complaint Evaluation Framework"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Hydrate command
    hydrate_parser = subparsers.add_parser(
        "hydrate", help="Generate background info from raw fact patterns"
    )
    hydrate_parser.add_argument(
        "--category",
        "-c",
        choices=["housing", "negligence", "custody", "all"],
        default="all",
        help="Which category of scenarios to hydrate",
    )
    hydrate_parser.add_argument(
        "--variants",
        "-v",
        type=int,
        default=10,
        help="Number of variants to generate per fact pattern (default: 10)",
    )
    hydrate_parser.add_argument(
        "--model", "-m", default="gpt-4o-mini", help="Model to use for hydration"
    )

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate", help="Generate complaints from hydrated scenarios"
    )
    gen_parser.add_argument(
        "--category",
        "-c",
        choices=["housing", "negligence", "custody", "all"],
        default="all",
        help="Which category of scenarios to generate complaints for",
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        default="data/complaints",
        help="Output directory for complaints",
    )
    gen_parser.add_argument(
        "--model", "-m", default="gpt-5", help="Model to use for generation"
    )

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract", help="Extract citations from generated complaints"
    )
    extract_parser.add_argument(
        "--input",
        "-i",
        default="data/complaints",
        help="Directory containing complaint files",
    )
    extract_parser.add_argument(
        "--model", "-m", default="gpt-5-mini", help="Model to use for extraction"
    )

    # Evaluate command
    eval_parser = subparsers.add_parser(
        "evaluate", help="Evaluate citations in generated complaints"
    )
    eval_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Directory containing complaint files to evaluate",
    )
    eval_parser.add_argument(
        "--extraction-model",
        default="gpt-5-mini",
        help="Model to use for citation extraction",
    )
    eval_parser.add_argument(
        "--evaluation-model",
        default="gpt-5.1",
        help="Model to use for proposition support evaluation",
    )

    # Evaluate elements command
    eval_elements_parser = subparsers.add_parser(
        "evaluate-elements", help="Evaluate whether complaints assert required elements"
    )
    eval_elements_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Directory containing complaint files to evaluate",
    )
    eval_elements_parser.add_argument(
        "--model",
        "-m",
        default="gpt-5-mini",
        help="Model to use for elements evaluation",
    )

    args = parser.parse_args()

    if args.command == "hydrate":
        cmd_hydrate(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "extract":
        cmd_extract(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "evaluate-elements":
        cmd_evaluate_elements(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
