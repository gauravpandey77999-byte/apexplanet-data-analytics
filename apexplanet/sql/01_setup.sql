-- =====================================================================
-- Task 2 | 01_setup.sql
-- Builds a small relational model from the flat cleaned table `telco_clean`
-- (loaded from data/processed/telco_churn_cleaned.csv by db_utils.load_csv_to_db).
--   customers      -> who the customer is (demographics)
--   services       -> what the customer subscribes to
--   accounts       -> billing, contract, tenure and churn outcome
--   contract_plans -> small lookup table (used to practise LEFT / RIGHT / FULL joins)
-- Dialect: SQLite (also works in PostgreSQL with minor type changes).
-- =====================================================================

DROP VIEW  IF EXISTS v_customer_360;
DROP VIEW  IF EXISTS v_churn_by_contract;
DROP VIEW  IF EXISTS v_tenure_band_summary;
DROP VIEW  IF EXISTS v_high_value_at_risk;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS contract_plans;

CREATE TABLE customers (
    customer_id    TEXT PRIMARY KEY,
    gender         TEXT,
    senior_citizen TEXT,
    partner        TEXT,
    dependents     TEXT
);

CREATE TABLE services (
    customer_id       TEXT PRIMARY KEY,
    phone_service     TEXT,
    multiple_lines    TEXT,
    internet_service  TEXT,
    online_security   TEXT,
    online_backup     TEXT,
    device_protection TEXT,
    tech_support      TEXT,
    streaming_tv      TEXT,
    streaming_movies  TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE accounts (
    customer_id       TEXT PRIMARY KEY,
    tenure            INTEGER,
    contract          TEXT,
    paperless_billing TEXT,
    payment_method    TEXT,
    monthly_charges   REAL,
    total_charges     REAL,
    churn             TEXT,
    churn_flag        INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE contract_plans (
    contract               TEXT PRIMARY KEY,
    commitment_months      INTEGER,
    early_termination_fee  REAL
);

INSERT INTO customers
SELECT customer_id, gender, senior_citizen, partner, dependents FROM telco_clean;

INSERT INTO services
SELECT customer_id, phone_service, multiple_lines, internet_service, online_security,
       online_backup, device_protection, tech_support, streaming_tv, streaming_movies
FROM telco_clean;

INSERT INTO accounts
SELECT customer_id, tenure, contract, paperless_billing, payment_method,
       monthly_charges, total_charges, churn, churn_flag
FROM telco_clean;

-- 'Three year' has no customers on purpose, so LEFT / RIGHT / FULL joins show a visible difference.
INSERT INTO contract_plans (contract, commitment_months, early_termination_fee) VALUES
    ('Month-to-month',  0,   0.0),
    ('One year',       12,  50.0),
    ('Two year',       24, 100.0),
    ('Three year',     36, 150.0);
