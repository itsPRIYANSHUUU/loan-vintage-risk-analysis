"""
vintage_analysis.py
--------------------
Builds vintage curves: for each disbursal cohort (vintage), what % of loans
are in 60+ DPD (early sign of trouble) or NPA, at each Month-On-Book (MOB).

Business read: if the March 2025 cohort's curve rises much faster than
January's, something in March's underwriting/approval process was weaker
-- a signal to investigate, not just a data point.
"""

import pandas as pd
import matplotlib.pyplot as plt

BAD_BUCKETS = {"60 DPD", "90 DPD", "NPA"}


def load_data():
    loans = pd.read_csv("data/loans.csv")
    snaps = pd.read_csv("data/monthly_snapshots.csv")
    return loans, snaps


def build_vintage_curve(snaps):
    snaps = snaps.copy()
    snaps["is_bad"] = snaps["dpd_bucket"].isin(BAD_BUCKETS)

    curve = (
        snaps.groupby(["disbursal_month", "mob"])["is_bad"]
        .mean()
        .reset_index()
        .rename(columns={"is_bad": "pct_60plus_dpd"})
    )
    curve["pct_60plus_dpd"] = (curve["pct_60plus_dpd"] * 100).round(2)
    return curve


def plot_vintage_curves(curve, out_path="outputs/vintage_curves.png"):
    plt.figure(figsize=(10, 6))
    for vintage, grp in curve.groupby("disbursal_month"):
        plt.plot(grp["mob"], grp["pct_60plus_dpd"], marker="o", markersize=3, label=vintage)

    plt.title("Vintage Curves: % of Loans in 60+ DPD by Months-on-Book")
    plt.xlabel("Months on Book (MOB)")
    plt.ylabel("% of Cohort in 60+ DPD")
    plt.legend(fontsize=6, ncol=3, loc="upper left")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved chart -> {out_path}")


def worst_vintages(curve, mob_checkpoint=6, top_n=5):
    """Rank cohorts by how bad they look at a fixed MOB checkpoint (fair comparison)."""
    snapshot_at_mob = curve[curve["mob"] == mob_checkpoint].sort_values(
        "pct_60plus_dpd", ascending=False
    )
    return snapshot_at_mob.head(top_n)


if __name__ == "__main__":
    loans, snaps = load_data()
    curve = build_vintage_curve(snaps)
    curve.to_csv("outputs/vintage_curve_data.csv", index=False)
    plot_vintage_curves(curve)

    print("\nTop 5 worst-performing vintages at MOB=6 (i.e. 6 months after disbursal):")
    print(worst_vintages(curve).to_string(index=False))
