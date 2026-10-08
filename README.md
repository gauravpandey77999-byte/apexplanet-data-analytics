# ApexPlanet Data Analytics Internship

An end-to-end data analytics repository developed during the Data Analytics Internship at ApexPlanet. This project encompasses data ingestion, exploratory data analysis (EDA), automated data cleaning pipelines, business intelligence dashboards, and stakeholder reporting.

---

## 📁 Repository Structure

```text
apexplanet-data-analytics/
├── data/
│   ├── raw/               # Immutable source datasets
│   └── processed/         # Cleaned, transformed data ready for analysis & BI
├── notebooks/             # Jupyter notebooks for EDA and hypothesis testing
├── scripts/               # Modular, production-ready Python automation scripts
├── reports/               # Executive summaries, presentations (PPTX), and PDF reports
├── dashboards/            # Interactive dashboard source files (PBIX / TWBX)
└── README.md              # Project documentation and setup guidelines


🛠️ Tech Stack & Dependencies
Language: Python 3.10

.Data Manipulation & Math: pandas, numpy

.Visualization: matplotlib, seaborn, plotly

.Machine Learning / Preprocessing: scikit-learn

.Database & SQL: sqlalchemy

.BI & Reporting: Power BI / Tableau, Microsoft Excel

⚙️ Environment Setup
To reproduce the analysis locally, configure the isolated Conda virtual environment:

1. Clone or Download Repository
Bash
git clone [https://github.com/](https://github.com/)<your-username>/apexplanet-data-analytics.git
cd apexplanet-data-analytics
2. Create and Activate Virtual Environment
Bash
# Using Conda
conda create -n analytics python=3.10 -y
conda activate analytics

# Alternatively, using Python venv
python -m venv analytics
source analytics/bin/activate   # On Linux/macOS
.\analytics\Scripts\activate    # On Windows
3. Install Required Packages
Bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn sqlalchemy openpyxl ipykernel
🔄 Project Workflow
Data Ingestion: Source datasets are loaded directly into data/raw/ without manual edits.

Exploratory Data Analysis (EDA): Notebooks in notebooks/ identify distributions, missing values, anomalies, and correlations.

Data Cleaning & Pipeline: Reusable transformation logic is modularized in scripts/ and outputs clean data into data/processed/.

BI & Dashboarding: Processed files feed interactive dashboards stored in dashboards/ for KPI monitoring.

Business Deliverables: Key business findings, metric breakdowns, and strategic recommendations are summarized in reports/.

👤 Author
Name: Gaurav Pandey

Role: Data Analytics Intern

Organization: ApexPlanet

GitHub:github.com/gauravpandey77999-byte

LinkedIn: linkedin.com/in/gauravpandey777
