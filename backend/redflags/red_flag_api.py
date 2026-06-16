from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
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


def send_redflag_alert(application_id, flag, evidence, confidence):
    alert_entry = {
        "timestamp": datetime.now().isoformat(),
        "application_id": application_id,
        "flag_triggered": flag,
        "evidence": evidence,
        "confidence_level": confidence
    }

    with open("redflag_alerts.log", "a") as f:
        f.write(json.dumps(alert_entry) + "\n")


def compute_red_flags(application_id):
    app_data = features[
        features["application_id"] == application_id
    ]

    if len(app_data) == 0:
        return {
            "error": "Application not found"
        }

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

    highest = "Low"

    if any(f["severity"] == "High" for f in flags):
        highest = "High"
    elif any(f["severity"] == "Medium" for f in flags):
        highest = "Medium"

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
        result = compute_red_flags(req.application_id)

        for flag in result["flags"]:
            send_redflag_alert(
                req.application_id,
                flag["rule"],
                flag["evidence"],
                flag["severity"]
            )

        latency_ms = (time.time() - start_time) * 1000

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

        with open("redflag_detection.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

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
            f.write(json.dumps(log_entry) + "\n")

        return {
            "error": str(e)
        }


@app.post("/api/redflags-batch")
def batch_redflags(req: BatchRequest):
    results = []

    for app_id in req.application_ids:
        flags = compute_red_flags(app_id)
        results.append(flags)

    return {
        "results": results
    }
