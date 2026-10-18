# ApexPlanet Data Analytics Internship Project

**Author:** Gaurav Pandey
**Internship:** ApexPlanet Software Pvt. Ltd. | Data Analytics (45 Days)

## Task 1: Foundational Setup & Exploratory Data Analysis

### Overview
- **Objective:** Set up the analytics environment, clean the data, and explore it to find what drives customer churn.
- **Dataset:** IBM Telco Customer Churn (7,043 customers, 21 columns). Each row is one customer, and the target column is `Churn` (Yes/No).
- **Key questions answered:**
  - What share of customers churn?
  - Which contract types, services and customer groups churn the most?
  - How do tenure and monthly charges relate to churn?

### Tech Stack
- Python, Pandas, NumPy, Matplotlib, Seaborn
- Jupyter Notebook
- Git / GitHub

### Project Structure
```
apexplanet-data-analytics/
├── data/
│   ├── raw/          original CSV (untouched)
│   └── processed/    telco_churn_cleaned.csv + cleaning_log.csv
├── notebooks/        01_eda_telco_churn.ipynb
├── scripts/          Python scripts (later tasks)
├── reports/          PDF/PPT (later tasks)
├── dashboards/       PBIX/TWBX files (later tasks)
├── figures/          charts exported by the notebook
├── requirements.txt
└── README.md
```

### Data Cleaning Summary
- Renamed all columns to snake_case
- Removed duplicates (none found)
- `total_charges` was stored as text with 11 hidden blank values (all customers with tenure = 0, i.e. not billed yet). Converted to numeric and set those to 0
- Converted text columns to `category`, `senior_citizen` from 0/1 to No/Yes
- Checked outliers with the IQR method and documented them
- Full step-by-step record: `data/processed/cleaning_log.csv`

### Key Findings
1. **Contract type is the biggest churn driver.** Month-to-month customers churn far more than one- and two-year customers.
2. **New customers leave the most.** Churn is highest in the first 12 months and falls as tenure grows.
3. **Fiber-optic users and customers without security/tech-support add-ons churn more.**

(Exact percentages are in the notebook, section 4.4 and 5.)

### How to Run
1. Clone the repo
2. Install requirements: `pip install -r requirements.txt`
3. Download the dataset from Kaggle ("Telco Customer Churn" by blastchar) and place `WA_Fn-UseC_-Telco-Customer-Churn.csv` in `data/raw/`
4. Run `notebooks/01_eda_telco_churn.ipynb` from top to bottom

### Author
Gaurav Pandey
ApexPlanet Software Pvt. Ltd. Internship
