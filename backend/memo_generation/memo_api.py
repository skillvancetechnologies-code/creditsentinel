from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import time
from groq import Groq
import requests

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI()

# ==============================
# LOAD DATASETS
# ==============================

loan_apps = pd.read_csv("data/loan_applications.csv")

bureau = pd.read_csv("data/bureau_data.csv")

# ==============================
# MERGE DATASETS
# ==============================

features = loan_apps.merge(
    bureau,
    on="application_id",
    how="left"
)

# ==============================
# REQUEST MODEL
# ==============================

class MemoRequest(BaseModel):
    application_id: str

# ==============================
# GROQ CLIENT
# ==============================

client = Groq(
    api_key="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"
)

# ==============================
# FAST MEMO GENERATION
# ==============================

def generate_memo_fast(prompt):

    start = time.time()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=400,
        temperature=0.3,
    )

    elapsed = round(
        time.time() - start,
        2
    )

    memo = response.choices[0].message.content

    return memo, elapsed

# ==============================
# PARSER
# ==============================

def parse_memo(text):

    reasons = []

    for line in text.split("\n"):

        raw = line.strip()
        upper = raw.upper()

        if "REASON 1" in upper:
            reasons.append(
                raw.split(":", 1)[1].strip()
            )

        elif "REASON 2" in upper:
            reasons.append(
                raw.split(":", 1)[1].strip()
            )

        elif "REASON 3" in upper:
            reasons.append(
                raw.split(":", 1)[1].strip()
            )

    while len(reasons) < 3:
        reasons.append(
            "Additional underwriting review required"
        )

    return reasons[:3]

# ==============================
# API ENDPOINT
# ==============================

@app.post("/api/memo")
def generate_memo(req: MemoRequest):

    try:

        # ==============================
        # FIND APPLICATION
        # ==============================

        app_data = features[
            features["application_id"].astype(str)
            == str(req.application_id)
        ]

        if app_data.empty:

            return {
                "error": "Application not found"
            }

        app_row = app_data.iloc[0]

        # ==============================
        # CALL DIVYA'S API
        # ==============================

        score_response = requests.post(
            "http://localhost:8000/api/score",

            json={
                "application_id": str(
                    req.application_id
                )
            }
        )

        score_data = score_response.json()

        # ==============================
        # SAFE RISK EXTRACTION
        # ==============================

        print("REQUEST ID:", req.application_id)

        print("RAW SCORE RESPONSE:",
              score_response.text)

        print("JSON SCORE DATA:",
              score_data)

        risk_level = str(
    score_data["risk_level"]
).upper().strip()

        risk_score = float(
    score_data["risk_score"]
)
        print("FINAL RISK LEVEL:",
              risk_level)

        print("RISK SCORE:",
              risk_score)

        print("CIBIL SCORE:",
              app_row["cibil_score"])

        print("FOIR:",
              app_row["foir"])

        # ==============================
        # FALLBACK LOGIC
        # ==============================

        if risk_level == "":

            cibil = int(
                app_row["cibil_score"]
            )

            foir = float(
                app_row["foir"]
            )

            if cibil >= 750 and foir < 40:
                risk_level = "LOW"

            elif cibil >= 650 and foir < 60:
                risk_level = "MEDIUM"

            else:
                risk_level = "HIGH"

            print(
                "USING FALLBACK RISK:",
                risk_level
            )

        # ==============================
        # DECISION LOGIC
        # ==============================

        if risk_level == "LOW":

            decision = "APPROVE"

        elif risk_level == "MEDIUM":

            decision = "APPROVE WITH CONDITIONS"

        elif risk_level == "HIGH":

            if risk_score >= 0.85:
                decision = "REJECT"

            else:
                decision = "REVIEW"

        else:
            decision = "REVIEW"

        # ==============================
        # PROMPT FOR GROQ
        # ==============================

        prompt = f"""
Generate professional underwriting reasons.

Application ID:
{app_row['application_id']}

Risk Level:
{risk_level}

Risk Score:
{risk_score}

FOIR:
{app_row['foir']}

CIBIL Score:
{app_row['cibil_score']}

Monthly Income:
{app_row['monthly_income']}

Loan Amount:
{app_row['requested_loan_amount']}

Employment Years:
{app_row['employment_years']}

IMPORTANT:
Do NOT generate risk level.
Do NOT generate decision.

Generate ONLY:

REASON 1: ...
REASON 2: ...
REASON 3: ...
"""

        # ==============================
        # GENERATE MEMO
        # ==============================

        memo, elapsed = generate_memo_fast(
            prompt
        )

        # ==============================
        # PARSE REASONS
        # ==============================

        reasons = parse_memo(memo)

        # ==============================
        # BUILD MEMO SECTIONS
        # ==============================

        profile = (
            f"Applicant {app_row['applicant_name']} applied for a loan of "
            f"₹{app_row['requested_loan_amount']}. "
            f"Monthly income is ₹{app_row['monthly_income']}. "
            f"Employment history shows "
            f"{app_row['employment_years']} years of work experience."
        )

        risk_assessment = (
            f"Overall application risk is classified as "
            f"{risk_level}. "
            f"The evaluated risk score is {risk_score}."
        )

        credit_history = (
            f"Applicant has a CIBIL score of "
            f"{app_row['cibil_score']}. "
            f"Credit behavior analysis was included in "
            f"the underwriting evaluation."
        )

        repayment_capacity = (
            f"FOIR recorded is {app_row['foir']}. "
            f"Income and obligation levels were evaluated "
            f"to determine repayment capacity."
        )

        risk_factors = (
            f"1. {reasons[0]} "
            f"2. {reasons[1]} "
            f"3. {reasons[2]}"
        )

        recommendation = (
            f"Final underwriting recommendation: "
            f"{decision}"
        )

        # ==============================
        # FINAL OUTPUT
        # ==============================

        return {

            "application_id": str(
                app_row["application_id"]
            ),

            "applicant_name": str(
                app_row["applicant_name"]
            ),

            "risk_level": risk_level,

            "risk_score": risk_score,

            "decision": decision,

            "profile": profile,

            "risk_assessment": risk_assessment,

            "credit_history": credit_history,

            "repayment_capacity": repayment_capacity,

            "risk_factors": risk_factors,

            "recommendation": recommendation,

            "generation_time_seconds": elapsed
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "error": "An error occurred while processing the request."
        }
    
