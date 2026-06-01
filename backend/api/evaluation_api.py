from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load application data once
df = pd.read_csv("./data/loan_applications.csv")


class EvalRequest(BaseModel):
    application_id: str
    section_type: str
    output: str


@app.get("/")
def home():
    return {
        "message": "Evaluation API is running successfully"
    }


@app.post("/api/evaluate")
def evaluate(req: EvalRequest):

    applicant = df[df["application_id"] == req.application_id]

    if applicant.empty:
        return {
            "error": f"Application ID {req.application_id} not found"
        }

    applicant = applicant.iloc[0]

    score = 0
    checks = {}

    # Income Check
    if applicant["monthly_income"] >= 50000:
        score += 1
        checks["income_good"] = True
    else:
        checks["income_good"] = False

    # Employment Stability Check
    if applicant["employment_years"] >= 3:
        score += 1
        checks["employment_stable"] = True
    else:
        checks["employment_stable"] = False

    # FOIR Check
    if applicant["foir"] <= 40:
        score += 1
        checks["foir_acceptable"] = True
    else:
        checks["foir_acceptable"] = False

    # Loan To Income Ratio Check
    if applicant["loan_to_income_ratio"] <= 5:
        score += 1
        checks["loan_ratio_safe"] = True
    else:
        checks["loan_ratio_safe"] = False

    # Existing Loans Check
    if applicant["num_existing_loans"] <= 2:
        score += 1
        checks["existing_loans_ok"] = True
    else:
        checks["existing_loans_ok"] = False

    final_score = round((score / 5) * 5, 1)

    passed = final_score >= 4.0

    if final_score >= 4.0:
        recommendation = "APPROVE"
    elif final_score >= 2.5:
        recommendation = "REVIEW"
    else:
        recommendation = "REJECT"

    return {
        "application_id": req.application_id,
        "section_type": req.section_type,
        "score": final_score,
        "max_score": 5.0,
        "checks": checks,
        "passed": passed,
        "recommendation": recommendation,
        "monthly_income": float(applicant["monthly_income"]),
        "employment_years": float(applicant["employment_years"]),
        "foir": float(applicant["foir"]),
        "loan_to_income_ratio": float(applicant["loan_to_income_ratio"]),
        "num_existing_loans": int(applicant["num_existing_loans"])
    }
