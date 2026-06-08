# Evaluation API Documentation

## Endpoint

POST /api/evaluate

## Description

Evaluates generated memo sections and returns:
- Score
- Validation checks
- Pass/Fail status
- Recommendation

## Request Format

{
  "section_type": "credit_history",
  "output": "Applicant has a CIBIL score of 742 with strong repayment history."
}

## Response Format

{
  "section_type": "credit_history",
  "score": 5.0,
  "max_score": 5.0,
  "checks": {
    "contains_cibil": true,
    "within_limit": true
  },
  "passed": true,
  "recommendation": "APPROVE"
}

## Validation Rules

1. CIBIL mention check
2. Word limit check (<= 80 words)

## Error Codes

- 200 : Success
- 422 : Validation Error

## Deployment

Render URL:
https://creditsentinel-0yom.onrender.com/docs

## Dependencies

- FastAPI
- Pydantic
- Uvicorn
