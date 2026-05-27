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

    if "recent_inquiries" in row:

        if float(row["recent_inquiries"]) >= 3:

            severity = "Medium"

            flags.append({

                "rule": "High Inquiries",

                "evidence":
                f"{row['recent_inquiries']} inquiries in 30 days",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 4 — EMI BOUNCES
    # ==============================

    if "emi_bounces" in row:

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
    # RULE 5 — INCOME MISMATCH
    # ==============================

    if "income_mismatch_percent" in row:

        if float(row["income_mismatch_percent"]) > 25:

            severity = "High"

            flags.append({

                "rule": "Income Mismatch",

                "evidence":
                f"{row['income_mismatch_percent']}% mismatch",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 6 — GST GAPS
    # ==============================

    if "missing_gst_quarters" in row:

        if float(row["missing_gst_quarters"]) >= 4:

            severity = "High"

            flags.append({

                "rule": "GST Filing Gaps",

                "evidence":
                f"{row['missing_gst_quarters']} missing quarters",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 7 — LOW BANK BALANCE
    # ==============================

    if "avg_bank_balance" in row:

        if float(row["avg_bank_balance"]) < 10000:

            severity = "Medium"

            flags.append({

                "rule": "Low Bank Balance",

                "evidence":
                f"Average balance is {row['avg_bank_balance']}",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 8 — CREDIT UTILIZATION
    # ==============================

    if "credit_utilization" in row:

        if float(row["credit_utilization"]) > 80:

            severity = "Medium"

            flags.append({

                "rule": "High Credit Utilization",

                "evidence":
                f"{row['credit_utilization']}% utilized",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 9 — LOAN DEFAULTS
    # ==============================

    if "loan_defaults" in row:

        if float(row["loan_defaults"]) >= 1:

            severity = "High"

            flags.append({

                "rule": "Loan Defaults",

                "evidence":
                f"{row['loan_defaults']} defaults found",

                "severity": severity,

                "color": get_color(severity)
            })

    # ==============================
    # RULE 10 — NIGHT TRANSACTIONS
    # ==============================

    if "night_transactions_percent" in row:

        if float(row["night_transactions_percent"]) > 40:

            severity = "Medium"

            flags.append({

                "rule": "High Night Transactions",

                "evidence":
                f"{row['night_transactions_percent']}% night activity",

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
@app.get("/debug-columns")
def debug_columns():

    return {
        "columns": list(features.columns)
    }
