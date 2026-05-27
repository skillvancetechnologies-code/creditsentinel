from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import time
from groq import Groq
import requests

# ==============================
# FASTAPI APP
# ==============================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ADD THIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# your APIs
@app.get("/")
def home():
    return {"message": "API Working"}

# ==============================
# LOAD DATASETS
# ==============================

loan_apps = pd.read_csv(
    r"C:\Users\sunny\Desktop\loan_applications.csv"
)

bureau = pd.read_csv(
    r"C:\Users\sunny\Desktop\bureau_data.csv"
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
# REQUEST MODEL
# ==============================

class MemoRequest(BaseModel):

    application_id: str

# ==============================
# GROQ CLIENT
# ==============================

client = Groq(
    api_key="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")

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

    elapsed = time.time() - start

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

            parts = raw.split(":", 1)

            if len(parts) > 1:

                reasons.append(
                    parts[1].strip()
                )

        elif "REASON 2" in upper:

            parts = raw.split(":", 1)

            if len(parts) > 1:

                reasons.append(
                    parts[1].strip()
                )

        elif "REASON 3" in upper:

            parts = raw.split(":", 1)

            if len(parts) > 1:

                reasons.append(
                    parts[1].strip()
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
            "https://creditsentinel-api.onrender.com/docs#/",
            json={
                "application_id": str(
                    req.application_id
                )
            }
        )

        score_data = score_response.json()


        # ==============================
        # RISK SCORE CALCULATION
        # ==============================

        cibil = int(
            app_row["cibil_score"]
        )

        foir = float(
            app_row["foir"]
        )

        cibil_component = (
            cibil - 300
        ) / 600

        foir_component = (
            100 - foir
        ) / 100

        risk_score = (
            (
                cibil_component * 0.55
                +
                foir_component * 0.45
            )
        )

        risk_score = (
            risk_score * 0.72
        )

        # ==============================
        # RISK LEVEL
        # ==============================

        if risk_score >= 0.70:

            risk_level = "LOW"

        elif risk_score >= 0.50:

            risk_level = "MEDIUM"

        else:

            risk_level = "HIGH"

        print(
            "FINAL RISK LEVEL:",
            risk_level
        )

        print(
            "RISK SCORE:",
            risk_score
        )

        print(
            "CIBIL SCORE:",
            cibil
        )

        print(
            "FOIR:",
            foir
        )

        # ==============================
        # DECISION LOGIC
        # ==============================

        if risk_level == "LOW":

            decision = "APPROVE"

        elif risk_level == "MEDIUM":

            decision = (
                "APPROVE WITH CONDITIONS"
            )

        elif risk_level == "HIGH":

            decision = "REJECT"

        else:

            decision = (
                "APPROVE WITH CONDITIONS"
            )

        # ==============================
        # PROMPT
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

        print("RAW MEMO:")
        print(memo)

        # ==============================
        # PARSE REASONS
        # ==============================

        reasons = parse_memo(memo)

        # ==============================
        # BUILD MEMO SECTIONS
        # ==============================

        profile = (
            f"Applicant {app_row['applicant_name']} "
            f"applied for a loan of "
            f"₹{app_row['requested_loan_amount']}. "
            f"Monthly income is "
            f"₹{app_row['monthly_income']}. "
            f"Employment history shows "
            f"{app_row['employment_years']} years "
            f"of work experience."
        )

        risk_assessment = (
            f"Overall application risk is "
            f"classified as {risk_level}. "
            f"The evaluated risk score is "
            f"{risk_score}."
        )

        credit_history = (
            f"Applicant has a CIBIL score of "
            f"{app_row['cibil_score']}. "
            f"Credit behavior analysis was "
            f"included in underwriting evaluation."
        )

        repayment_capacity = (
            f"FOIR recorded is "
            f"{app_row['foir']}. "
            f"Income and obligation levels were "
            f"evaluated to determine repayment "
            f"capacity."
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
        # FINAL RESPONSE
        # ==============================

        return {

            "application_id": str(
                app_row["application_id"]
            ),

            "applicant_name": str(
                app_row["applicant_name"]
            ),

            "risk_level": risk_level,

            "risk_tier": risk_level,

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

        print(
            "FULL ERROR:",
            str(e)
        )

        return {
            "error": str(e)
        }
