#!/usr/bin/env python3
"""Analysis utilities for the NeSy Cybersecurity survey paper catalog.

Provides summary statistics, cross-tabulations, and visualizations
for the 103-paper corpus described in the survey.

Usage:
    python catalog_analysis.py              # Print summary statistics
    python catalog_analysis.py --plot       # Also generate plots
    python catalog_analysis.py --export     # Export summary tables to CSV
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

TIER_NAMES = {
    "A": "Deep NeSy",
    "B": "Structured NeSy",
    "C": "Contextual Baselines",
}


def load_catalog() -> pd.DataFrame:
    """Load and return the paper catalog DataFrame."""
    path = DATA_DIR / "paper_catalog.csv"
    if not path.exists():
        sys.exit(f"Error: catalog not found at {path}")
    return pd.read_csv(path)


def load_gia_scores() -> pd.DataFrame:
    """Load and return the G-I-A scores DataFrame."""
    path = DATA_DIR / "gia_scores.csv"
    if not path.exists():
        sys.exit(f"Error: G-I-A scores not found at {path}")
    return pd.read_csv(path)


def print_summary(df: pd.DataFrame) -> None:
    """Print high-level summary statistics."""
    print("=" * 60)
    print("NeSy Cybersecurity Survey — Catalog Summary")
    print("=" * 60)
    print(f"\nTotal papers: {len(df)}")
    print(f"Year range: {df['year'].min()}–{df['year'].max()}")

    # Tier breakdown
    print("\n--- Integration Tier Distribution ---")
    for tier in ["A", "B", "C"]:
        count = (df["tier"] == tier).sum()
        pct = count / len(df) * 100
        print(f"  Type {tier} ({TIER_NAMES[tier]}): {count} papers ({pct:.1f}%)")

    # Type B subtypes
    type_b = df[df["tier"] == "B"]
    if not type_b.empty:
        print("\n--- Type B Subtypes ---")
        for subtype, count in type_b["subtype"].value_counts().items():
            print(f"  {subtype}: {count}")

    # Year distribution
    print("\n--- Papers by Year ---")
    for year, count in df["year"].value_counts().sort_index().items():
        bar = "█" * count
        print(f"  {year}: {count:3d}  {bar}")

    # Top domains
    print("\n--- Top 10 Application Domains ---")
    for domain, count in df["domain"].value_counts().head(10).items():
        print(f"  {domain}: {count}")

    # Venue types
    print("\n--- Venue Types ---")
    for venue, count in df["venue_type"].value_counts().items():
        print(f"  {venue}: {count}")


def print_gia_summary(gia_df: pd.DataFrame) -> None:
    """Print G-I-A score summary."""
    print("\n" + "=" * 60)
    print("G-I-A Framework Scores (from Table 2)")
    print("=" * 60)

    for _, row in gia_df.iterrows():
        print(f"\n  {row['system']} (Type {row['tier']})")
        print(f"    G={row['grounding']:.1f}  I={row['instructibility']:.1f}  A={row['alignment']:.1f}")
        print(f"    Key metric: {row['key_metric']} = {row['metric_value']}")

    # Averages by tier
    print("\n--- Average G-I-A by Tier ---")
    for tier in sorted(gia_df["tier"].unique()):
        subset = gia_df[gia_df["tier"] == tier]
        g_avg = subset["grounding"].mean()
        i_avg = subset["instructibility"].mean()
        a_avg = subset["alignment"].mean()
        print(f"  Type {tier}: G={g_avg:.2f}  I={i_avg:.2f}  A={a_avg:.2f}")


def cross_tabulation(df: pd.DataFrame) -> pd.DataFrame:
    """Generate tier x domain cross-tabulation."""
    cross = pd.crosstab(df["domain"], df["tier"], margins=True)
    cross.columns = [TIER_NAMES.get(c, c) for c in cross.columns]
    return cross


def generate_plots(df: pd.DataFrame) -> None:
    """Generate and save analysis plots."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib/numpy not available; skipping plots.")
        return

    FIGURES_DIR.mkdir(exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Tier distribution pie
    tier_counts = df["tier"].value_counts().sort_index()
    colors = ["#2E8B57", "#1F77B4", "#808080"]
    labels = [f"Type {t}\n{TIER_NAMES[t]}\n({c})" for t, c in tier_counts.items()]
    axes[0, 0].pie(tier_counts.values, labels=labels, colors=colors,
                   autopct="%1.1f%%", startangle=90)
    axes[0, 0].set_title("Integration Tier Distribution", fontweight="bold")

    # 2. Papers by year (stacked by tier)
    year_tier = pd.crosstab(df["year"], df["tier"])
    year_tier = year_tier.reindex(columns=["A", "B", "C"], fill_value=0)
    year_tier.plot.bar(stacked=True, ax=axes[0, 1], color=colors, alpha=0.85)
    axes[0, 1].set_title("Papers by Year and Tier", fontweight="bold")
    axes[0, 1].set_xlabel("Year")
    axes[0, 1].set_ylabel("Number of Papers")
    axes[0, 1].legend(title="Tier", labels=[TIER_NAMES[t] for t in ["A", "B", "C"]])

    # 3. Top domains
    domain_counts = df["domain"].value_counts().head(10)
    axes[1, 0].barh(range(len(domain_counts)), domain_counts.values,
                    color="#1F77B4", alpha=0.8)
    axes[1, 0].set_yticks(range(len(domain_counts)))
    axes[1, 0].set_yticklabels(domain_counts.index)
    axes[1, 0].set_xlabel("Number of Papers")
    axes[1, 0].set_title("Top Application Domains", fontweight="bold")
    axes[1, 0].invert_yaxis()

    # 4. Type B subtype breakdown
    type_b = df[df["tier"] == "B"]
    if not type_b.empty:
        sub_counts = type_b["subtype"].value_counts()
        axes[1, 1].bar(range(len(sub_counts)), sub_counts.values,
                       color="#1F77B4", alpha=0.8)
        axes[1, 1].set_xticks(range(len(sub_counts)))
        axes[1, 1].set_xticklabels(sub_counts.index, rotation=45, ha="right")
        axes[1, 1].set_ylabel("Number of Papers")
        axes[1, 1].set_title("Type B Subtypes", fontweight="bold")

    plt.tight_layout()
    out_path = FIGURES_DIR / "catalog_analysis.png"
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"\nPlot saved to {out_path}")
    plt.close()


def export_tables(df: pd.DataFrame) -> None:
    """Export summary tables to CSV."""
    out_dir = DATA_DIR / "summaries"
    out_dir.mkdir(exist_ok=True)

    # Tier counts
    tier_summary = df.groupby("tier").agg(
        count=("id", "count"),
        domains=("domain", "nunique"),
        year_min=("year", "min"),
        year_max=("year", "max"),
    )
    tier_summary.to_csv(out_dir / "tier_summary.csv")

    # Cross-tab
    cross = cross_tabulation(df)
    cross.to_csv(out_dir / "domain_tier_crosstab.csv")

    print(f"\nSummary tables exported to {out_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze the NeSy Cybersecurity survey paper catalog."
    )
    parser.add_argument("--plot", action="store_true", help="Generate analysis plots")
    parser.add_argument("--export", action="store_true", help="Export summary tables")
    args = parser.parse_args()

    df = load_catalog()
    print_summary(df)

    gia_df = load_gia_scores()
    print_gia_summary(gia_df)

    if args.plot:
        generate_plots(df)

    if args.export:
        export_tables(df)


if __name__ == "__main__":
    main()
