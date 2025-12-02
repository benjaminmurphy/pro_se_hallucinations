#!/usr/bin/env python
"""Generate proposition support rate plots.

For non-hallucinated (valid) citations, shows whether they support
their cited proposition, broken down by model and topic area.
"""

import matplotlib.pyplot as plt
import numpy as np

from load_data import (
    CATEGORY_DISPLAY_NAMES,
    get_data_dir,
    get_output_dir,
    load_all_evaluations,
)

# NeurIPS-style plot settings
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# Color palette
COLORS = {
    "supported": "#55A868",  # Green
    "unsupported": "#C44E52",  # Red
    "unknown": "#CCCCCC",  # Gray
}

TOPIC_COLORS = ["#4C72B0", "#55A868", "#C44E52"]


def plot_support_stacked_by_model(model_stats: dict, output_dir):
    """Plot stacked bar chart of support/unsupport by model."""
    models = sorted(model_stats.keys())

    supported_rates = []
    unsupported_rates = []

    for model_name in models:
        stats = model_stats[model_name]
        total_evaluated = stats.supported + stats.unsupported
        if total_evaluated > 0:
            supported_rates.append(stats.supported / total_evaluated * 100)
            unsupported_rates.append(stats.unsupported / total_evaluated * 100)
        else:
            supported_rates.append(0)
            unsupported_rates.append(0)

    if not models:
        print("No data to plot for support by model")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(models))
    width = 0.6

    # Stacked bars
    bars1 = ax.bar(
        x,
        supported_rates,
        width,
        label="Supports Proposition",
        color=COLORS["supported"],
        edgecolor="black",
        linewidth=0.5,
    )
    bars2 = ax.bar(
        x,
        unsupported_rates,
        width,
        bottom=supported_rates,
        label="Does Not Support",
        color=COLORS["unsupported"],
        edgecolor="black",
        linewidth=0.5,
    )

    # Add labels
    for i, (model_name, supp, unsupp) in enumerate(zip(models, supported_rates, unsupported_rates)):
        stats = model_stats[model_name]
        total = stats.supported + stats.unsupported
        if total > 0:
            ax.annotate(
                f"{supp:.0f}%",
                xy=(i, supp / 2),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )
            ax.annotate(
                f"{unsupp:.0f}%",
                xy=(i, supp + unsupp / 2),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    ax.set_ylabel("Percentage of Valid Citations")
    ax.set_xlabel("Model")
    ax.set_title("Proposition Support Rate for Valid Citations by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right")

    plt.tight_layout()

    output_file = output_dir / "support_by_model.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "support_by_model.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def plot_support_by_model_and_topic(model_stats: dict, output_dir):
    """Plot support rate by model and topic area (grouped bars)."""
    models = sorted(model_stats.keys())
    categories = ["custody_modification", "negligence", "landlord_tenant"]
    category_labels = [CATEGORY_DISPLAY_NAMES.get(c, c) for c in categories]

    # Build data: support rate for each category
    data = []
    for cat in categories:
        cat_rates = []
        for model_name in models:
            stats = model_stats[model_name]
            cat_stats = stats.by_category.get(cat, {})
            supported = cat_stats.get("supported", 0)
            unsupported = cat_stats.get("unsupported", 0)
            total = supported + unsupported
            rate = (supported / total * 100) if total > 0 else 0
            cat_rates.append(rate)
        data.append(cat_rates)

    if not models:
        print("No data to plot for support by topic")
        return

    fig, ax = plt.subplots(figsize=(12, 5))

    x = np.arange(len(models))
    width = 0.25
    multiplier = 0

    for i, (cat_rates, label) in enumerate(zip(data, category_labels)):
        offset = width * multiplier
        bars = ax.bar(
            x + offset,
            cat_rates,
            width,
            label=label,
            color=TOPIC_COLORS[i],
            edgecolor="black",
            linewidth=0.5,
        )
        # Add value labels
        for bar, rate in zip(bars, cat_rates):
            if rate > 0:
                ax.annotate(
                    f"{rate:.0f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                )
        multiplier += 1

    ax.set_ylabel("Support Rate (%)")
    ax.set_xlabel("Model")
    ax.set_title("Proposition Support Rate by Model and Topic Area\n(For Valid Citations Only)")
    ax.set_xticks(x + width)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.legend(title="Topic Area", loc="upper right")
    ax.set_ylim(0, 110)

    plt.tight_layout()

    output_file = output_dir / "support_by_model_topic.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "support_by_model_topic.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def plot_combined_validity_support(model_stats: dict, output_dir):
    """Plot combined view: hallucinated vs valid-supported vs valid-unsupported."""
    models = sorted(model_stats.keys())

    hallucinated = []
    valid_supported = []
    valid_unsupported = []

    for model_name in models:
        stats = model_stats[model_name]
        total = stats.valid_citations + stats.invalid_citations
        if total > 0:
            hallucinated.append(stats.invalid_citations / total * 100)
            valid_supported.append(stats.supported / total * 100)
            valid_unsupported.append(stats.unsupported / total * 100)
        else:
            hallucinated.append(0)
            valid_supported.append(0)
            valid_unsupported.append(0)

    if not models:
        print("No data to plot for combined view")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(models))
    width = 0.6

    # Stacked bars: hallucinated (bottom), valid-unsupported, valid-supported (top)
    bars1 = ax.bar(
        x,
        hallucinated,
        width,
        label="Hallucinated",
        color="#C44E52",
        edgecolor="black",
        linewidth=0.5,
    )
    bars2 = ax.bar(
        x,
        valid_unsupported,
        width,
        bottom=hallucinated,
        label="Valid but Unsupported",
        color="#CCB974",
        edgecolor="black",
        linewidth=0.5,
    )
    bottom2 = [h + u for h, u in zip(hallucinated, valid_unsupported)]
    bars3 = ax.bar(
        x,
        valid_supported,
        width,
        bottom=bottom2,
        label="Valid and Supported",
        color="#55A868",
        edgecolor="black",
        linewidth=0.5,
    )

    ax.set_ylabel("Percentage of All Case Citations")
    ax.set_xlabel("Model")
    ax.set_title("Citation Quality Breakdown by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right")

    plt.tight_layout()

    output_file = output_dir / "citation_quality_breakdown.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "citation_quality_breakdown.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def main():
    data_dir = get_data_dir()
    output_dir = get_output_dir()

    print(f"Loading data from {data_dir}...")
    all_citations, model_stats = load_all_evaluations(data_dir)

    print(f"Loaded {len(all_citations)} citations from {len(model_stats)} models")

    # Print summary stats
    print("\nSummary by model:")
    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        total_evaluated = stats.supported + stats.unsupported
        if total_evaluated > 0:
            support_rate = stats.supported / total_evaluated * 100
            print(f"  {model_name}: {support_rate:.1f}% support rate ({stats.supported}/{total_evaluated})")

    print("\nGenerating plots...")
    plot_support_stacked_by_model(model_stats, output_dir)
    plot_support_by_model_and_topic(model_stats, output_dir)
    plot_combined_validity_support(model_stats, output_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
