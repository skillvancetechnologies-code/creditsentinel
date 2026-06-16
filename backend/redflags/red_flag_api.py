from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import time
from datetime import datetime

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
# DEBUG COLUMN NAMES
# ==============================

print("\nALL AVAILABLE COLUMNS:\n")

print(list(features.columns))

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
# SAFE COLUMN GETTER
# ==============================

def safe_get(app, possible_columns, default=0):

    for col in possible_columns:

        if col in app.index:

            return app[col]

    return default
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
    # SAFE COLUMN MAPPING
    # ==============================

    cibil_score = safe_get(
        app,
        ["cibil_score"]
    )

    foir = safe_get(
        app,
        ["foir"]
    )

    recent_inquiries = safe_get(
        app,
        [
            "num_credit_inquiries_30d"
        ]
    )

    emi_bounces = safe_get(
        app,
        [
            "emi_bounces"
        ]
    )

    # GST gaps approximation
    missing_gst_quarters = 0

    # Income mismatch not available
    income_mismatch_pct = 0

    night_txn_flag = safe_get(
        app,
        [
            "is_night_application"
        ]
    )

    past_defaults = safe_get(
        app,
        [
            "has_previous_default"
        ]
    )

    avg_bank_balance = safe_get(
        app,
        [
            "min_eod_balance"
        ]
    )

    employment_years = safe_get(
        app,
        [
            "employment_years",
            "work_experience_years"
        ]
    )

    # ==============================
    # RULE 1 — LOW CIBIL
    # ==============================

    if cibil_score < 600:

        flags.append({

            "rule": "Low CIBIL",

            "evidence":
            f"CIBIL score is "
            f"{cibil_score}",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 2 — HIGH FOIR
    # ==============================

    if foir > 60:

        flags.append({

            "rule": "High FOIR",

            "evidence":
            f"FOIR is "
            f"{foir}%",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 3 — HIGH INQUIRIES
    # ==============================

    if recent_inquiries >= 3:

        flags.append({

            "rule": "High Inquiries",

            "evidence":
            f"{recent_inquiries} "
            f"inquiries in 30 days",

            "severity": "Medium",

            "color": severity_colors["Medium"]
        })

    # ==============================
    # RULE 4 — EMI BOUNCES
    # ==============================

    if emi_bounces >= 1:

        flags.append({

            "rule": "EMI Bounces",

            "evidence":
            f"{emi_bounces} "
            f"bounces",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 5 — GST GAPS
    # ==============================

    if missing_gst_quarters >= 4:

        flags.append({

            "rule": "GST Filing Gaps",

            "evidence":
            f"{missing_gst_quarters} "
            f"missing quarters",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 6 — INCOME MISMATCH
    # ==============================

    if income_mismatch_pct > 25:

        flags.append({

            "rule": "Income Mismatch",

            "evidence":
            f"{income_mismatch_pct}% "
            f"mismatch",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 7 — NIGHT TRANSACTIONS
    # ==============================

    if night_txn_flag == 1:

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

    if past_defaults >= 1:

        flags.append({

            "rule": "Past Defaults",

            "evidence":
            f"{past_defaults} "
            f"past defaults",

            "severity": "High",

            "color": severity_colors["High"]
        })

    # ==============================
    # RULE 9 — LOW BANK BALANCE
    # ==============================

    if avg_bank_balance < 10000:

        flags.append({

            "rule": "Low Bank Balance",

            "evidence":
            f"Average balance "
            f"{avg_bank_balance}",

            "severity": "Low",

            "color": severity_colors["Low"]
        })

    # ==============================
    # RULE 10 — SHORT EMPLOYMENT
    # ==============================

    if employment_years < 2:

        flags.append({

            "rule": "Short Employment History",

            "evidence":
            f"{employment_years} "
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
def get_redflags(req: RedFlagRequest):

    start_time = time.time()

    try:

        result = compute_red_flags(
            req.application_id
        )

        latency_ms = (
            time.time() - start_time
        ) * 1000

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "application_id": req.application_id,
            "latency_ms": round(latency_ms, 2),
            "flag_count": result["flag_count"],
            "rules_triggered": [
                f["rule"]
                for f in result["flags"]
            ],
            "status": "success"
        }

        with open(
            "redflag_detection.log",
            "a"
        ) as f:

            f.write(
                json.dumps(log_entry)
                + "\n"
            )

        result["latency_ms"] = round(
            latency_ms,
            2
        )

        return result

    except Exception as e:

        latency_ms = (
            time.time() - start_time
        ) * 1000

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "application_id": req.application_id,
            "latency_ms": round(latency_ms, 2),
            "status": "error",
            "error": str(e)
        }

        with open(
            "redflag_detection.log",
            "a"
        ) as f:

            f.write(
                json.dumps(log_entry)
                + "\n"
            )

        return {
            "error": str(e)
        }

# ==============================
# BATCH ENDPOINT
# ==============================

@app.post("/api/redflags-batch")
def batch_redflags(req: BatchRequest):

    results = []

    for app_id in req.application_ids:

        flags = compute_red_flags(app_id)

        results.append(flags)

    return {
        "results": results
    }

import json
import time
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loan_apps = pd.read_csv("loan_applications.csv")
bureau = pd.read_csv("bureau_data.csv")
banking = pd.read_csv("bank_statements.csv")
gst = pd.read_csv("gst_filings.csv")

features = loan_apps.merge(bureau, on="application_id", how="left")
features = features.merge(banking, on="application_id", how="left")
features = features.merge(gst, on="application_id", how="left")

print("\nALL AVAILABLE COLUMNS:\n")
print(list(features.columns))

class RedFlagRequest(BaseModel):
    application_id: str

class BatchRequest(BaseModel):
    application_ids: list[str]

severity_colors = {
    "High": "red",
    "Medium": "orange",
    "Low": "yellow"
}

def safe_get(app, possible_columns, default=0):
    for col in possible_columns:
        if col in app.index:
            return app[col]
    return default

def compute_red_flags(application_id):
    app_data = features[features["application_id"] == application_id]

    if len(app_data) == 0:
        return {"error": "Application not found"}

    app = app_data.iloc[0]
    flags = []

    cibil_score = safe_get(app, ["cibil_score"])
    foir = safe_get(app, ["foir"])
    recent_inquiries = safe_get(app, ["num_credit_inquiries_30d"])
    emi_bounces = safe_get(app, ["emi_bounces"])

    missing_gst_quarters = 0
    income_mismatch_pct = 0

    night_txn_flag = safe_get(app, ["is_night_application"])
    past_defaults = safe_get(app, ["has_previous_default"])
    avg_bank_balance = safe_get(app, ["min_eod_balance"])
    employment_years = safe_get(
        app,
        ["employment_years", "work_experience_years"]
    )

    if cibil_score < 600:
        flags.append({
            "rule": "Low CIBIL",
            "evidence": f"CIBIL score is {cibil_score}",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if foir > 60:
        flags.append({
            "rule": "High FOIR",
            "evidence": f"FOIR is {foir}%",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if recent_inquiries >= 3:
        flags.append({
            "rule": "High Inquiries",
            "evidence": f"{recent_inquiries} inquiries in 30 days",
            "severity": "Medium",
            "color": severity_colors["Medium"]
        })

    if emi_bounces >= 1:
        flags.append({
            "rule": "EMI Bounces",
            "evidence": f"{emi_bounces} bounces",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if missing_gst_quarters >= 4:
        flags.append({
            "rule": "GST Filing Gaps",
            "evidence": f"{missing_gst_quarters} missing quarters",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if income_mismatch_pct > 25:
        flags.append({
            "rule": "Income Mismatch",
            "evidence": f"{income_mismatch_pct}% mismatch",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if night_txn_flag == 1:
        flags.append({
            "rule": "Night Transactions",
            "evidence": "Suspicious night transactions",
            "severity": "Medium",
            "color": severity_colors["Medium"]
        })

    if past_defaults >= 1:
        flags.append({
            "rule": "Past Defaults",
            "evidence": f"{past_defaults} past defaults",
            "severity": "High",
            "color": severity_colors["High"]
        })

    if avg_bank_balance < 10000:
        flags.append({
            "rule": "Low Bank Balance",
            "evidence": f"Average balance {avg_bank_balance}",
            "severity": "Low",
            "color": severity_colors["Low"]
        })

    if employment_years < 2:
        flags.append({
            "rule": "Short Employment History",
            "evidence": f"{employment_years} years employment",
            "severity": "Low",
            "color": severity_colors["Low"]
        })

    highest = "None"

    if any(f["severity"] == "High" for f in flags):
        highest = "High"
    elif any(f["severity"] == "Medium" for f in flags):
        highest = "Medium"
    elif any(f["severity"] == "Low" for f in flags):
        highest = "Low"

    return {
        "application_id": application_id,
        "flag_count": len(flags),
        "highest_severity": highest,
        "flags": flags
    }

@app.post("/api/redflags")
def get_redflags(req: RedFlagRequest):
    start_time = time.time()

    try:

    result = compute_red_flags(
        req.application_id
    )

    latency_ms = (
        time.time() - start_time) * 1000

        high_count = sum(
            1 for f in result.get("flags", [])
            if f["severity"] == "High"
        )
        medium_count = sum(
            1 for f in result.get("flags", [])
            if f["severity"] == "Medium"
        )
        low_count = sum(
            1 for f in result.get("flags", [])
            if f["severity"] == "Low"
        )

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "application_id": req.application_id,
            "latency_ms": round(latency_ms, 2),
            "flag_count": result.get("flag_count", 0),
            "high_flags": high_count,
            "medium_flags": medium_count,
            "low_flags": low_count,
            "rules_triggered": [
                f["rule"]
                for f in result.get("flags", [])
            ],
            "status": "success"
        }

        with open("redflag_detection.log", "a") as f:
            f.write(json.dumps(log_entry) + "\\n")

        result["latency_ms"] = round(latency_ms, 2)
        return result

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "application_id": req.application_id,
            "latency_ms": round(latency_ms, 2),
            "status": "error",
            "error": str(e)
        }

        with open("redflag_detection.log", "a") as f:
            f.write(json.dumps(log_entry) + "\\n")

        return {"error": str(e)}

@app.post("/api/redflags-batch")
def batch_redflags(req: BatchRequest):
    start_time = time.time()

    results = []

    for app_id in req.application_ids:
        results.append(compute_red_flags(app_id))

    latency_ms = round((time.time() - start_time) * 1000, 2)

    with open("redflag_detection.log", "a") as f:
        f.write(
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "endpoint": "batch",
                "applications_processed": len(req.application_ids),
                "latency_ms": latency_ms,
                "status": "success"
            }) + "\\n"
        )

    return {
        "results": results,
        "latency_ms": latency_ms
    }
