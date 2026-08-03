#!/usr/bin/env python3
"""Analysis utilities for the NeSy Cybersecurity survey paper catalog.

Provides summary statistics, cross-tabulations, and visualizations
for the 107-paper corpus described in the survey.

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
    """Generate and save an academic-style overview figure."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        import numpy as np
    except ImportError:
        print("matplotlib/numpy not available; skipping plots.")
        return

    FIGURES_DIR.mkdir(exist_ok=True)

    # --- Academic style ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "figure.dpi": 150,
    })

    tier_colors = {"A": "#2E8B57", "B": "#1F77B4", "C": "#808080"}
    subtype_palette = ["#1F4E79", "#2E75B6", "#5B9BD5", "#8FAADC",
                       "#A5A5A5", "#7F7F7F", "#C55A11", "#ED7D31", "#F4B183"]

    fig = plt.figure(figsize=(15, 11.5), constrained_layout=False)
    gs = GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38,
                  height_ratios=[0.38, 1.0, 1.0], left=0.06, right=0.97,
                  top=0.95, bottom=0.06)

    # ---- Header / summary banner ----
    ax_hdr = fig.add_subplot(gs[0, :])
    ax_hdr.axis("off")
    n_total = len(df)
    n_a = (df["tier"] == "A").sum()
    n_b = (df["tier"] == "B").sum()
    n_c = (df["tier"] == "C").sum()
    year_min, year_max = df["year"].min(), df["year"].max()
    n_domains = df["domain"].nunique()
    n_venues = df["venue_type"].nunique()

    ax_hdr.text(0.5, 0.92,
                "Neuro-Symbolic AI for Cybersecurity — Corpus Overview",
                ha="center", va="top", fontsize=16, fontweight="bold",
                transform=ax_hdr.transAxes)
    ax_hdr.text(0.5, 0.70,
                f"Systematic Literature Review  ·  {n_total} Publications  ·  "
                f"{year_min}–{year_max}  ·  {n_domains} Application Domains",
                ha="center", va="top", fontsize=10.5, style="italic",
                color="#555555", transform=ax_hdr.transAxes)

    # Stat boxes
    stat_items = [
        ("Type A — Deep NeSy", n_a, tier_colors["A"]),
        ("Type B — Structured NeSy", n_b, tier_colors["B"]),
        ("Type C — Baselines", n_c, tier_colors["C"]),
        ("Venue Types", n_venues, "#444444"),
    ]
    box_w = 0.18
    gap = (1 - 4 * box_w) / 5
    for i, (lbl, val, col) in enumerate(stat_items):
        x = gap + i * (box_w + gap)
        ax_hdr.add_patch(plt.Rectangle((x, 0.05), box_w, 0.42,
                                        transform=ax_hdr.transAxes,
                                        facecolor=col, alpha=0.12,
                                        edgecolor=col, linewidth=1.2))
        ax_hdr.text(x + box_w / 2, 0.38, lbl, ha="center", va="center",
                    fontsize=8.5, color="#333333", transform=ax_hdr.transAxes)
        ax_hdr.text(x + box_w / 2, 0.20, f"{val}", ha="center", va="center",
                    fontsize=15, fontweight="bold", color=col,
                    transform=ax_hdr.transAxes)

    # ---- (A) Donut: tier distribution ----
    ax1 = fig.add_subplot(gs[1, 0])
    tier_counts = df["tier"].value_counts().sort_index()
    colors_ord = [tier_colors[t] for t in tier_counts.index]
    wedges, _ = ax1.pie(tier_counts.values, colors=colors_ord,
                        startangle=90, wedgeprops=dict(width=0.38,
                                                       edgecolor="white",
                                                       linewidth=2))
    for w, t, c in zip(wedges, tier_counts.index, tier_counts.values):
        ang = (w.theta2 + w.theta1) / 2
        x = 0.78 * np.cos(np.deg2rad(ang))
        y = 0.78 * np.sin(np.deg2rad(ang))
        ax1.text(x, y, f"{c}\n({c/n_total*100:.0f}%)", ha="center",
                 va="center", fontsize=9.5, fontweight="bold", color="white")
    ax1.text(0, 0, f"N={n_total}", ha="center", va="center",
             fontsize=13, fontweight="bold", color="#333333")
    ax1.set_title("(a) Integration Tier Distribution", pad=10)
    legend_labels = [f"Type {t}  {TIER_NAMES[t]}" for t in tier_counts.index]
    ax1.legend(wedges, legend_labels, loc="center",
               bbox_to_anchor=(0.5, -0.08), ncol=1, fontsize=8.5)

    # ---- (B) Stacked bar: papers by year × tier ----
    ax2 = fig.add_subplot(gs[1, 1:])
    year_tier = pd.crosstab(df["year"], df["tier"]).reindex(
        columns=["A", "B", "C"], fill_value=0)
    bottoms = np.zeros(len(year_tier))
    for tier in ["A", "B", "C"]:
        vals = year_tier[tier].values
        ax2.bar(year_tier.index.astype(str), vals, bottom=bottoms,
                color=tier_colors[tier], edgecolor="white", linewidth=0.8,
                label=f"Type {tier} — {TIER_NAMES[tier]}", width=0.72)
        bottoms += vals
    totals = year_tier.sum(axis=1).values
    for i, tot in enumerate(totals):
        ax2.text(i, tot + 0.6, f"{tot}", ha="center", va="bottom",
                 fontsize=9, fontweight="bold", color="#333333")
    ax2.set_title("(b) Publication Volume by Year and Integration Tier", pad=10)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Publications")
    ax2.set_ylim(0, max(totals) * 1.18)
    ax2.grid(axis="y", linestyle=":", alpha=0.5, color="#999999")
    ax2.set_axisbelow(True)
    ax2.legend(loc="upper left", ncol=1, frameon=False)

    # ---- (C) Horizontal bar: top application domains ----
    ax3 = fig.add_subplot(gs[2, :2])
    dom_counts = df["domain"].value_counts().head(10).iloc[::-1]
    # Compute dominant tier per domain for color hint
    def dominant_tier(domain):
        sub = df[df["domain"] == domain]
        return sub["tier"].mode().iloc[0]
    bar_colors = [tier_colors[dominant_tier(d)] for d in dom_counts.index]
    bars = ax3.barh(range(len(dom_counts)), dom_counts.values,
                    color=bar_colors, alpha=0.85, edgecolor="white",
                    linewidth=0.8)
    ax3.set_yticks(range(len(dom_counts)))
    ax3.set_yticklabels(dom_counts.index)
    for bar, v in zip(bars, dom_counts.values):
        ax3.text(v + 0.12, bar.get_y() + bar.get_height() / 2, str(v),
                 va="center", ha="left", fontsize=9, color="#333333")
    ax3.set_title("(c) Top-10 Application Domains (colored by dominant tier)",
                  pad=10)
    ax3.set_xlabel("Number of Publications")
    ax3.set_xlim(0, dom_counts.max() * 1.15)
    ax3.grid(axis="x", linestyle=":", alpha=0.5, color="#999999")
    ax3.set_axisbelow(True)

    # ---- (D) Type B subtype breakdown ----
    ax4 = fig.add_subplot(gs[2, 2])
    type_b = df[df["tier"] == "B"]
    if not type_b.empty:
        sub_counts = type_b["subtype"].value_counts()
        pal = (subtype_palette * ((len(sub_counts) // len(subtype_palette)) + 1))[:len(sub_counts)]
        bars = ax4.barh(range(len(sub_counts)), sub_counts.values,
                        color=pal, edgecolor="white", linewidth=0.8, alpha=0.9)
        ax4.set_yticks(range(len(sub_counts)))
        ax4.set_yticklabels(sub_counts.index)
        ax4.invert_yaxis()
        for bar, v in zip(bars, sub_counts.values):
            ax4.text(v + 0.1, bar.get_y() + bar.get_height() / 2, str(v),
                     va="center", ha="left", fontsize=9, color="#333333")
        ax4.set_title(f"(d) Type B Subtypes (N={len(type_b)})", pad=10)
        ax4.set_xlabel("Number of Publications")
        ax4.set_xlim(0, sub_counts.max() * 1.2)
        ax4.grid(axis="x", linestyle=":", alpha=0.5, color="#999999")
        ax4.set_axisbelow(True)

    # Footer / source note
    fig.text(0.5, 0.015,
             "Source: paper_catalog.csv  ·  Hakim et al. (2025), "
             "arXiv:2509.06921  ·  Generated by scripts/catalog_analysis.py",
             ha="center", va="bottom", fontsize=8, style="italic",
             color="#666666")

    out_png = FIGURES_DIR / "catalog_analysis.png"
    out_pdf = FIGURES_DIR / "catalog_analysis.pdf"
    plt.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    plt.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    print(f"\nPlot saved to {out_png} and {out_pdf}")
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
