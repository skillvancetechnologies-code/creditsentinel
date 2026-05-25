from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware
)
from pydantic import BaseModel
import pandas as pd
import os

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI()

# ==============================
# CORS
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ==============================
# MERGE DATASETS
# ==============================

features = loan_apps.merge(
    bureau,
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

def severity_color(severity):

    if severity == "High":

        return "red"

    elif severity == "Medium":

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
            "error": "Application not found"
        }

    app_row = app_data.iloc[0]

    flags = []

    # ==============================
    # RULE 1 — LOW CIBIL
    # ==============================

    if app_row["cibil_score"] < 600:

        flags.append({

            "rule": "Low CIBIL",

            "evidence":
            f"CIBIL score is "
            f"{app_row['cibil_score']}",

            "severity": "High",

            "color": severity_color(
                "High"
            )
        })

    # ==============================
    # RULE 2 — HIGH FOIR
    # ==============================

    if app_row["foir"] > 60:

        flags.append({

            "rule": "High FOIR",

            "evidence":
            f"FOIR is "
            f"{app_row['foir']}%",

            "severity": "High",

            "color": severity_color(
                "High"
            )
        })

    # ==============================
    # RULE 3 — EMI BOUNCES
    # ==============================

    if (
        "emi_bounces"
        in app_row.index
    ):

        if app_row["emi_bounces"] > 0:

            flags.append({

                "rule": "EMI Bounces",

                "evidence":
                f"{app_row['emi_bounces']} bounces",

                "severity": "High",

                "color": severity_color(
                    "High"
                )
            })

    # ==============================
    # RULE 4 — HIGH INQUIRIES
    # ==============================

    if (
        "recent_inquiries"
        in app_row.index
    ):

        if app_row["recent_inquiries"] >= 3:

            flags.append({

                "rule": "High Inquiries",

                "evidence":
                f"{app_row['recent_inquiries']} "
                f"inquiries in 30 days",

                "severity": "Medium",

                "color": severity_color(
                    "Medium"
                )
            })

    # ==============================
    # RULE 5 — INCOME MISMATCH
    # ==============================

    if (
        "income_mismatch_percent"
        in app_row.index
    ):

        if (
            app_row[
                "income_mismatch_percent"
            ] > 25
        ):

            flags.append({

                "rule": "Income Mismatch",

                "evidence":
                f"{app_row['income_mismatch_percent']}% mismatch",

                "severity": "High",

                "color": severity_color(
                    "High"
                )
            })

    # ==============================
    # RULE 6 — GST GAPS
    # ==============================

    if (
        "gst_gap_quarters"
        in app_row.index
    ):

        if app_row["gst_gap_quarters"] > 0:

            flags.append({

                "rule": "GST Gaps",

                "evidence":
                f"{app_row['gst_gap_quarters']} quarters missing",

                "severity": "Medium",

                "color": severity_color(
                    "Medium"
                )
            })

    # ==============================
    # RULE 7 — DEFAULT HISTORY
    # ==============================

    if (
        "has_default_history"
        in app_row.index
    ):

        if (
            app_row[
                "has_default_history"
            ] == 1
        ):

            flags.append({

                "rule": "Default History",

                "evidence":
                "Previous default found",

                "severity": "High",

                "color": severity_color(
                    "High"
                )
            })

    # ==============================
    # RULE 8 — NIGHT TRANSACTIONS
    # ==============================

    if (
        "night_transactions"
        in app_row.index
    ):

        if (
            app_row[
                "night_transactions"
            ] > 10
        ):

            flags.append({

                "rule": "Night Transactions",

                "evidence":
                f"{app_row['night_transactions']} "
                f"night transactions",

                "severity": "Medium",

                "color": severity_color(
                    "Medium"
                )
            })

    # ==============================
    # RULE 9 — SHORT EMPLOYMENT
    # ==============================

    if (
        app_row["employment_years"]
        < 1
    ):

        flags.append({

            "rule": "Short Employment",

            "evidence":
            f"{app_row['employment_years']} years",

            "severity": "Low",

            "color": severity_color(
                "Low"
            )
        })

    # ==============================
    # RULE 10 — LOW INCOME
    # ==============================

    if (
        app_row["monthly_income"]
        < 25000
    ):

        flags.append({

            "rule": "Low Income",

            "evidence":
            f"Income is "
            f"{app_row['monthly_income']}",

            "severity": "Medium",

            "color": severity_color(
                "Medium"
            )
        })

    # ==============================
    # HIGHEST SEVERITY
    # ==============================

    highest_severity = "Low"

    for flag in flags:

        if flag["severity"] == "High":

            highest_severity = "High"

            break

        elif (
            flag["severity"]
            == "Medium"
        ):

            highest_severity = "Medium"

    # ==============================
    # FINAL RESPONSE
    # ==============================

    return {

        "application_id":
        str(application_id),

        "flag_count":
        len(flags),

        "highest_severity":
        highest_severity,

        "flags":
        flags
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

        flags = compute_red_flags(
            app_id
        )

        results.append(flags)

    return {
        "results": results
    }