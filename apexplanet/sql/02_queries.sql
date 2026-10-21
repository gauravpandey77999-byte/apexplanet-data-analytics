-- =====================================================================
-- Task 2 | 02_queries.sql   (26 queries, IBM Telco Customer Churn)
-- Each query starts with a "-- name: <id>" marker so db_utils.load_queries()
-- can load them into Python. Run 01_setup.sql first.
-- Dialect: SQLite 3.39+ (RIGHT / FULL JOIN need 3.39+). Works in PostgreSQL
-- with small changes (see README).
-- NOTE: Telco is a snapshot with no order dates, so "monthly" = tenure month
-- (months since the customer joined).
-- =====================================================================


-- ######################  A. SQL FUNDAMENTALS  ######################

-- name: q01_preview_accounts
SELECT *
FROM accounts
LIMIT 10;

-- name: q02_high_bill_churners
SELECT customer_id, tenure, contract, monthly_charges
FROM accounts
WHERE churn = 'Yes'
  AND monthly_charges > 80
ORDER BY monthly_charges DESC
LIMIT 15;

-- name: q03_top10_highest_monthly_bills
SELECT customer_id, contract, tenure, monthly_charges, churn
FROM accounts
ORDER BY monthly_charges DESC
LIMIT 10;

-- name: q04_distinct_payment_methods
SELECT DISTINCT payment_method
FROM accounts
ORDER BY payment_method;

-- name: q05_inner_join_senior_fiber
SELECT c.customer_id, c.gender, c.senior_citizen,
       s.internet_service, a.contract, a.monthly_charges, a.churn
FROM customers c
INNER JOIN accounts a ON a.customer_id = c.customer_id
INNER JOIN services s ON s.customer_id = c.customer_id
WHERE c.senior_citizen = 'Yes'
  AND s.internet_service = 'Fiber optic'
ORDER BY a.monthly_charges DESC
LIMIT 20;

-- name: q06_left_join_plans_with_customer_counts
SELECT p.contract, p.commitment_months, COUNT(a.customer_id) AS customers
FROM contract_plans p
LEFT JOIN accounts a ON a.contract = p.contract
GROUP BY p.contract, p.commitment_months
ORDER BY p.commitment_months;

-- name: q07_right_join_plans_without_customers
SELECT p.contract AS unused_plan, p.commitment_months
FROM accounts a
RIGHT JOIN contract_plans p ON a.contract = p.contract
WHERE a.customer_id IS NULL;

-- name: q08_full_join_plans_vs_usage
SELECT COALESCE(p.contract, x.contract) AS contract,
       p.commitment_months,
       COALESCE(x.customers, 0)         AS customers
FROM contract_plans p
FULL JOIN (SELECT contract, COUNT(*) AS customers
           FROM accounts
           GROUP BY contract) x ON p.contract = x.contract
ORDER BY p.commitment_months;

-- name: q09_churn_by_contract
SELECT contract,
       COUNT(*)                          AS customers,
       SUM(churn_flag)                   AS churned,
       ROUND(100.0 * AVG(churn_flag), 1) AS churn_rate_pct,
       ROUND(AVG(monthly_charges), 2)    AS avg_monthly,
       MIN(monthly_charges)              AS min_monthly,
       MAX(monthly_charges)              AS max_monthly
FROM accounts
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- name: q10_having_risky_payment_methods
SELECT payment_method,
       COUNT(*)                          AS customers,
       ROUND(100.0 * AVG(churn_flag), 1) AS churn_rate_pct
FROM accounts
GROUP BY payment_method
HAVING COUNT(*) > 500
   AND AVG(churn_flag) > 0.20
ORDER BY churn_rate_pct DESC;

-- name: q11_subquery_above_average_bill
SELECT CASE WHEN monthly_charges > (SELECT AVG(monthly_charges) FROM accounts)
            THEN 'Above average bill'
            ELSE 'At or below average' END AS bill_level,
       COUNT(*)                          AS customers,
       ROUND(100.0 * AVG(churn_flag), 1) AS churn_rate_pct
FROM accounts
GROUP BY bill_level;

-- name: q12_cte_tenure_bands
WITH banded AS (
    SELECT customer_id, churn_flag, monthly_charges,
           CASE WHEN tenure <= 12 THEN '0-12'
                WHEN tenure <= 24 THEN '13-24'
                WHEN tenure <= 48 THEN '25-48'
                ELSE '49-72' END AS tenure_group
    FROM accounts
)
SELECT tenure_group,
       COUNT(*)                          AS customers,
       ROUND(100.0 * AVG(churn_flag), 1) AS churn_rate_pct,
       ROUND(AVG(monthly_charges), 2)    AS avg_monthly
FROM banded
GROUP BY tenure_group
ORDER BY tenure_group;

-- name: q13_window_row_number_top3_per_contract
WITH ranked AS (
    SELECT customer_id, contract, tenure, total_charges,
           ROW_NUMBER() OVER (PARTITION BY contract ORDER BY total_charges DESC) AS rn
    FROM accounts
)
SELECT contract, rn AS position, customer_id, tenure, total_charges
FROM ranked
WHERE rn <= 3
ORDER BY contract, rn;

-- name: q14_window_rank_payment_methods
WITH pm AS (
    SELECT payment_method,
           COUNT(*)                   AS customers,
           100.0 * AVG(churn_flag)    AS churn_rate
    FROM accounts
    GROUP BY payment_method
)
SELECT RANK() OVER (ORDER BY churn_rate DESC) AS churn_rank,
       payment_method, customers, ROUND(churn_rate, 1) AS churn_rate_pct
FROM pm
ORDER BY churn_rank;

-- name: q15_window_lag_lead_first_year
WITH m AS (
    SELECT tenure, ROUND(AVG(monthly_charges), 2) AS avg_monthly
    FROM accounts
    WHERE tenure BETWEEN 1 AND 12
    GROUP BY tenure
)
SELECT tenure, avg_monthly,
       LAG(avg_monthly)  OVER (ORDER BY tenure) AS prev_month,
       LEAD(avg_monthly) OVER (ORDER BY tenure) AS next_month,
       ROUND(avg_monthly - LAG(avg_monthly) OVER (ORDER BY tenure), 2) AS change_vs_prev
FROM m
ORDER BY tenure;


-- ######################  B. ADVANCED SQL: BUSINESS PROBLEMS  ######################

-- name: q16_tenure_month_trend
-- "Monthly sales trend" equivalent: customers and recurring revenue by tenure month.
SELECT tenure                          AS tenure_month,
       COUNT(*)                        AS customers,
       SUM(churn_flag)                 AS churned,
       ROUND(SUM(monthly_charges), 2)  AS monthly_revenue,
       ROUND(AVG(monthly_charges), 2)  AS avg_monthly_charge
FROM accounts
WHERE tenure BETWEEN 1 AND 24
GROUP BY tenure
ORDER BY tenure;

-- name: q17_top10_customers_by_revenue
SELECT c.customer_id, c.senior_citizen, s.internet_service,
       a.contract, a.tenure, a.total_charges, a.churn
FROM customers c
JOIN accounts a ON a.customer_id = c.customer_id
JOIN services s ON s.customer_id = c.customer_id
ORDER BY a.total_charges DESC
LIMIT 10;

-- name: q18_retention_rate_contract_by_tenure_band
WITH base AS (
    SELECT contract, churn_flag,
           CASE WHEN tenure <= 12 THEN '0-12'
                WHEN tenure <= 24 THEN '13-24'
                WHEN tenure <= 48 THEN '25-48'
                ELSE '49-72' END AS tenure_group
    FROM accounts
)
SELECT contract, tenure_group,
       COUNT(*)                                AS customers,
       ROUND(100.0 * (1 - AVG(churn_flag)), 1) AS retention_rate_pct
FROM base
GROUP BY contract, tenure_group
ORDER BY contract, tenure_group;

-- name: q19_monthly_churn_hazard
-- Life-table logic: at_risk(t) = customers who stayed at least t months.
WITH by_t AS (
    SELECT tenure, COUNT(*) AS customers, SUM(churn_flag) AS churned
    FROM accounts
    WHERE tenure >= 1
    GROUP BY tenure
),
risk AS (
    SELECT tenure, churned,
           SUM(customers) OVER (ORDER BY tenure
                                ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS at_risk
    FROM by_t
)
SELECT tenure AS tenure_month, at_risk, churned,
       ROUND(100.0 * churned / at_risk, 2) AS monthly_churn_rate_pct
FROM risk
WHERE tenure <= 24
ORDER BY tenure;

-- name: q20_service_category_performance
SELECT s.internet_service,
       COUNT(*)                                   AS customers,
       ROUND(SUM(a.total_charges), 2)             AS lifetime_revenue,
       ROUND(100.0 * SUM(a.total_charges) / SUM(SUM(a.total_charges)) OVER (), 1) AS revenue_share_pct,
       ROUND(AVG(a.monthly_charges), 2)           AS avg_monthly,
       ROUND(100.0 * AVG(a.churn_flag), 1)        AS churn_rate_pct
FROM services s
JOIN accounts a ON a.customer_id = s.customer_id
GROUP BY s.internet_service
ORDER BY lifetime_revenue DESC;

-- name: q21_addon_service_performance
SELECT 'online_security' AS addon, COUNT(*) AS subscribers,
       ROUND(100.0 * AVG(a.churn_flag), 1) AS churn_rate_pct, ROUND(AVG(a.monthly_charges), 2) AS avg_monthly
FROM services s JOIN accounts a USING (customer_id) WHERE s.online_security = 'Yes'
UNION ALL
SELECT 'online_backup', COUNT(*), ROUND(100.0 * AVG(a.churn_flag), 1), ROUND(AVG(a.monthly_charges), 2)
FROM services s JOIN accounts a USING (customer_id) WHERE s.online_backup = 'Yes'
UNION ALL
SELECT 'device_protection', COUNT(*), ROUND(100.0 * AVG(a.churn_flag), 1), ROUND(AVG(a.monthly_charges), 2)
FROM services s JOIN accounts a USING (customer_id) WHERE s.device_protection = 'Yes'
UNION ALL
SELECT 'tech_support', COUNT(*), ROUND(100.0 * AVG(a.churn_flag), 1), ROUND(AVG(a.monthly_charges), 2)
FROM services s JOIN accounts a USING (customer_id) WHERE s.tech_support = 'Yes'
UNION ALL
SELECT 'streaming_tv', COUNT(*), ROUND(100.0 * AVG(a.churn_flag), 1), ROUND(AVG(a.monthly_charges), 2)
FROM services s JOIN accounts a USING (customer_id) WHERE s.streaming_tv = 'Yes'
UNION ALL
SELECT 'streaming_movies', COUNT(*), ROUND(100.0 * AVG(a.churn_flag), 1), ROUND(AVG(a.monthly_charges), 2)
FROM services s JOIN accounts a USING (customer_id) WHERE s.streaming_movies = 'Yes'
ORDER BY churn_rate_pct;

-- name: q22_moving_average_monthly_charge
WITH t AS (
    SELECT tenure, AVG(monthly_charges) AS avg_monthly
    FROM accounts
    WHERE tenure BETWEEN 1 AND 36
    GROUP BY tenure
)
SELECT tenure AS tenure_month,
       ROUND(avg_monthly, 2) AS avg_monthly_charge,
       ROUND(AVG(avg_monthly) OVER (ORDER BY tenure ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m
FROM t
ORDER BY tenure;

-- name: q23_cumulative_customers_and_revenue
WITH t AS (
    SELECT tenure, COUNT(*) AS customers, SUM(monthly_charges) AS revenue
    FROM accounts
    GROUP BY tenure
)
SELECT tenure AS tenure_month,
       customers,
       SUM(customers) OVER (ORDER BY tenure)                                  AS cumulative_customers,
       ROUND(100.0 * SUM(customers) OVER (ORDER BY tenure) / SUM(customers) OVER (), 1) AS cumulative_pct,
       ROUND(SUM(revenue) OVER (ORDER BY tenure), 2)                          AS cumulative_monthly_revenue
FROM t
ORDER BY tenure;

-- name: q24_risk_segments
WITH seg AS (
    SELECT a.churn_flag, a.monthly_charges,
           CASE WHEN a.contract = 'Month-to-month'
                 AND s.internet_service = 'Fiber optic'
                 AND a.tenure <= 12 THEN '1 High risk: month-to-month + fiber + new'
                WHEN a.contract = 'Month-to-month'  THEN '2 Medium risk: other month-to-month'
                ELSE '3 Lower risk: 1-2 year contract' END AS risk_segment
    FROM accounts a
    JOIN services s ON s.customer_id = a.customer_id
)
SELECT risk_segment,
       COUNT(*)                          AS customers,
       ROUND(100.0 * AVG(churn_flag), 1) AS churn_rate_pct,
       ROUND(AVG(monthly_charges), 2)    AS avg_monthly
FROM seg
GROUP BY risk_segment
ORDER BY risk_segment;

-- name: q25_revenue_lost_to_churn
WITH r AS (
    SELECT contract,
           SUM(monthly_charges) AS total_monthly_revenue,
           SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) AS lost_monthly_revenue
    FROM accounts
    GROUP BY contract
)
SELECT contract,
       ROUND(total_monthly_revenue, 2) AS total_monthly_revenue,
       ROUND(lost_monthly_revenue, 2)  AS lost_monthly_revenue,
       ROUND(100.0 * lost_monthly_revenue / total_monthly_revenue, 1)         AS pct_of_contract_revenue_lost,
       ROUND(100.0 * lost_monthly_revenue / SUM(lost_monthly_revenue) OVER (), 1) AS pct_of_all_lost_revenue
FROM r
ORDER BY lost_monthly_revenue DESC;

-- name: q26_senior_partner_segments
SELECT c.senior_citizen, c.partner,
       COUNT(*)                          AS customers,
       ROUND(100.0 * AVG(a.churn_flag), 1) AS churn_rate_pct,
       ROUND(AVG(a.monthly_charges), 2)  AS avg_monthly
FROM customers c
JOIN accounts a ON a.customer_id = c.customer_id
GROUP BY c.senior_citizen, c.partner
ORDER BY churn_rate_pct DESC;
