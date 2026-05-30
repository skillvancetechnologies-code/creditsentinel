from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import time
import os
import requests
from groq import Groq
from dotenv import load_dotenv

# ==============================
# LOAD ENVIRONMENT VARIABLES
# Must be called before os.getenv()
# ==============================

load_dotenv()

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI(
    title="Loan Underwriting Memo API",
    description=(
        "AI-powered underwriting memo generation for Indian NBFC loan applications. "
        "Uses CIBIL scores, FOIR analysis, and LLaMA 3.1 via Groq to produce "
        "structured credit assessments in under one second."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API Working"}

# ==============================
# LOAD DATASETS
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

loan_apps = pd.read_csv(os.path.join(BASE_DIR, "loan_applications.csv"))
bureau = pd.read_csv(os.path.join(BASE_DIR, "bureau_data.csv"))

# ==============================
# MERGE DATASETS
# ==============================

features = loan_apps.merge(bureau, on="application_id", how="left")

# ==============================
# REQUEST MODEL
# ==============================

class MemoRequest(BaseModel):
    application_id: str

# ==============================
# GROQ CLIENT
# Loaded securely from .env — never hardcode API keys in source code
# ==============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Create a .env file with GROQ_API_KEY=your_key_here "
        "or set it as an environment variable before starting the server."
    )

client = Groq(api_key=GROQ_API_KEY)

# ==============================
# FAST MEMO GENERATION
# ==============================

def generate_memo_fast(prompt: str):
    start = time.time()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.3,
    )

    elapsed = time.time() - start
    memo = response.choices[0].message.content
    return memo, elapsed

# ==============================
# PARSER
# ==============================

def parse_memo(text: str):
    reasons = []

    for line in text.split("\n"):
        raw = line.strip()
        upper = raw.upper()

        if "REASON 1" in upper:
            parts = raw.split(":", 1)
            if len(parts) > 1:
                reasons.append(parts[1].strip())

        elif "REASON 2" in upper:
            parts = raw.split(":", 1)
            if len(parts) > 1:
                reasons.append(parts[1].strip())

        elif "REASON 3" in upper:
            parts = raw.split(":", 1)
            if len(parts) > 1:
                reasons.append(parts[1].strip())

    while len(reasons) < 3:
        reasons.append("Additional underwriting review required")

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
            features["application_id"].astype(str) == str(req.application_id)
        ]

        if app_data.empty:
            return {"error": f"Application ID '{req.application_id}' not found"}

        app_row = app_data.iloc[0]

        # ==============================
        # CALL EXTERNAL CREDIT SCORE API (optional / non-fatal)
        # FIX: Corrected URL from /docs#/ to actual endpoint
        # FIX: Wrapped in try/except so a failure here does not crash the memo
        # ==============================

        score_data = {}
        try:
            score_response = requests.post(
                "https://creditsentinel-api.onrender.com/api/score",
                json={"application_id": str(req.application_id)},
                timeout=10,
            )
            score_response.raise_for_status()
            score_data = score_response.json()
            print("External score API response:", score_data)
        except Exception as ext_err:
            print(f"External score API failed (non-fatal): {ext_err}")
            score_data = {}

        # ==============================
        # RISK SCORE CALCULATION
        # ==============================

        cibil = int(app_row["cibil_score"])
        foir = float(app_row["foir"])

        cibil_component = (cibil - 300) / 600
        foir_component = (100 - foir) / 100

        risk_score = (cibil_component * 0.55 + foir_component * 0.45) * 0.72

        # ==============================
        # RISK LEVEL
        # ==============================

        if risk_score >= 0.70:
            risk_level = "LOW"
        elif risk_score >= 0.50:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        print(f"FINAL RISK LEVEL: {risk_level}")
        print(f"RISK SCORE: {risk_score:.4f}")
        print(f"CIBIL SCORE: {cibil}")
        print(f"FOIR: {foir}")

        # ==============================
        # DECISION LOGIC
        # ==============================

        if risk_level == "LOW":
            decision = "APPROVE"
        elif risk_level == "MEDIUM":
            decision = "APPROVE WITH CONDITIONS"
        else:
            decision = "REJECT"

        # ==============================
        # PROMPT
        # ==============================

        prompt = f"""
Generate professional underwriting reasons.

Application ID: {app_row['application_id']}
Risk Level: {risk_level}
Risk Score: {risk_score:.4f}
FOIR: {app_row['foir']}
CIBIL Score: {app_row['cibil_score']}
Monthly Income: {app_row['monthly_income']}
Loan Amount: {app_row['requested_loan_amount']}
Employment Years: {app_row['employment_years']}

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

        memo, elapsed = generate_memo_fast(prompt)

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
            f"Applicant {app_row['applicant_name']} applied for a loan of "
            f"₹{app_row['requested_loan_amount']}. "
            f"Monthly income is ₹{app_row['monthly_income']}. "
            f"Employment history shows {app_row['employment_years']} years of work experience."
        )

        risk_assessment = (
            f"Overall application risk is classified as {risk_level}. "
            f"The evaluated risk score is {risk_score:.4f}."
        )

        credit_history = (
            f"Applicant has a CIBIL score of {app_row['cibil_score']}. "
            f"Credit behavior analysis was included in underwriting evaluation."
        )

        repayment_capacity = (
            f"FOIR recorded is {app_row['foir']}. "
            f"Income and obligation levels were evaluated to determine repayment capacity."
        )

        risk_factors = (
            f"1. {reasons[0]} "
            f"2. {reasons[1]} "
            f"3. {reasons[2]}"
        )

        recommendation = f"Final underwriting recommendation: {decision}"

        # ==============================
        # FINAL RESPONSE
        # ==============================

        return {
            "application_id": str(app_row["application_id"]),
            "applicant_name": str(app_row["applicant_name"]),
            "risk_level": risk_level,
            "risk_tier": risk_level,
            "risk_score": round(risk_score, 4),
            "decision": decision,
            "profile": profile,
            "risk_assessment": risk_assessment,
            "credit_history": credit_history,
            "repayment_capacity": repayment_capacity,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "generation_time_seconds": round(elapsed, 3),
        }

    except Exception as e:
        print(f"FULL ERROR: {e}")
        return {"error": str(e)}
