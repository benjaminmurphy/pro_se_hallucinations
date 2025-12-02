"""Entry point for scenario hydration.

Usage:
    uv run python -m src.generate_scenarios [--category housing|negligence|custody|all] [--variants 10]
"""

import argparse

from scenarios import (
    QUIET_ENJOYMENT_SCENARIOS,
    NEGLIGENCE_SCENARIOS,
    CUSTODY_MODIFICATION_SCENARIOS,
)
from src.scenarios import (
    generate_housing_scenarios,
    generate_negligence_scenarios,
    generate_custody_scenarios,
)


def main():
    parser = argparse.ArgumentParser(description="Generate hydrated scenarios")
    parser.add_argument(
        "--category", "-c",
        choices=["housing", "negligence", "custody", "all"],
        default="all",
        help="Which category of scenarios to hydrate"
    )
    parser.add_argument(
        "--variants", "-v",
        type=int,
        default=10,
        help="Number of variants to generate per fact pattern (default: 10)"
    )
    parser.add_argument(
        "--model", "-m",
        default="gpt-4o-mini",
        help="Model to use for hydration"
    )

    args = parser.parse_args()
    num_variants = args.variants

    if args.category in ("housing", "all"):
        print("=" * 60)
        print(f"HOUSING / QUIET ENJOYMENT SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_housing_scenarios(
            QUIET_ENJOYMENT_SCENARIOS, model=args.model, num_variants=num_variants
        )

    if args.category in ("negligence", "all"):
        print("\n" + "=" * 60)
        print(f"NEGLIGENCE SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_negligence_scenarios(
            NEGLIGENCE_SCENARIOS, model=args.model, num_variants=num_variants
        )

    if args.category in ("custody", "all"):
        print("\n" + "=" * 60)
        print(f"CUSTODY MODIFICATION SCENARIOS ({num_variants} variants each)")
        print("=" * 60)
        generate_custody_scenarios(
            CUSTODY_MODIFICATION_SCENARIOS, model=args.model, num_variants=num_variants
        )


if __name__ == "__main__":
    main()
