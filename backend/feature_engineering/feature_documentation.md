# Feature Documentation
### `backend/feature_engineering/feature_engine.py`

This document describes all **43 features** computed by the feature engineering pipeline for loan application risk scoring. Features are derived from four data sources and grouped into six logical categories.

---

## Data Sources

| Identifier | File | Description |
|------------|------|-------------|
| `loans` | `loan_applications.csv` | Applicant profile, loan request details, employment info |
| `bureau` | `bureau_data.csv` | Credit bureau pull — CIBIL score, inquiries, active loans |
| `bank` | `bank_statements.csv` | Month-wise bank statement data — balances, credits, bounces |
| `gst` | `gst_filings.csv` | GST filing history — quarters filed, missing, or delayed |

---

## Feature Groups

- [1. Loan Profile Features](#1-loan-profile-features) — 7 features
- [2. Applicant Risk Features](#2-applicant-risk-features) — 6 features
- [3. Bureau / Credit Features](#3-bureau--credit-features) — 13 features
- [4. Bank Statement Features](#4-bank-statement-features) — 11 features
- [5. GST & Employment Features](#5-gst--employment-features) — 4 features
- [6. Behavioural / Application Features](#6-behavioural--application-features) — 2 features

---

## 1. Loan Profile Features

Raw fields extracted directly from the loan application record.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 1 | `monthly_income` | float | `loans` | Applicant's declared monthly income in INR |
| 2 | `requested_loan_amount` | float | `loans` | Total loan amount requested by the applicant |
| 3 | `existing_monthly_emi` | float | `loans` | Sum of EMIs the applicant is currently paying on other loans |
| 4 | `employment_years` | float | `loans` | Number of years the applicant has been continuously employed |
| 5 | `foir` | float | `loans` | Fixed Obligations to Income Ratio — total EMI burden as % of income |
| 6 | `loan_to_income_ratio` | float | `loans` | Ratio of requested loan amount to annual income; measures loan size relative to earnings |
| 7 | `is_night_application` | int (0/1) | `loans` | Flag indicating the application was submitted between 11 PM and 5 AM |

---

## 2. Applicant Risk Features

Derived signals based on the applicant's personal and demographic profile.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 8 | `dependents` | int | `loans` | Number of financial dependents declared by the applicant |
| 9 | `high_dependents` | int (0/1) | `loans` | Flag set to 1 if dependents ≥ 4, indicating elevated household financial burden |
| 10 | `is_tier3` | int (0/1) | `loans` | Flag set to 1 if the applicant resides in a Tier-3 city, associated with lower income stability |
| 11 | `age_group_risk` | int (0/1) | `loans` | Flag set to 1 if applicant age is below 21 or above 58 — boundary age groups with higher default rates |
| 12 | `short_employment` | int (0/1) | `loans` | Flag set to 1 if employment tenure is less than 1 year, indicating job instability |
| 13 | `high_loan_short_emp` | int (0/1) | `loans` | Combined risk flag: short employment AND loan-to-income ratio > 4 simultaneously |

---

## 3. Bureau / Credit Features

Features derived from the credit bureau pull (CIBIL). Captures creditworthiness, borrowing behaviour, and repayment history.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 14 | `cibil_score` | int | `bureau` | Applicant's CIBIL credit score; ranges from 300 to 900 |
| 15 | `num_credit_inquiries_30d` | int | `bureau` | Number of hard credit inquiries made in the last 30 days |
| 16 | `num_credit_inquiries_90d` | int | `bureau` | Number of hard credit inquiries made in the last 90 days |
| 17 | `has_previous_default` | int (0/1) | `bureau` | Flag set to 1 if the applicant has any prior loan default on record |
| 18 | `credit_utilization_pct` | float | `bureau` | Percentage of total available revolving credit currently in use |
| 19 | `credit_age_months` | int | `bureau` | Age of the applicant's oldest credit account in months |
| 20 | `num_active_loans` | int | `bureau` | Total count of loans currently active and being serviced |
| 21 | `num_existing_loans` | int | `bureau` | Alias for `num_active_loans`; used explicitly in downstream risk scoring rules |
| 22 | `low_cibil` | int (0/1) | `bureau` | Flag set to 1 if CIBIL score is below 650 — high credit risk threshold |
| 23 | `high_inquiries` | int (0/1) | `bureau` | Flag set to 1 if 3 or more hard inquiries occurred in the last 30 days |
| 24 | `foir_cibil_risk` | int (0/1) | `loans` + `bureau` | Combined flag: FOIR > 55% AND CIBIL < 680 — over-leveraged applicant with weak credit |
| 25 | `high_utilization` | int (0/1) | `bureau` | Flag set to 1 if credit utilization exceeds 70%, signalling credit dependency |
| 26 | `inquiry_velocity` | float | `bureau` | Ratio of 30-day to 90-day inquiries; a high value indicates a recent surge in credit-seeking |
| 27 | `multiple_loans` | int (0/1) | `bureau` | Flag set to 1 if the applicant has 3 or more active loans simultaneously |

---

## 4. Bank Statement Features

Features derived from month-wise bank statement data. Captures cash flow health, balance behaviour, and payment reliability.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 28 | `total_emi_bounces` | int | `bank` | Total number of EMI bounce events across all statement months on record |
| 29 | `avg_emi_bounces` | float | `bank` | Average EMI bounces per month — smooths out outlier months |
| 30 | `avg_min_balance` | float | `bank` | Average of the minimum end-of-day balance across all statement months |
| 31 | `avg_credits` | float | `bank` | Average monthly total credits; used as a proxy for actual take-home income |
| 32 | `income_bank_mismatch` | float | `loans` + `bank` | Percentage difference between declared income and average bank credits; flags income inflation |
| 33 | `has_emi_bounces` | int (0/1) | `bank` | Flag set to 1 if any EMI bounce has occurred in the statement period |
| 34 | `low_balance_flag` | int (0/1) | `bank` | Flag set to 1 if average minimum balance is below ₹5,000 — indicates chronic low liquidity |
| 35 | `inquiry_bounce_combo` | int (0/1) | `bureau` + `bank` | Combined flag: high recent inquiries AND at least one EMI bounce — dual stress signal |
| 36 | `total_cheque_bounces` | int | `bank` | Total cheque bounce events across all statement months (0 if column absent) |
| 37 | `has_cheque_bounces` | int (0/1) | `bank` | Flag set to 1 if any cheque bounce has occurred in the statement period |
| 38 | `salary_months` | int | `bank` | Count of months where a salary credit was detected in the bank statement |
| 39 | `irregular_salary` | int (0/1) | `bank` | Flag set to 1 if salary credits appear in fewer than 70% of statement months |

---

## 5. GST & Employment Features

Features that combine GST filing compliance with employment type to assess self-employed applicant risk.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 40 | `gst_missing_quarters` | int | `gst` | Count of GST quarters with filing status marked as "Missing" |
| 41 | `is_self_employed` | int (0/1) | `loans` | Flag set to 1 if employment type is "Self-Employed" |
| 42 | `self_emp_gst_risk` | int (0/1) | `loans` + `gst` | Combined flag: self-employed AND 2 or more missing GST quarters — unreliable income signal |

---

## 6. Behavioural / Application Features

Features that capture the context and timing of the loan application itself.

| # | Feature | Type | Source | Description |
|---|---------|------|--------|-------------|
| 43 | `night_high_foir` | int (0/1) | `loans` | Combined flag: application submitted at night AND FOIR > 50% — distress-driven application pattern |

---

## Summary

| Category | Features | Sources Used |
|----------|----------|--------------|
| Loan Profile | 7 | `loans` |
| Applicant Risk | 6 | `loans` |
| Bureau / Credit | 14 | `bureau`, `loans` |
| Bank Statement | 11 | `bank`, `bureau`, `loans` |
| GST & Employment | 3 | `gst`, `loans` |
| Behavioural | 1 | `loans` |
| **Total** | **43** | |

---

## Derived vs Raw Features

| Type | Count | Description |
|------|-------|-------------|
| Raw | 18 | Directly read from a source CSV with no transformation |
| Derived | 25 | Computed via thresholds, ratios, or cross-source logic |

---

*Generated from `backend/feature_engineering/feature_engine.py`*
