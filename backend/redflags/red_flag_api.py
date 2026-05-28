from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI()

# ==============================
# CORS CONFIGURATION
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# LOAD DATASETS
# ==============================

loan_apps = pd.read_csv(
    "loan_applications.csv"
)

bureau = pd.read_csv(
    "bureau_data.csv"
)

banking = pd.read_csv(
    "bank_statements.csv"
)

gst = pd.read_csv(
    "gst_filings.csv"
)

# ==============================
# MERGE DATA
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

severity_colors = {

    "High": "red",

    "Medium": "orange",

    "Low": "yellow"
}

# ==============================
# RED FLAG ENGINE
# ==============================

def compute_red_flags(application_id):

    app_data = features[
        features["application_id"] ==
        application_id
    ]

    if len(app_data) == 0:

        return {
            "error": "Application not found"
        }

    app = app_data.iloc[0]

    flags = []

    # ==============================
    # RULE 1 — LOW CIBIL
    # ==============================

    if app["cibil_score"] < 600:

        flags.append({

            "rule": "Low CIBIL",

            "evidence":
            f"CIBIL score is "
            f"{app['cibil_score']}",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 2 — HIGH FOIR
    # ==============================

    if app["foir"] > 60:

        flags.append({

            "rule": "High FOIR",

            "evidence":
            f"FOIR is "
            f"{app['foir']}%",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 3 — HIGH INQUIRIES
    # ==============================

    if app["recent_inquiries"] >= 3:

        flags.append({

            "rule": "High Inquiries",

            "evidence":
            f"{app['recent_inquiries']} "
            f"inquiries in 30 days",

            "severity": "Medium",

            "color": severity_colors["Medium"]
        })

    # ==============================
    # RULE 4 — EMI BOUNCES
    # ==============================

    if app["emi_bounces"] >= 1:

        flags.append({

            "rule": "EMI Bounces",

            "evidence":
            f"{app['emi_bounces']} "
            f"bounces",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 5 — GST GAPS
    # ==============================

    if app["missing_gst_quarters"] >= 4:

        flags.append({

            "rule": "GST Filing Gaps",

            "evidence":
            f"{app['missing_gst_quarters']} "
            f"missing quarters",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 6 — INCOME MISMATCH
    # ==============================

    if app["income_mismatch_pct"] > 25:

        flags.append({

            "rule": "Income Mismatch",

            "evidence":
            f"{app['income_mismatch_pct']}% "
            f"mismatch",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 7 — NIGHT TRANSACTIONS
    # ==============================

    if app["night_txn_flag"] == 1:

        flags.append({

            "rule": "Night Transactions",

            "evidence":
            "Suspicious night transactions",

            "severity": "Medium",

            "color": severity_colors["Medium"]
        })

    # ==============================
    # RULE 8 — DEFAULT HISTORY
    # ==============================

    if app["past_defaults"] >= 1:

        flags.append({

            "rule": "Past Defaults",

            "evidence":
            f"{app['past_defaults']} "
            f"past defaults",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 9 — LOW BANK BALANCE
    # ==============================

    if app["avg_bank_balance"] < 10000:

        flags.append({

            "rule": "Low Bank Balance",

            "evidence":
            f"Average balance "
            f"{app['avg_bank_balance']}",

            "severity": "Low",

            "color": severity_colors["Low"]
        })

    # ==============================
    # RULE 10 — SHORT EMPLOYMENT
    # ==============================

    if app["employment_years"] < 2:

        flags.append({

            "rule": "Short Employment History",

            "evidence":
            f"{app['employment_years']} "
            f"years employment",

            "severity": "Low",

            "color": severity_colors["Low"]
        })

    # ==============================
    # HIGHEST SEVERITY
    # ==============================

    highest = "Low"

    if any(
        f["severity"] == "High"
        for f in flags
    ):

        highest = "High"

    elif any(
        f["severity"] == "Medium"
        for f in flags
    ):

        highest = "Medium"

    # ==============================
    # FINAL RESPONSE
    # ==============================

    return {

        "application_id": application_id,

        "flag_count": len(flags),

        "highest_severity": highest,

        "flags": flags
    }

# ==============================
# SINGLE ENDPOINT
# ==============================

@app.post("/api/redflags")
def get_redflags(
    req: RedFlagRequest
):

    return compute_red_flags(
        req.application_id
    )

# ==============================
# BATCH ENDPOINT
# ==============================

@app.post("/api/redflags-batch")
def batch_redflags(
    req: BatchRequest
):

    results = []

    for app_id in req.application_ids:

        flags = compute_red_flags(
            app_id
        )

        results.append(flags)

    return {
        "results": results
    }
