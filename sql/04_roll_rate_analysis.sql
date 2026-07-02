-- 04_roll_rate_analysis.sql
-- Roll-rate analysis: for every loan, pair this month's DPD bucket with next
-- month's bucket using LEAD() -- a classic window function use case.

-- Step 1: build the transition pairs (reused by both queries below via CTE)
WITH transitions AS (
    SELECT
        loan_id,
        snapshot_month,
        mob,
        dpd_bucket,
        LEAD(dpd_bucket) OVER (PARTITION BY loan_id ORDER BY mob) AS next_bucket
    FROM monthly_snapshots
)

-- Overall transition matrix, pivoted with conditional aggregation
-- (no extension needed -- this pattern shows up constantly in real SQL interviews)
SELECT
    dpd_bucket AS bucket_this_month,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = 'Current' THEN 1 ELSE 0 END) / COUNT(*), 1) AS to_current,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = '30 DPD'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS to_30_dpd,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = '60 DPD'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS to_60_dpd,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = '90 DPD'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS to_90_dpd,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = 'NPA'     THEN 1 ELSE 0 END) / COUNT(*), 1) AS to_npa
FROM transitions
WHERE next_bucket IS NOT NULL
GROUP BY dpd_bucket
ORDER BY CASE dpd_bucket
    WHEN 'Current' THEN 1 WHEN '30 DPD' THEN 2 WHEN '60 DPD' THEN 3
    WHEN '90 DPD' THEN 4 WHEN 'NPA' THEN 5 END;


-- Early warning KPI: % of 30-DPD loans that roll to 60-DPD, tracked monthly.
-- This is the metric that moves BEFORE the headline NPA% does -- watch this,
-- not just the final default number.

WITH transitions AS (
    SELECT
        loan_id,
        snapshot_month,
        mob,
        dpd_bucket,
        LEAD(dpd_bucket) OVER (PARTITION BY loan_id ORDER BY mob) AS next_bucket
    FROM monthly_snapshots
)
SELECT
    snapshot_month,
    COUNT(*) AS loans_in_30dpd,
    ROUND(100.0 * SUM(CASE WHEN next_bucket = '60 DPD' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_30_to_60_roll
FROM transitions
WHERE dpd_bucket = '30 DPD' AND next_bucket IS NOT NULL
GROUP BY snapshot_month
ORDER BY snapshot_month;
