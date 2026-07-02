"""
generate_data.py
-----------------
Simulates a realistic NBFC/Bank personal loan portfolio disbursed over 18 months,
then simulates each loan's monthly delinquency status (DPD bucket) using a
Markov-chain style transition model, so that:
    - some months of disbursal are deliberately "bad vintages" (weaker underwriting)
    - riskier segments roll into delinquency faster
    - a small % of loans cure (move back to a healthier bucket)

Outputs:
    data/loans.csv              -> one row per loan (static attributes)
    data/monthly_snapshots.csv  -> one row per loan per month (DPD bucket over time)
"""

import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

np.random.seed(42)

AS_OF_DATE = datetime(2026, 6, 30)
DISBURSAL_START = datetime(2025, 1, 1)
N_MONTHS_DISBURSAL = 18          # loans disbursed Jan 2025 - Jun 2026
LOANS_PER_MONTH = 220

BUCKETS = ["Current", "30 DPD", "60 DPD", "90 DPD", "NPA"]
BUCKET_IDX = {b: i for i, b in enumerate(BUCKETS)}

SEGMENTS = ["Salaried", "Self-Employed"]
CITY_TIERS = ["Tier 1", "Tier 2", "Tier 3"]

# Vintages that had weaker underwriting (simulates a real risk event, e.g.
# a relaxed credit policy or an economic shock affecting that cohort)
BAD_VINTAGES = {"2025-06", "2025-07", "2025-08"}  # a "bad quarter"


def month_str(dt):
    return dt.strftime("%Y-%m")


def generate_loans():
    rows = []
    loan_id = 1000
    for m in range(N_MONTHS_DISBURSAL):
        disb_date = DISBURSAL_START + relativedelta(months=m)
        vintage = month_str(disb_date)
        for _ in range(LOANS_PER_MONTH):
            loan_id += 1
            segment = np.random.choice(SEGMENTS, p=[0.62, 0.38])
            city_tier = np.random.choice(CITY_TIERS, p=[0.45, 0.35, 0.20])
            loan_amount = int(np.clip(np.random.normal(90000, 30000), 15000, 300000))
            tenure = int(np.random.choice([12, 24, 36, 48]))
            interest_rate = round(np.random.uniform(11.5, 22.0), 2)
            # base risk score 300-900 (like a bureau score), lower = riskier
            risk_score = int(np.clip(np.random.normal(680, 90), 300, 900))

            rows.append({
                "loan_id": f"L{loan_id}",
                "disbursal_month": vintage,
                "disbursal_date": disb_date.strftime("%Y-%m-%d"),
                "segment": segment,
                "city_tier": city_tier,
                "loan_amount": loan_amount,
                "tenure_months": tenure,
                "interest_rate": interest_rate,
                "bureau_risk_score": risk_score,
                "is_bad_vintage": vintage in BAD_VINTAGES,
            })
    return pd.DataFrame(rows)


def base_deterioration_prob(row):
    """Monthly probability a loan in 'Current' status starts slipping (Current -> 30 DPD)."""
    p = 0.025  # baseline
    if row["segment"] == "Self-Employed":
        p += 0.015
    if row["city_tier"] == "Tier 3":
        p += 0.012
    if row["bureau_risk_score"] < 600:
        p += 0.03
    elif row["bureau_risk_score"] > 750:
        p -= 0.012
    if row["is_bad_vintage"]:
        p += 0.035
    return float(np.clip(p, 0.005, 0.20))


def simulate_snapshots(loans_df):
    snapshot_rows = []
    for _, loan in loans_df.iterrows():
        disb_date = datetime.strptime(loan["disbursal_date"], "%Y-%m-%d")
        deteriorate_p = base_deterioration_prob(loan)
        bucket = "Current"
        mob = 0
        cur_date = disb_date
        while cur_date <= AS_OF_DATE and mob <= loan["tenure_months"]:
            mob += 1
            cur_date = disb_date + relativedelta(months=mob)
            if cur_date > AS_OF_DATE:
                break

            idx = BUCKET_IDX[bucket]
            if bucket == "NPA":
                pass  # absorbing state, stays NPA (written off)
            else:
                roll = np.random.random()
                if idx == 0:  # Current
                    if roll < deteriorate_p:
                        bucket = "30 DPD"
                else:
                    # chance to worsen further, chance to cure back to Current,
                    # else stay in same bucket
                    worsen_p = 0.32 + (0.05 if loan["is_bad_vintage"] else 0)
                    cure_p = 0.18 if idx < 3 else 0.05
                    if roll < worsen_p and idx < 4:
                        bucket = BUCKETS[idx + 1]
                    elif roll > (1 - cure_p):
                        bucket = "Current"
                    # else: stays in same bucket this month

            snapshot_rows.append({
                "loan_id": loan["loan_id"],
                "disbursal_month": loan["disbursal_month"],
                "snapshot_month": month_str(cur_date),
                "mob": mob,
                "dpd_bucket": bucket,
            })
    return pd.DataFrame(snapshot_rows)


if __name__ == "__main__":
    loans = generate_loans()
    snapshots = simulate_snapshots(loans)

    loans.to_csv("data/loans.csv", index=False)
    snapshots.to_csv("data/monthly_snapshots.csv", index=False)

    print(f"Loans generated: {len(loans)}")
    print(f"Monthly snapshots generated: {len(snapshots)}")
    print(loans.head())
    print(snapshots.head())
