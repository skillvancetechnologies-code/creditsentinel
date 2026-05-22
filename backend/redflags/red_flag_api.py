from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# ==============================
# LOAD DATASETS
# ==============================

loan_apps = pd.read_csv(
    r"C:\Users\gurup\OneDrive\Desktop\creditsentinel\data\raw\loan_applications.csv"
)

bureau = pd.read_csv(
    r"C:\Users\gurup\OneDrive\Desktop\creditsentinel\data\raw\bureau_data.csv"
)

bank = pd.read_csv(
    r"C:\Users\gurup\OneDrive\Desktop\creditsentinel\data\raw\bank_statements.csv"
)

gst = pd.read_csv(
    r"C:\Users\gurup\OneDrive\Desktop\creditsentinel\data\raw\gst_filings.csv"
)

# ==============================
# CREATE FEATURES
# ==============================

# Bank features
bank_features = bank.groupby(
    "application_id"
).agg({
    "emi_bounces": "sum"
}).reset_index()

bank_features.rename(columns={
    "emi_bounces": "total_emi_bounces"
}, inplace=True)

# Dummy avg credits
bank_features["avg_credits"] = 50000

# GST missing quarters
gst_features = gst.groupby(
    "application_id"
).size().reset_index(
    name="gst_missing_quarters"
)

# Merge all datasets
features = loan_apps.merge(
    bureau,
    on="application_id",
    how="left"
)

features = features.merge(
    bank_features,
    on="application_id",
    how="left"
)

features = features.merge(
    gst_features,
    on="application_id",
    how="left"
)

# Fill missing values
features["total_emi_bounces"] = (
    features["total_emi_bounces"].fillna(0)
)

features["gst_missing_quarters"] = (
    features["gst_missing_quarters"].fillna(0)
)

features["avg_credits"] = (
    features["avg_credits"].fillna(50000)
)

# Derived features
features["income_bank_mismatch"] = abs(
    features["monthly_income"] -
    features["avg_credits"]
) / features["monthly_income"] * 100

features["is_self_employed"] = (
    features["employment_type"] == "Self-Employed"
).astype(int)

# ==============================
# RED FLAG ENGINE
# ==============================

def detect_red_flags(app):

    flags = []

    # Rule 1
    if app['foir'] > 60:
        flags.append({
            "rule": "High FOIR",
            "evidence": (
                f"FOIR is {app['foir']}%"
            ),
            "severity": "High"
        })

    # Rule 2
    if app['cibil_score'] < 650:
        flags.append({
            "rule": "Low CIBIL",
            "evidence": (
                f"CIBIL score is "
                f"{app['cibil_score']}"
            ),
            "severity": "High"
        })

    # Rule 3
    if app['num_credit_inquiries_30d'] >= 3:
        flags.append({
            "rule": "High Inquiries",
            "evidence": (
                f"{app['num_credit_inquiries_30d']} "
                f"inquiries in 30 days"
            ),
            "severity": "Medium"
        })

    # Rule 4
    lti = (
        app['requested_loan_amount'] /
        (app['monthly_income'] * 12)
    )

    if lti > 5:
        flags.append({
            "rule": "Loan Exceeds 5x Income",
            "evidence": (
                f"Loan is {lti:.1f}x "
                f"annual income"
            ),
            "severity": "High"
        })

    # Rule 5
    if app['has_previous_default'] == 1:
        flags.append({
            "rule": "Previous Default",
            "evidence": (
                "Previous default "
                "found"
            ),
            "severity": "High"
        })

    # Rule 6
    if app['is_night_application'] == 1:
        flags.append({
            "rule": "Night Application",
            "evidence": (
                "Submitted between "
                "11PM and 5AM"
            ),
            "severity": "Medium"
        })

    # Rule 7
    if app['total_emi_bounces'] > 0:
        flags.append({
            "rule": "EMI Bounces",
            "evidence": (
                f"{app['total_emi_bounces']} "
                f"bounces"
            ),
            "severity": "High"
        })

    # Rule 8
    if app['income_bank_mismatch'] > 25:
        flags.append({
            "rule": "Income Mismatch",
            "evidence": (
                f"{round(app['income_bank_mismatch'],1)}% "
                f"mismatch"
            ),
            "severity": "High"
        })

    # Rule 9
    if (
        app['is_self_employed'] == 1
        and app['gst_missing_quarters'] >= 2
    ):
        flags.append({
            "rule": "GST Filing Gaps",
            "evidence": (
                f"{int(app['gst_missing_quarters'])} "
                f"missing quarters"
            ),
            "severity": "High"
        })

    # Rule 10
    if (
        app['employment_years'] < 1
        and app['foir'] > 50
    ):
        flags.append({
            "rule": "Short Emp + High FOIR",
            "evidence": (
                f"{app['employment_years']} years "
                f"employment"
            ),
            "severity": "High"
        })

    return flags

# ==============================
# API ENDPOINT
# ==============================

@app.post("/api/redflags")
def get_red_flags(payload: dict):

    application_id = payload["application_id"]

    app_data = features[
        features["application_id"] ==
        application_id
    ]

    if len(app_data) == 0:

        return {
            "error": "Application not found"
        }

    app_row = app_data.iloc[0]

    flags = detect_red_flags(app_row)

    highest_severity = "Low"

    if any(
        f["severity"] == "High"
        for f in flags
    ):
        highest_severity = "High"

    elif any(
        f["severity"] == "Medium"
        for f in flags
    ):
        highest_severity = "Medium"

    return {
        "application_id": application_id,
        "flag_count": len(flags),
        "highest_severity": highest_severity,
        "flags": flags
    }
# ==============================
# BATCH REQUEST MODEL
# ==============================

class BatchRequest(BaseModel):

    application_ids: list[str]

# ==============================
# COMPUTE RED FLAGS
# ==============================

def compute_red_flags(application_id):

    app_data = features[
        features["application_id"] ==
        application_id
    ]

    if len(app_data) == 0:

        return {
            "application_id": application_id,
            "error": "Application not found"
        }

    app_row = app_data.iloc[0]

    flags = detect_red_flags(app_row)

    highest_severity = "Low"

    if any(
        f["severity"] == "High"
        for f in flags
    ):

        highest_severity = "High"

    elif any(
        f["severity"] == "Medium"
        for f in flags
    ):

        highest_severity = "Medium"

    return {
        "application_id": application_id,
        "flag_count": len(flags),
        "highest_severity": highest_severity,
        "flags": flags
    }

# ==============================
# BATCH ENDPOINT
# ==============================

@app.post("/api/redflags-batch")
def batch_redflags(req: BatchRequest):

    results = []

    for app_id in req.application_ids:

        result = compute_red_flags(app_id)

        results.append(result)

    return {
        "results": results
    }