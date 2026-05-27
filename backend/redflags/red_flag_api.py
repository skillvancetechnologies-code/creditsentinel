from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI()

# ==============================
# BASE DIRECTORY
# ==============================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ==============================
# LOAD DATASETS
# ==============================

loan_apps = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "loan_applications.csv"
    )
)

bureau = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "bureau_data.csv"
    )
)

banking = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "bank_statements.csv"
    )
)

gst = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "gst_filings.csv"
    )
)

# ==============================
# MERGE DATASETS
# ==============================

features = loan_apps.merge(
    bureau,
    on="application_id",
    how="left"
)

features = features.merge(
    banking,
    on="application_id",
    how="left"
)

features = features.merge(
    gst,
    on="application_id",
    how="left"
)

# ==============================
# REQUEST MODELS
# ==============================

class RedFlagRequest(BaseModel):

    application_id: str


class BatchRequest(BaseModel):

    application_ids: list[str]

# ==============================
# COLOR MAPPING
# ==============================

def get_color(severity):

    severity = severity.lower()

    if severity == "high":

        return "red"

    elif severity == "medium":

        return "orange"

    else:

        return "yellow"

# ==============================
# RED FLAG ENGINE
# ==============================

def compute_red_flags(application_id):

    app_data = features[
        features["application_id"].astype(str)
        == str(application_id)
    ]

    if app_data.empty:

        return {

            "application_id": application_id,

            "flag_count": 0,

            "highest_severity": "Low",

            "flags": []
        }

    row = app_data.iloc[0]

    flags = []

    # ==============================
    # RULE 1 — LOW CIBIL
    # ==============================

    if float(row["cibil_score"]) < 600:

        severity = "High"

        flags.append({

            "rule": "Low CIBIL Score",

            "evidence":
            f"CIBIL score is {row['cibil_score']}",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 2 — HIGH FOIR
    # ==============================

    if float(row["foir"]) > 60:

        severity = "High"

        flags.append({

            "rule": "High FOIR",

            "evidence":
            f"FOIR is {row['foir']}%",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 3 — HIGH INQUIRIES
    # ==============================

    if float(row["num_credit_inquiries_30d"]) >= 3:

        severity = "Medium"

        flags.append({

            "rule": "High Inquiries",

            "evidence":
            f"{row['num_credit_inquiries_30d']} inquiries in 30 days",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 4 — EMI BOUNCES
    # ==============================

    if float(row["emi_bounces"]) >= 1:

        severity = "High"

        flags.append({

            "rule": "EMI Bounces",

            "evidence":
            f"{row['emi_bounces']} bounces",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 5 — LOW BANK BALANCE
    # ==============================

    if float(row["min_eod_balance"]) < 10000:

        severity = "Medium"

        flags.append({

            "rule": "Low Bank Balance",

            "evidence":
            f"Minimum balance is {row['min_eod_balance']}",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 6 — HIGH CREDIT UTILIZATION
    # ==============================

    if float(row["credit_utilization_pct"]) > 80:

        severity = "Medium"

        flags.append({

            "rule": "High Credit Utilization",

            "evidence":
            f"{row['credit_utilization_pct']}% utilized",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 7 — PREVIOUS DEFAULT
    # ==============================

    if int(row["has_previous_default"]) == 1:

        severity = "High"

        flags.append({

            "rule": "Previous Loan Default",

            "evidence":
            "Applicant has previous default history",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 8 — NIGHT APPLICATION
    # ==============================

    if int(row["is_night_application"]) == 1:

        severity = "Medium"

        flags.append({

            "rule": "Night Application",

            "evidence":
            "Application submitted during night hours",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 9 — CHEQUE BOUNCES
    # ==============================

    if float(row["cheque_bounces"]) >= 1:

        severity = "Medium"

        flags.append({

            "rule": "Cheque Bounces",

            "evidence":
            f"{row['cheque_bounces']} cheque bounces found",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # RULE 10 — LOW CREDIT AGE
    # ==============================

    if float(row["credit_age_months"]) < 12:

        severity = "Medium"

        flags.append({

            "rule": "Low Credit Age",

            "evidence":
            f"Credit age is {row['credit_age_months']} months",

            "severity": severity,

            "color": get_color(severity)
        })

    # ==============================
    # HIGHEST SEVERITY
    # ==============================

    highest_severity = "Low"

    for flag in flags:

        if flag["severity"] == "High":

            highest_severity = "High"
            break

        elif flag["severity"] == "Medium":

            highest_severity = "Medium"

    # ==============================
    # FINAL RESPONSE
    # ==============================

    return {

        "application_id": str(application_id),

        "flag_count": len(flags),

        "highest_severity": highest_severity,

        "flags": flags
    }

# ==============================
# SINGLE ENDPOINT
# ==============================

@app.post("/api/redflags")
def redflags(req: RedFlagRequest):

    return compute_red_flags(
        req.application_id
    )

# ==============================
# BATCH ENDPOINT
# ==============================

@app.post("/api/redflags-batch")
def batch_redflags(req: BatchRequest):

    results = []

    for app_id in req.application_ids:

        results.append(
            compute_red_flags(app_id)
        )

    return {
        "results": results
    }

# ==============================
# ROOT ENDPOINT
# ==============================

@app.get("/")
def root():

    return {
        "message":
        "Red Flags API Running Successfully"
    }

# ==============================
# DEBUG ENDPOINT
# ==============================

@app.get("/debug-columns")
def debug_columns():

    return {
        "columns": list(features.columns)
    }
