#!/usr/bin/env python
"""Run all analysis scripts."""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).parent

    scripts = [
        "top_cases.py",
        "hallucination_plots.py",
        "support_plots.py",
    ]

    for script in scripts:
        script_path = script_dir / script
        print(f"\n{'='*60}")
        print(f"Running {script}...")
        print("=" * 60)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_dir,
        )

        if result.returncode != 0:
            print(f"Error running {script}")
            sys.exit(1)

    print(f"\n{'='*60}")
    print("All analyses complete!")
    print(f"Output files saved to: {script_dir / 'output'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
