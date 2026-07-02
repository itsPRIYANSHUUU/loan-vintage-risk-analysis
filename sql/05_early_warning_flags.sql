-- 05_early_warning_flags.sql
-- Decision-ready output: which cohorts and which customer segments need action.

-- [1] Risky vintages: cohorts whose 60+DPD rate at MOB=6 exceeds 10%
SELECT
    disbursal_month,
    ROUND(
        100.0 * SUM(CASE WHEN dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS pct_60plus_at_mob6
FROM monthly_snapshots
WHERE mob = 6
GROUP BY disbursal_month
HAVING
    100.0 * SUM(CASE WHEN dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
    / COUNT(*) > 10
ORDER BY pct_60plus_at_mob6 DESC;


-- [2] Risky segment x city-tier combinations: overall 60+DPD rate exceeding 8%
SELECT
    l.segment,
    l.city_tier,
    COUNT(*) AS total_snapshots,
    ROUND(
        100.0 * SUM(CASE WHEN s.dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS pct_60plus
FROM monthly_snapshots s
JOIN loans l ON l.loan_id = s.loan_id
GROUP BY l.segment, l.city_tier
HAVING
    100.0 * SUM(CASE WHEN s.dpd_bucket IN ('60 DPD', '90 DPD', 'NPA') THEN 1 ELSE 0 END)
    / COUNT(*) > 8
ORDER BY pct_60plus DESC;
