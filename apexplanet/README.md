# Apexplanet Data Analytics Project

**ApexPlanet Software Pvt. Ltd. | Data Analytics Internship (45 Days)**

## Overview
- **Objective:** Find out which telecom customers churn and why, using Python and SQL.
- **Dataset:** IBM Telco Customer Churn (7,043 customers, 21 columns), cleaned in Task 1.
- **Key questions answered:**
  - Which contracts, services and tenure groups churn the most?
  - In which months do customers leave?
  - Which active customers are at risk, and how much revenue is that?

## Tech Stack
- Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly
- SQL (SQLite, PostgreSQL-compatible), sqlite3 and SQLAlchemy
- Power BI / Tableau (Task 3)
- Scikit-learn, Statsmodels (Task 4)

## Project Structure

```
apexplanet-data-analytics/
│
├── README.md                          Project documentation (this file)
├── requirements.txt                   Python libraries needed
├── .gitignore                         Files Git should ignore (database, caches)
│
├── data/
│   ├── raw/                           Original dataset (WA_Fn-UseC_-Telco-Customer-Churn.csv)
│   └── processed/                     Cleaned data and SQL exports
│       ├── telco_churn_cleaned.csv        Task 1 output (input for Task 2)
│       ├── cleaning_log.csv               Task 1 cleaning log
│       └── sql_*.csv                      Task 2 exports for the dashboard
│
├── notebooks/
│   ├── 01_eda_telco_churn.ipynb           Task 1: cleaning + EDA
│   ├── 02_sql_basics_beginner.ipynb       Task 2: SQL from basics + Python integration
│   └── 02_sql_data_extraction.ipynb       Task 2: same work using scripts/db_utils.py (optional)
│
├── sql/
│   ├── 01_setup.sql                       Creates customers, services, accounts, contract_plans
│   ├── 02_queries.sql                     26 business queries
│   └── 03_views_indexes.sql               Views + indexes
│
├── scripts/
│   └── db_utils.py                        Reusable database connection module
│
├── reports/
│   └── figures/                           Charts and the final report (Task 5)
│
└── dashboards/                            Power BI / Tableau files (Task 3)
```

## What Each Task Delivers

| Task | Deliverable | Where |
|---|---|---|
| Task 1 | EDA notebook + cleaned dataset | `notebooks/01_eda_telco_churn.ipynb`, `data/processed/telco_churn_cleaned.csv` |
| Task 2 | SQL query files (.sql) | `sql/01_setup.sql`, `sql/02_queries.sql`, `sql/03_views_indexes.sql` |
| Task 2 | Python script for DB connection | `scripts/db_utils.py` |
| Task 2 | Notebook with SQL + Python integration | `notebooks/02_sql_basics_beginner.ipynb` |
| Task 3 | Dashboards | `dashboards/` (coming) |
| Task 4 | Statistical models and forecasts | `notebooks/` (coming) |
| Task 5 | Final report, automation, README | `reports/`, `scripts/` (coming) |

## Task Status
- [x] Task 1: Setup, cleaning and EDA
- [x] Task 2: SQL and data extraction
- [ ] Task 3: Data visualization and dashboards
- [ ] Task 4: Advanced analytics and modeling
- [ ] Task 5: Final reporting and presentation

## SQL Files Explained

| File | Purpose | Run order |
|---|---|---|
| `01_setup.sql` | Splits the flat table into related tables and adds a plan lookup table | 1st |
| `02_queries.sql` | 26 queries: SELECT/WHERE/ORDER BY/LIMIT, all JOINs, GROUP BY/HAVING, subqueries, CTEs, window functions (ROW_NUMBER, RANK, LAG, LEAD), retention, moving average, cumulative sums | 2nd |
| `03_views_indexes.sql` | 4 reusable views and 3 indexes for performance | 3rd |

## Key Findings
1. [Finding 1: copy from the "Key insights" cell in the Task 2 notebook]
2. [Finding 2]
3. [Finding 3]

## Dashboard Link
[Power BI / Tableau Public link: Task 3]

## How to Run
1. Clone the repo:
   `git clone https://github.com/YOUR-USERNAME/apexplanet-data-analytics.git`
2. Install requirements: `pip install -r requirements.txt`
3. Make sure `data/processed/telco_churn_cleaned.csv` exists (run notebook 01 to create it from the raw data in `data/raw/`).
4. Run the notebooks in order:
   - `notebooks/01_eda_telco_churn.ipynb`
   - `notebooks/02_sql_basics_beginner.ipynb`

The database file `data/telco.db` is created automatically when you run the Task 2 notebook.

### Optional: use PostgreSQL instead of SQLite
Set the connection URL before running `02_sql_data_extraction.ipynb`:
```
export DB_URL=postgresql+psycopg2://user:password@localhost:5432/telco
```
(On Windows: `set DB_URL=...`.)

## Author
[Your Name]
Apexplanet Software Pvt. Ltd. Internship
