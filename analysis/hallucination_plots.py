#!/usr/bin/env python
"""Generate hallucination rate plots.

Creates:
1. Overall hallucination rate by model
2. Hallucination rate by model and topic area
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
COLORS = ["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974", "#64B5CD"]


def plot_hallucination_by_model(model_stats: dict, output_dir):
    """Plot overall hallucination rate by model."""
    models = []
    hallucination_rates = []
    valid_counts = []
    invalid_counts = []

    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        total = stats.valid_citations + stats.invalid_citations
        if total == 0:
            continue

        models.append(model_name)
        rate = stats.invalid_citations / total * 100
        hallucination_rates.append(rate)
        valid_counts.append(stats.valid_citations)
        invalid_counts.append(stats.invalid_citations)

    if not models:
        print("No data to plot for hallucination by model")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(models))
    width = 0.6

    bars = ax.bar(x, hallucination_rates, width, color=COLORS[2], edgecolor="black", linewidth=0.5)

    # Add value labels on bars
    for bar, rate, invalid, valid in zip(bars, hallucination_rates, invalid_counts, valid_counts):
        height = bar.get_height()
        ax.annotate(
            f"{rate:.1f}%\n({invalid}/{invalid+valid})",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_ylabel("Hallucination Rate (%)")
    ax.set_xlabel("Model")
    ax.set_title("Citation Hallucination Rate by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_ylim(0, max(hallucination_rates) * 1.3 if hallucination_rates else 100)

    plt.tight_layout()

    output_file = output_dir / "hallucination_by_model.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "hallucination_by_model.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def plot_hallucination_by_model_and_topic(model_stats: dict, output_dir):
    """Plot hallucination rate by model and topic area."""
    models = sorted(model_stats.keys())
    categories = ["custody_modification", "negligence", "landlord_tenant"]
    category_labels = [CATEGORY_DISPLAY_NAMES.get(c, c) for c in categories]

    # Build data matrix
    data = []
    for cat in categories:
        cat_rates = []
        for model_name in models:
            stats = model_stats[model_name]
            cat_stats = stats.by_category.get(cat, {})
            valid = cat_stats.get("valid_citations", 0)
            invalid = cat_stats.get("invalid_citations", 0)
            total = valid + invalid
            rate = (invalid / total * 100) if total > 0 else 0
            cat_rates.append(rate)
        data.append(cat_rates)

    if not models:
        print("No data to plot for hallucination by topic")
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
            color=COLORS[i],
            edgecolor="black",
            linewidth=0.5,
        )
        multiplier += 1

    ax.set_ylabel("Hallucination Rate (%)")
    ax.set_xlabel("Model")
    ax.set_title("Citation Hallucination Rate by Model and Topic Area")
    ax.set_xticks(x + width)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.legend(title="Topic Area", loc="upper right")

    # Set reasonable y-axis limit
    all_rates = [r for rates in data for r in rates]
    if all_rates:
        ax.set_ylim(0, max(all_rates) * 1.2 if max(all_rates) > 0 else 100)

    plt.tight_layout()

    output_file = output_dir / "hallucination_by_model_topic.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "hallucination_by_model_topic.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def plot_avg_citations_per_complaint(model_stats: dict, output_dir):
    """Plot average number of citations per complaint by model."""
    models = []
    avg_citations = []
    complaint_counts = []
    citation_counts = []

    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        if stats.num_complaints == 0:
            continue

        models.append(model_name)
        avg = stats.total_case_citations / stats.num_complaints
        avg_citations.append(avg)
        complaint_counts.append(stats.num_complaints)
        citation_counts.append(stats.total_case_citations)

    if not models:
        print("No data to plot for citations per complaint")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(models))
    width = 0.6

    bars = ax.bar(x, avg_citations, width, color=COLORS[0], edgecolor="black", linewidth=0.5)

    # Add value labels on bars
    for bar, avg, citations, complaints in zip(bars, avg_citations, citation_counts, complaint_counts):
        height = bar.get_height()
        ax.annotate(
            f"{avg:.1f}\n({citations}/{complaints})",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_ylabel("Average Citations per Complaint")
    ax.set_xlabel("Model")
    ax.set_title("Average Number of Case Citations per Complaint by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_ylim(0, max(avg_citations) * 1.25 if avg_citations else 10)

    plt.tight_layout()

    output_file = output_dir / "avg_citations_per_complaint.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "avg_citations_per_complaint.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {output_file}")
    plt.close()


def main():
    data_dir = get_data_dir()
    output_dir = get_output_dir()

    print(f"Loading data from {data_dir}...")
    all_citations, model_stats = load_all_evaluations(data_dir)

    print(f"Loaded {len(all_citations)} citations from {len(model_stats)} models")

    print("\nGenerating plots...")
    plot_hallucination_by_model(model_stats, output_dir)
    plot_hallucination_by_model_and_topic(model_stats, output_dir)
    plot_avg_citations_per_complaint(model_stats, output_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
