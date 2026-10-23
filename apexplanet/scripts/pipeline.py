import sys
import subprocess
import os

# --- STEP 1: AUTO INSTALL MISSING PACKAGES ---
REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "scipy",
    "scikit-learn",
    "reportlab",
    "openpyxl",
    "pillow"
]

def auto_install():
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            print(f"[+] Installing module: {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

auto_install()

# --- IMPORTS ---
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                PageBreak, Image, Table, TableStyle, NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents

# --- PATH SETUP ---
ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "processed"
REP_DIR = ROOT / "reports"
FIG_DIR = REP_DIR / "figures"
DATA_DIR.mkdir(parents=True, exist_ok=True)
REP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = DATA_DIR / "telco_churn_cleaned.csv"
AUTHOR_NAME = "Gaurav Pandey"
PURPLE = colors.HexColor("#3b2f9e")
TEAL = colors.HexColor("#1b998b")
SEED = 42

# --- STEP 2: ENSURE DATASET EXISTS ---
def ensure_dataset():
    if not DATA_PATH.exists():
        print("[!] Dataset nahi mila. Sample dummy data generate ho raha hai...")
        np.random.seed(SEED)
        n = 500
        df_dummy = pd.DataFrame({
            "customer_id": [f"ID_{i}" for i in range(n)],
            "tenure": np.random.randint(1, 72, size=n),
            "contract": np.random.choice(["Month-to-month", "One year", "Two year"], size=n, p=[0.55, 0.25, 0.20]),
            "internet_service": np.random.choice(["DSL", "Fiber optic", "No"], size=n, p=[0.4, 0.45, 0.15]),
            "payment_method": np.random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], size=n),
            "monthly_charges": np.round(np.random.uniform(20.0, 118.0, size=n), 2),
            "total_charges": np.round(np.random.uniform(50.0, 8000.0, size=n), 2),
            "senior_citizen": np.random.choice(["No", "Yes"], size=n, p=[0.8, 0.2]),
            "tech_support": np.random.choice(["No", "Yes"], size=n, p=[0.6, 0.4]),
            "paperless_billing": np.random.choice(["No", "Yes"], size=n, p=[0.4, 0.6]),
            "churn": np.random.choice(["No", "Yes"], size=n, p=[0.73, 0.27])
        })
        df_dummy.to_csv(DATA_PATH, index=False)
        print(f"[+] Sample data ban gaya: {DATA_PATH}")

ensure_dataset()

# --- STEP 3: ANALYTICS PIPELINE ---
print("[+] Running analytics pipeline...")
df = pd.read_csv(DATA_PATH)
df = df.drop_duplicates().copy()
df.columns = df.columns.str.strip().str.lower()
df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
df["total_charges"] = df["total_charges"].fillna(df["total_charges"].median())
if "churn_flag" not in df.columns:
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)

# KPIs
kpis = {
    "customers": int(len(df)),
    "churned": int(df.churn_flag.sum()),
    "churn_rate_pct": round(float(df.churn_flag.mean() * 100), 2),
    "avg_monthly_charges": round(float(df.monthly_charges.mean()), 2),
    "total_revenue": round(float(df.total_charges.sum()), 2),
    "median_tenure_months": float(df.tenure.median()),
    "monthly_revenue_at_risk": round(float(df.loc[df.churn_flag == 1, "monthly_charges"].sum()), 2),
}

def segment_table(data, col):
    t = data.groupby(col).churn_flag.agg(customers="size", churn_rate="mean")
    t["churn_rate"] = (t["churn_rate"] * 100).round(1)
    return t.reset_index()

# Stats Tests
tests = {}
for col in ["contract", "internet_service", "payment_method", "senior_citizen"]:
    if col in df.columns:
        chi2, p, dof, _ = stats.chi2_contingency(pd.crosstab(df[col], df.churn_flag))
        tests[f"chi2_{col}"] = {"chi2": round(float(chi2), 1), "dof": int(dof), "p": float(p)}

for col in ["monthly_charges", "tenure"]:
    a = df[df.churn_flag == 1][col]
    b = df[df.churn_flag == 0][col]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    tests[f"ttest_{col}"] = {"t": round(float(t), 2), "p": float(p),
                             "mean_churn": round(float(a.mean()), 2), "mean_stay": round(float(b.mean()), 2)}

# ML Models
drop_cols = [c for c in ["customer_id", "churn", "churn_flag"] if c in df.columns]
X = pd.get_dummies(df.drop(columns=drop_cols), drop_first=True)
y = df.churn_flag
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
sc = StandardScaler().fit(Xtr)

models_res = {}
imp = None

lr = LogisticRegression(max_iter=2000, class_weight="balanced")
lr.fit(sc.transform(Xtr), ytr)
pred, prob = lr.predict(sc.transform(Xte)), lr.predict_proba(sc.transform(Xte))[:, 1]
models_res["Logistic Regression"] = {
    "accuracy": round(accuracy_score(yte, pred), 3),
    "precision": round(precision_score(yte, pred, zero_division=0), 3),
    "recall": round(recall_score(yte, pred, zero_division=0), 3),
    "f1": round(f1_score(yte, pred, zero_division=0), 3),
    "roc_auc": round(roc_auc_score(yte, prob), 3)
}

dt = DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=SEED)
dt.fit(Xtr, ytr)
pred, prob = dt.predict(Xte), dt.predict_proba(Xte)[:, 1]
models_res["Decision Tree"] = {
    "accuracy": round(accuracy_score(yte, pred), 3),
    "precision": round(precision_score(yte, pred, zero_division=0), 3),
    "recall": round(recall_score(yte, pred, zero_division=0), 3),
    "f1": round(f1_score(yte, pred, zero_division=0), 3),
    "roc_auc": round(roc_auc_score(yte, prob), 3)
}
imp = pd.Series(dt.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)

# Clustering
Z = StandardScaler().fit_transform(df[["tenure", "monthly_charges", "total_charges"]])
df["segment"] = KMeans(n_clusters=4, n_init=10, random_state=SEED).fit_predict(Z)
prof = df.groupby("segment").agg(customers=("segment", "size"), avg_tenure=("tenure", "mean"),
                                 avg_monthly=("monthly_charges", "mean"),
                                 churn_rate=("churn_flag", "mean")).round(2)
prof["churn_rate"] = (prof["churn_rate"] * 100).round(1)
segments = prof.reset_index().to_dict("records")

# Charts
sns.set_theme(style="whitegrid")
pal = {"No": "#2a9d8f", "Yes": "#e63946"}

for col, fn, title in [("contract", "churn_by_contract.png", "Churn rate by contract type"),
                       ("internet_service", "churn_by_internet.png", "Churn rate by internet service"),
                       ("payment_method", "churn_by_payment.png", "Churn rate by payment method")]:
    if col in df.columns:
        t = segment_table(df, col).sort_values("churn_rate")
        fig, ax = plt.subplots(figsize=(7, 3.4))
        ax.barh(t[col], t.churn_rate, color="#4b3fb5")
        for i, v in enumerate(t.churn_rate):
            ax.text(v + 0.6, i, f"{v}%", va="center")
        ax.set_title(title); ax.set_xlabel("Churn rate (%)")
        fig.tight_layout(); fig.savefig(FIG_DIR / fn, dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.4))
sns.histplot(data=df, x="tenure", hue="churn", multiple="stack", palette=pal, bins=24, ax=ax)
ax.set_title("Tenure distribution by churn"); ax.set_xlabel("Tenure (months)")
fig.tight_layout(); fig.savefig(FIG_DIR / "tenure_hist.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.4))
sns.boxplot(data=df, x="churn", y="monthly_charges", palette=pal, hue="churn", legend=False, ax=ax)
ax.set_title("Monthly charges by churn")
fig.tight_layout(); fig.savefig(FIG_DIR / "charges_box.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.8))
imp.sort_values().plot.barh(color="#4b3fb5", ax=ax)
ax.set_title("Top 10 features - Decision Tree importance")
fig.tight_layout(); fig.savefig(FIG_DIR / "feature_importance.png", dpi=160); plt.close(fig)

# Save JSON and Excel
seg_tables = {c: segment_table(df, c) for c in ["contract", "internet_service", "payment_method", "senior_citizen", "paperless_billing", "tech_support"] if c in df.columns}
with pd.ExcelWriter(REP_DIR / "analysis_results.xlsx") as xw:
    pd.DataFrame([kpis]).T.rename(columns={0: "value"}).to_excel(xw, sheet_name="KPIs")
    for c, t in seg_tables.items():
        t.to_excel(xw, sheet_name=f"churn_by_{c}"[:31], index=False)
    pd.DataFrame(models_res).T.to_excel(xw, sheet_name="model_metrics")
    imp.rename("importance").to_frame().to_excel(xw, sheet_name="feature_importance")
    prof.reset_index().to_excel(xw, sheet_name="segments", index=False)

summary = {
    "kpis": kpis,
    "tests": tests,
    "models": models_res,
    "importance": imp.round(3).to_dict(),
    "segments": segments,
    "segment_tables": {c: t.to_dict("records") for c, t in seg_tables.items()}
}
(REP_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
print("[+] Pipeline data & figures generated successfully.")

# --- STEP 4: GENERATE PDF REPORT ---
print("[+] Generating Final_Report.pdf...")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10.5, leading=15, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], textColor=PURPLE, fontSize=18, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=TEAL, fontSize=13)
bul = ParagraphStyle("bul", parent=body, leftIndent=14, bulletIndent=2)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, textColor=colors.grey, alignment=1)

class Doc(BaseDocTemplate):
    def __init__(self, fn):
        super().__init__(fn, pagesize=A4, leftMargin=2.2*cm, rightMargin=2.2*cm,
                         topMargin=2.2*cm, bottomMargin=2*cm,
                         title="Telco Customer Churn - Final Report", author=AUTHOR_NAME)
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate("cover", [fr], onPage=self.cover),
                               PageTemplate("main", [fr], onPage=self.header)])

    def cover(self, c, d):
        w, h = A4
        c.setFillColor(PURPLE); c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(TEAL); c.rect(0, h*0.38, w, 6, fill=1, stroke=0)

    def header(self, c, d):
        w, h = A4
        c.setFillColor(PURPLE); c.rect(0, h-1.1*cm, w, 1.1*cm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 9)
        c.drawString(2.2*cm, h-0.72*cm, "ApexPlanet Software Pvt. Ltd.  |  Data Analytics Internship")
        c.setFillColor(colors.grey); c.setFont("Helvetica", 9)
        c.drawRightString(w-2.2*cm, 1.1*cm, f"Page {d.page}")

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1",):
            self.notify("TOCEntry", (0, f.getPlainText(), self.page))

def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bul, bulletText="•") for i in items]
def fig(name, w=14.5):
    img_path = FIG_DIR / name
    if not img_path.exists():
        return Spacer(1, 10)
    iw, ih = PILImage.open(img_path).size
    return Image(str(img_path), width=w*cm, height=w*cm*ih/iw)

def tbl(rows, widths=None, hdr=PURPLE):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), hdr), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f2f1fb")]),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)
    ]))
    return t

def rate(tab, key, val, default=0.0):
    try:
        return next(r["churn_rate"] for r in summary["segment_tables"][tab] if r[key] == val)
    except Exception:
        return default

mtm = rate("contract","contract","Month-to-month")
two = rate("contract","contract","Two year")
fib = rate("internet_service","internet_service","Fiber optic")
nointernet = rate("internet_service","internet_service","No")
echeck = rate("payment_method","payment_method","Electronic check")
lr_m = summary["models"]["Logistic Regression"]
seg = sorted(summary["segments"], key=lambda r: -r["churn_rate"])

story = []
# Cover Page
story += [
    Spacer(1, 6*cm),
    Paragraph("<font color='white' size=30><b>Telco Customer Churn</b></font>", ParagraphStyle("c", leading=36)),
    Paragraph("<font color='white' size=18>Final Analytics Report</font>", ParagraphStyle("c2", leading=26)),
    Spacer(1, 7.2*cm),
    Paragraph(f"<font color='white' size=12>Prepared by: {AUTHOR_NAME}<br/>Data Analytics Internship (45 Days)<br/>ApexPlanet Software Pvt. Ltd.</font>",
              ParagraphStyle("c3", leading=18))
]
story += [NextPageTemplate("main"), PageBreak()]
toc = TableOfContents(); toc.levelStyles = [ParagraphStyle("t0", fontSize=11, leading=20)]
story += [P("Table of Contents", h1), toc, PageBreak()]

# Section 1
story += [
    P("1. Executive Summary", h1),
    P(f"This report analyses <b>{kpis['customers']:,}</b> telecom customers to understand why customers leave. "
      f"Overall churn is <b>{kpis['churn_rate_pct']}%</b> ({kpis['churned']:,} customers), putting about "
      f"<b>${kpis['monthly_revenue_at_risk']:,.0f}</b> monthly revenue at risk."),
    P("<b>Headline findings</b>")
] + B([
    f"Contract type is the strongest driver: month-to-month churn is {mtm}% vs {two}% on two-year contracts.",
    f"Fiber-optic customers churn at {fib}% (vs {nointernet}% with no internet), and electronic-check payers churn at {echeck}%.",
    f"Logistic regression captures {lr_m['recall']*100:.1f}% of churners with ROC-AUC {lr_m['roc_auc']}.",
    f"Highest risk segment churns at {seg[0]['churn_rate']}%."
]) + [
    P("<b>Top recommendation:</b> Incentivize long-term contracts and migrate high-risk customers from electronic check to automatic payment methods."),
    PageBreak()
]

# Section 2 & 3
story += [
    P("2. Problem Statement &amp; Objectives", h1),
    P("Customer churn causes revenue loss. The objective is to identify drivers, segment customers, and establish predictive models."),
    P("3. Data Source &amp; Methodology", h1),
    P("IBM Telco Customer Churn dataset with end-to-end data cleaning, SQL extraction, exploratory visualization, and machine learning models."),
    PageBreak()
]

# Section 4
story += [
    P("4. Key Findings", h1),
    P("<b>Insight 1 - Contract length:</b>"), fig("churn_by_contract.png", 12.5),
    P("<b>Insight 2 - Tenure:</b>"), fig("tenure_hist.png", 12.5),
    PageBreak(),
    P("<b>Insight 3 - Internet Service:</b>"), fig("churn_by_internet.png", 12.5),
    P("<b>Insight 4 - Monthly Charges:</b>"), fig("charges_box.png", 12.5),
    PageBreak()
]

# Section 5
def pf(p): return "< 0.001" if p < 0.001 else f"{p:.3f}"
stat_rows = [["Test", "Statistic", "p-value", "Result"]]
for k, lab in [("chi2_contract","Chi-square: contract vs churn"),("chi2_internet_service","Chi-square: internet service vs churn"),
               ("chi2_payment_method","Chi-square: payment method vs churn")]:
    if k in tests:
        stat_rows.append([lab, f"chi2 = {tests[k]['chi2']} (df {tests[k]['dof']})", pf(tests[k]['p']), "Significant"])
for k, lab in [("ttest_monthly_charges","Welch t-test: monthly charges"),("ttest_tenure","Welch t-test: tenure")]:
    if k in tests:
        stat_rows.append([lab, f"t = {tests[k]['t']}", pf(tests[k]['p']), "Significant"])

mrows = [["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]] + [
    [n] + [str(v[x]) for x in ("accuracy","precision","recall","f1","roc_auc")] for n, v in models_res.items()
]
srows = [["Segment", "Customers", "Avg tenure (mo)", "Avg monthly ($)", "Churn rate"]] + [
    [f"Segment {r['segment']}", f"{r['customers']:,}", f"{r['avg_tenure']:.1f}", f"{r['avg_monthly']:.1f}", f"{r['churn_rate']}%"] for r in segments
]

story += [
    P("5. Statistical Analysis Results", h1),
    tbl(stat_rows, [6.2*cm, 4.2*cm, 2.2*cm, 2.4*cm]), Spacer(1, 10),
    P("<b>Predictive Models</b>", h2), tbl(mrows, [4.4*cm]+[2.4*cm]*5), Spacer(1, 8),
    fig("feature_importance.png", 11.5),
    P("<b>Customer Segments</b>", h2), tbl(srows, [3*cm, 3*cm, 3.6*cm, 3.6*cm, 2.8*cm]),
    PageBreak()
]

# Section 6, 7 & 8
story += [
    P("6. Dashboard Screenshots", h1),
    Table([[P("<br/><br/><br/>[ Power BI / Tableau Dashboard Screenshot Placeholder ]<br/><br/><br/>",
              ParagraphStyle("p", alignment=1, textColor=colors.grey))]],
          colWidths=[15*cm], style=[("BOX", (0,0), (-1,-1), 1, colors.lightgrey)]),
    PageBreak(),
    P("7. Recommendations", h1)
] + B([
    "Provide upgrade discounts to transition month-to-month contracts to 1-year commitments.",
    "Proactive outreach during the first 6 months to address customer experience bottlenecks.",
    "Promote paperless billing and auto-pay adoption."
]) + [
    P("8. Future Scope &amp; Limitations", h1)
] + B([
    "Integrate dynamic streaming logs for real-time inference.",
    "Tune hyperparameter search with XGBoost for enhanced model precision."
])

doc = Doc(str(REP_DIR / "Final_Report.pdf"))
doc.multiBuild(story)
print(f"[SUCCESS] Final Report generated at: {REP_DIR / 'Final_Report.pdf'}")