-- 02_load_data.sql
-- Run this with psql (it uses \copy, which is a psql client-side command,
-- so it works even without server-side file access permissions):
--
--   psql -U postgres -d loan_risk -f sql/02_load_data.sql
--
-- Adjust the file paths below if you run this from a different working directory.

\copy loans FROM 'data/loans.csv' WITH (FORMAT csv, HEADER true);
\copy monthly_snapshots(loan_id, disbursal_month, snapshot_month, mob, dpd_bucket) FROM 'data/monthly_snapshots.csv' WITH (FORMAT csv, HEADER true);
