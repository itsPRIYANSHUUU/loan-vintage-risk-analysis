-- 01_schema.sql
-- Creates the two tables that back the entire analysis.

DROP TABLE IF EXISTS monthly_snapshots;
DROP TABLE IF EXISTS loans;

CREATE TABLE loans (
    loan_id             VARCHAR(10) PRIMARY KEY,
    disbursal_month     CHAR(7)       NOT NULL,   -- 'YYYY-MM'
    disbursal_date      DATE          NOT NULL,
    segment             VARCHAR(20)   NOT NULL,    -- Salaried / Self-Employed
    city_tier           VARCHAR(10)   NOT NULL,    -- Tier 1 / Tier 2 / Tier 3
    loan_amount         NUMERIC(12,2) NOT NULL,
    tenure_months       INT           NOT NULL,
    interest_rate       NUMERIC(5,2)  NOT NULL,
    bureau_risk_score   INT           NOT NULL,
    is_bad_vintage      BOOLEAN       NOT NULL
);

CREATE TABLE monthly_snapshots (
    loan_id             VARCHAR(10) REFERENCES loans(loan_id),
    disbursal_month     CHAR(7)     NOT NULL,
    snapshot_month      CHAR(7)     NOT NULL,   -- 'YYYY-MM'
    mob                 INT         NOT NULL,   -- months on book
    dpd_bucket          VARCHAR(10) NOT NULL    -- Current / 30 DPD / 60 DPD / 90 DPD / NPA
);

CREATE INDEX idx_snapshots_loan_mob ON monthly_snapshots(loan_id, mob);
CREATE INDEX idx_snapshots_month ON monthly_snapshots(snapshot_month);
