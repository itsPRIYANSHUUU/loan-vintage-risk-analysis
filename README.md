# Loan Portfolio Vintage & Roll-Rate Analysis
### Early Warning System for Credit Risk Monitoring in NBFC/Bank Lending

## Why this project exists

Most fresher data analyst portfolios have a fraud-detection or churn model. Very few
have this — **vintage analysis and roll-rate analysis**, which is how actual credit
risk teams at banks and NBFCs monitor a loan book *before* losses show up on the
balance sheet.

The core idea: don't wait for a loan to default. Watch how fast it moves through
delinquency stages, and which batch of loans ("vintage") is behaving worse than
expected. This is the language used in RBI-regulated lending risk reviews, and it's
a genuinely different skill set from a generic ML classifier.

## Business Questions This Project Answers

1. **Which month's loan approvals are turning out worse than others?** (Vintage analysis)
2. **How fast are delinquent loans deteriorating vs. curing?** (Roll-rate / transition matrix)
3. **Is there an early-warning KPI that moves before the headline NPA% does?** (30→60 DPD roll rate trend)
4. **Which customer segments need tighter underwriting or pricing?** (Segment-level flagging)

## Data (Simulated)

Real bank loan tapes aren't public, so this project simulates an 18-month loan book
(~4,000 loans) with realistic risk dynamics — including one deliberately "bad vintage"
quarter, to prove the method actually detects it. Attributes: disbursal month, loan
amount, tenure, segment (Salaried/Self-Employed), city tier, bureau-style risk score,
and a monthly DPD (Days Past Due) bucket: `Current → 30 DPD → 60 DPD → 90 DPD → NPA`.

## Project Structure

```
loan-vintage-project/
├── generate_data.py                    # simulates the loan portfolio + monthly DPD snapshots
├── analysis/
│   ├── vintage_analysis.py             # vintage curves by cohort
│   ├── roll_rate_analysis.py           # transition matrix + early warning KPI trend
│   ├── early_warning_flags.py          # decision-ready risk flags
│   └── powerbi_export.py               # exports star-schema CSVs for Power BI
├── sql/                                # same analysis, rewritten in pure PostgreSQL
│   ├── 01_schema.sql
│   ├── 02_load_data.sql
│   ├── 03_vintage_analysis.sql
│   ├── 04_roll_rate_analysis.sql
│   ├── 05_early_warning_flags.sql
│   └── README.md                       # SQL-specific setup + run instructions
├── data/                               # generated loan-level + snapshot data
└── outputs/                            # charts, flagged reports, Power BI-ready exports
```

> Two ways to explore this project: run the **Python** pipeline for the full
> workflow with charts, or the **SQL** version (`sql/`) if you want to see the
> same analysis done with window functions and CTEs in PostgreSQL.

## Key Findings (from the simulated data)

- **Loans disbursed in June–August 2025 are the worst-performing cohort**: 12–18%
  are in 60+ DPD by month 6, vs. 5–9% for other months — a clear signal that
  underwriting quality slipped that quarter.
- **Roll-rate matrix**: once a loan hits 30 DPD, it has roughly a 1-in-3 chance of
  worsening to 60 DPD the next month, and only about a 1-in-6 chance of curing back
  to current.
- **Segment risk**: Self-Employed borrowers in Tier 2/3 cities and Salaried borrowers
  in Tier 3 cities show the highest 60+DPD rates — candidates for tighter limits or
  risk-based pricing.

See `outputs/early_warning_report.txt` for the full flagged list, and
`outputs/vintage_curves.png` / `outputs/roll_rate_heatmap.png` for the visuals.

# Dashboard & Visualizations

## 1. Vintage Curve Analysis

![Vintage Curve](images/vintage%20curve.png)

---

## 2. Roll Rate Transition Matrix

![Roll Rate Heatmap](images/roll%20rate%20heatmap.png)

---

## 3. Early Warning KPI Trend

![Early Warning Trend](images/early%20warning%20trend.png)

## How to Run

```bash
pip install pandas numpy python-dateutil matplotlib seaborn
python generate_data.py
python analysis/vintage_analysis.py
python analysis/roll_rate_analysis.py
python analysis/early_warning_flags.py
python analysis/powerbi_export.py
```

## Building the Power BI Dashboard

1. Open Power BI Desktop → Get Data → Text/CSV
2. Import `outputs/powerbi/fact_snapshots.csv` and `outputs/powerbi/dim_loans.csv`
3. Create a relationship: `fact_snapshots[loan_id]` → `dim_loans[loan_id]`
4. Suggested visuals:
   - Line chart: vintage curves (use `outputs/vintage_curve_data.csv`) — X = MOB, Y = % 60+DPD, legend = disbursal_month
   - Matrix/heatmap: `outputs/transition_matrix.csv`
   - KPI card + trend line: 30→60 DPD roll rate over time
   - Slicers: segment, city tier, disbursal month

## What This Demonstrates (for interviews)

- Understanding of core credit risk metrics used in BFSI (vintage curves, roll rates,
  DPD buckets) — not just applying a generic ML model to a Kaggle dataset
- Python for simulation and cohort-based aggregation (`pandas.groupby`, crosstab-based
  transition matrices)
- SQL fluency: the exact same analysis rewritten in PostgreSQL using `LEAD()` window
  functions, CTEs, and conditional-aggregation pivots (see `sql/`) — the patterns most
  BFSI SQL interviews actually test
- Translating analysis into **decision-ready output** (the early warning report), which
  is what separates an analyst from a script-runner
- Power BI dashboard-readiness with a proper star schema

## Disclaimer

All data is synthetically generated for demonstration purposes and does not represent
any real financial institution's portfolio.
