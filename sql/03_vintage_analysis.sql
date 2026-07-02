-- 03_vintage_analysis.sql
-- Vintage curve: % of each disbursal cohort in 60+ DPD, by months-on-book (MOB).
-- Business read: compare cohorts at the SAME mob to see which month's approvals
-- are aging worse -- a signal to review that month's underwriting.

SELECT
    disbursal_month,
    mob,
    COUNT(*) AS loans_in_cohort_at_mob,
    ROUND(
        100.0 * SUM(CASE WHEN dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS pct_60plus_dpd
FROM monthly_snapshots
GROUP BY disbursal_month, mob
ORDER BY disbursal_month, mob;


-- Fair, apples-to-apples cohort comparison: rank vintages by their 60+DPD rate
-- at a fixed checkpoint (MOB = 6), instead of comparing cohorts at different ages.

SELECT
    disbursal_month,
    ROUND(
        100.0 * SUM(CASE WHEN dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS pct_60plus_at_mob6
FROM monthly_snapshots
WHERE mob = 6
GROUP BY disbursal_month
ORDER BY pct_60plus_at_mob6 DESC
LIMIT 5;
