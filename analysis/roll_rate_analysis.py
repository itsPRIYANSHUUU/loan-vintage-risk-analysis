"""
roll_rate_analysis.py
----------------------
Roll-rate analysis answers: "Of loans that were in bucket X last month,
what % moved to bucket Y this month?"

This produces:
1. An overall transition matrix (the portfolio's typical behavior)
2. A monthly trend of the "30 DPD -> 60 DPD" roll rate -- this is the
   classic early-warning metric risk teams watch weekly/monthly, because
   it moves BEFORE headline NPA% does.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BUCKET_ORDER = ["Current", "30 DPD", "60 DPD", "90 DPD", "NPA"]


def load_snapshots():
    return pd.read_csv("data/monthly_snapshots.csv")


def build_transition_pairs(snaps):
    """For each loan, pair each month's bucket with the next month's bucket."""
    snaps = snaps.sort_values(["loan_id", "mob"])
    snaps["next_bucket"] = snaps.groupby("loan_id")["dpd_bucket"].shift(-1)
    snaps["next_snapshot_month"] = snaps.groupby("loan_id")["snapshot_month"].shift(-1)
    pairs = snaps.dropna(subset=["next_bucket"]).copy()
    return pairs


def overall_transition_matrix(pairs):
    matrix = pd.crosstab(pairs["dpd_bucket"], pairs["next_bucket"], normalize="index")
    matrix = matrix.reindex(index=BUCKET_ORDER, columns=BUCKET_ORDER, fill_value=0)
    return (matrix * 100).round(1)


def plot_transition_heatmap(matrix, out_path="outputs/roll_rate_heatmap.png"):
    plt.figure(figsize=(7, 5.5))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="Reds", cbar_kws={"label": "% of loans"})
    plt.title("Roll-Rate Transition Matrix (% moving from row bucket -> column bucket)")
    plt.ylabel("Bucket this month")
    plt.xlabel("Bucket next month")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved chart -> {out_path}")


def monthly_early_warning_trend(pairs, out_path="outputs/roll_rate_trend.png"):
    """Track the 30->60 DPD roll rate over calendar time -- the key early-warning KPI."""
    from_30 = pairs[pairs["dpd_bucket"] == "30 DPD"]
    trend = (
        from_30.groupby("snapshot_month")["next_bucket"]
        .apply(lambda x: (x == "60 DPD").mean() * 100)
        .reset_index(name="pct_30_to_60_roll")
    )
    trend = trend.sort_values("snapshot_month")
    trend.to_csv("outputs/roll_rate_trend_30to60.csv", index=False)

    plt.figure(figsize=(9, 4.5))
    plt.plot(trend["snapshot_month"], trend["pct_30_to_60_roll"], marker="o", color="darkred")
    plt.title("Early Warning KPI: % of 30-DPD Loans Rolling to 60-DPD, by Month")
    plt.xlabel("Calendar Month")
    plt.ylabel("Roll Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved chart -> {out_path}")
    return trend


if __name__ == "__main__":
    snaps = load_snapshots()
    pairs = build_transition_pairs(snaps)

    matrix = overall_transition_matrix(pairs)
    matrix.to_csv("outputs/transition_matrix.csv")
    plot_transition_heatmap(matrix)
    print("\nOverall Transition Matrix (%):")
    print(matrix)

    trend = monthly_early_warning_trend(pairs)
    print("\n30 DPD -> 60 DPD roll rate trend (early warning KPI):")
    print(trend.to_string(index=False))
