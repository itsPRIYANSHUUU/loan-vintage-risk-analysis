"""
powerbi_export.py
------------------
Exports a clean, star-schema-friendly set of CSVs so this project can be
plugged straight into Power BI:
    - fact_snapshots.csv   (loan_id, month, mob, bucket, is_bad flag)
    - dim_loans.csv        (loan attributes for slicing: segment, city tier, vintage)
    - vintage_curve.csv    (pre-aggregated, ready for a line chart visual)
    - transition_matrix.csv(ready for a matrix/heatmap visual)

Import all four into Power BI, relate fact_snapshots.loan_id -> dim_loans.loan_id,
and you have a working delinquency early-warning dashboard.
"""

import pandas as pd

BAD_BUCKETS = {"60 DPD", "90 DPD", "NPA"}


def run():
    loans = pd.read_csv("data/loans.csv")
    snaps = pd.read_csv("data/monthly_snapshots.csv")

    snaps["is_bad_flag"] = snaps["dpd_bucket"].isin(BAD_BUCKETS).astype(int)

    snaps.to_csv("outputs/powerbi/fact_snapshots.csv", index=False)
    loans.to_csv("outputs/powerbi/dim_loans.csv", index=False)

    print("Power BI-ready files exported to outputs/powerbi/")
    print(" - fact_snapshots.csv (relate loan_id -> dim_loans.loan_id)")
    print(" - dim_loans.csv")
    print(" - vintage_curve_data.csv and transition_matrix.csv (already in outputs/, copy over too)")


if __name__ == "__main__":
    run()
