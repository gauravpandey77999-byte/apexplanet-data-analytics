-- =====================================================================
-- Task 2 | 03_views_indexes.sql
-- Reusable views for frequently used queries + indexes for performance.
-- Run AFTER 01_setup.sql.
-- =====================================================================

DROP VIEW IF EXISTS v_customer_360;
CREATE VIEW v_customer_360 AS
SELECT c.customer_id, c.gender, c.senior_citizen, c.partner, c.dependents,
       s.phone_service, s.internet_service, s.online_security, s.online_backup,
       s.device_protection, s.tech_support, s.streaming_tv, s.streaming_movies,
       a.tenure, a.contract, a.paperless_billing, a.payment_method,
       a.monthly_charges, a.total_charges, a.churn, a.churn_flag
FROM customers c
JOIN services s ON s.customer_id = c.customer_id
JOIN accounts a ON a.customer_id = c.customer_id;

DROP VIEW IF EXISTS v_churn_by_contract;
CREATE VIEW v_churn_by_contract AS
SELECT contract,
       COUNT(*)                              AS customers,
       SUM(churn_flag)                       AS churned,
       ROUND(100.0 * AVG(churn_flag), 1)     AS churn_rate_pct,
       ROUND(AVG(monthly_charges), 2)        AS avg_monthly_charges
FROM accounts
GROUP BY contract;

DROP VIEW IF EXISTS v_tenure_band_summary;
CREATE VIEW v_tenure_band_summary AS
SELECT CASE WHEN tenure <= 12 THEN '0-12'
            WHEN tenure <= 24 THEN '13-24'
            WHEN tenure <= 48 THEN '25-48'
            ELSE '49-72' END                AS tenure_group,
       COUNT(*)                              AS customers,
       ROUND(100.0 * AVG(churn_flag), 1)     AS churn_rate_pct,
       ROUND(AVG(monthly_charges), 2)        AS avg_monthly_charges,
       ROUND(SUM(monthly_charges), 2)        AS monthly_revenue
FROM accounts
GROUP BY 1;

-- Active customers who look like the churners: month-to-month, high bill, still new.
DROP VIEW IF EXISTS v_high_value_at_risk;
CREATE VIEW v_high_value_at_risk AS
SELECT customer_id, internet_service, contract, tenure, monthly_charges, payment_method
FROM v_customer_360
WHERE churn = 'No'
  AND contract = 'Month-to-month'
  AND monthly_charges >= 80
  AND tenure <= 12;

-- Indexes on columns used in WHERE / JOIN / GROUP BY
CREATE INDEX IF NOT EXISTS idx_accounts_contract     ON accounts (contract);
CREATE INDEX IF NOT EXISTS idx_accounts_churn_tenure ON accounts (churn, tenure);
CREATE INDEX IF NOT EXISTS idx_services_internet     ON services (internet_service);
