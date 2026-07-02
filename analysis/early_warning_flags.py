"""
early_warning_flags.py
-----------------------
Turns the vintage + roll-rate numbers into a short, decision-ready list --
the kind of output a credit risk analyst would actually send to their
manager: "here's what needs action, and why."
"""

import pandas as pd

BAD_BUCKETS = {"60 DPD", "90 DPD", "NPA"}


def load():
    loans = pd.read_csv("data/loans.csv")
    snaps = pd.read_csv("data/monthly_snapshots.csv")
    return loans, snaps


def flag_risky_vintages(loans, snaps, mob_checkpoint=6, threshold_pct=10.0):
    snaps = snaps.copy()
    snaps["is_bad"] = snaps["dpd_bucket"].isin(BAD_BUCKETS)
    at_mob = snaps[snaps["mob"] == mob_checkpoint]
    cohort_rate = (
        at_mob.groupby("disbursal_month")["is_bad"].mean().mul(100).round(2)
    )
    flagged = cohort_rate[cohort_rate > threshold_pct].sort_values(ascending=False)
    return flagged


def flag_risky_segments(loans, snaps, threshold_pct=8.0):
    merged = snaps.merge(loans[["loan_id", "segment", "city_tier"]], on="loan_id")
    merged["is_bad"] = merged["dpd_bucket"].isin(BAD_BUCKETS)
    seg_rate = (
        merged.groupby(["segment", "city_tier"])["is_bad"].mean().mul(100).round(2)
    )
    flagged = seg_rate[seg_rate > threshold_pct].sort_values(ascending=False)
    return flagged


if __name__ == "__main__":
    loans, snaps = load()

    print("=" * 60)
    print("EARLY WARNING REPORT")
    print("=" * 60)

    risky_vintages = flag_risky_vintages(loans, snaps)
    print("\n[1] Cohorts exceeding 10% 60+DPD rate at MOB=6 (action: tighten underwriting"
          " for similar future approvals, review that month's policy):")
    print(risky_vintages.to_string() if len(risky_vintages) else "  None flagged.")

    risky_segments = flag_risky_segments(loans, snaps)
    print("\n[2] Segment x City-Tier combos exceeding 8% 60+DPD rate overall"
          " (action: review pricing/limits for these segments):")
    print(risky_segments.to_string() if len(risky_segments) else "  None flagged.")

    with open("outputs/early_warning_report.txt", "w") as f:
        f.write("EARLY WARNING REPORT\n" + "=" * 60 + "\n\n")
        f.write("Risky Vintages (60+DPD > 10% at MOB=6):\n")
        f.write(risky_vintages.to_string() if len(risky_vintages) else "None flagged.")
        f.write("\n\nRisky Segment x City-Tier (60+DPD > 8% overall):\n")
        f.write(risky_segments.to_string() if len(risky_segments) else "None flagged.")
    print("\nSaved -> outputs/early_warning_report.txt")
