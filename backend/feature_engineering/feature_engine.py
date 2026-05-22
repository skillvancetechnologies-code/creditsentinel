import pandas as pd
import numpy as np
import os

# ── Relative paths (works everywhere: VS Code, Colab, any machine) ────
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR, "data", "samples"
)

# ── Load datasets ─────────────────
df_loans = pd.read_csv(
    os.path.join(DATA_DIR, "loan_applications.csv")
)

df_bank = pd.read_csv(
    os.path.join(DATA_DIR, "bank_statements.csv")
)

df_bur = pd.read_csv(
    os.path.join(DATA_DIR, "bureau_data.csv")
)

df_gst = pd.read_csv(
    os.path.join(DATA_DIR, "gst_filings.csv")
)


def compute_features(
    application_id,
    loans_df=None,
    bank_df=None,
    bur_df=None,
    gst_df=None
):
    """
    Core feature computation.
    """

    # ── Use passed dataframes or global ones ─────────────────
    loans_df = loans_df if loans_df is not None else df_loans
    bank_df = bank_df if bank_df is not None else df_bank
    bur_df = bur_df if bur_df is not None else df_bur
    gst_df = gst_df if gst_df is not None else df_gst

    # ── Filter application data ─────────────────
    loan = loans_df[
        loans_df["application_id"] == application_id
    ].iloc[0]

    bank = bank_df[
        bank_df["application_id"] == application_id
    ]

    bur = bur_df[
        bur_df["application_id"] == application_id
    ].iloc[0]

    gst = gst_df[
        gst_df["application_id"] == application_id
    ]

    # ── Feature Engineering ─────────────────
    features = {

        # Loan features
        "monthly_income": loan["monthly_income"],
        "requested_loan_amount": loan["requested_loan_amount"],
        "existing_monthly_emi": loan["existing_monthly_emi"],
        "employment_years": loan["employment_years"],
        "foir": loan["foir"],
        "loan_to_income_ratio": loan["loan_to_income_ratio"],
        "is_night_application": loan["is_night_application"],

        # Bureau features
        "cibil_score": bur["cibil_score"],
        "num_credit_inquiries_30d": bur["num_credit_inquiries_30d"],
        "num_credit_inquiries_90d": bur["num_credit_inquiries_90d"],
        "has_previous_default": bur["has_previous_default"],
        "credit_utilization_pct": bur["credit_utilization_pct"],
        "credit_age_months": bur["credit_age_months"],
        "num_active_loans": bur["num_active_loans"],
    }

    # ── Derived Features ─────────────────
    features["short_employment"] = int(
        loan["employment_years"] < 1
    )

    features["high_loan_short_emp"] = int(
        features["short_employment"] == 1
        and loan["loan_to_income_ratio"] > 4
    )

    features["dependents"] = int(loan["dependents"]) if "dependents" in loan.index else 0

    features["high_dependents"] = int(
        features["dependents"] >= 4
    )

    features["is_tier3"] = int(loan["city_tier"] == 3) if "city_tier" in loan.index else 0

    if "age" in loan.index:
        features["age_group_risk"] = 1 if (loan["age"] < 21 or loan["age"] > 58) else 0
    else:
        features["age_group_risk"] = 0

    features["num_existing_loans"] = bur["num_active_loans"]

    features["low_cibil"] = int(
        bur["cibil_score"] < 650
    )

    features["high_inquiries"] = int(
        bur["num_credit_inquiries_30d"] >= 3
    )

    features["foir_cibil_risk"] = int(
        loan["foir"] > 55 and bur["cibil_score"] < 680
    )

    features["high_utilization"] = int(
        bur["credit_utilization_pct"] > 70
    )

    features["inquiry_velocity"] = float(
        bur["num_credit_inquiries_30d"] / max(bur["num_credit_inquiries_90d"], 1)
    )

    features["multiple_loans"] = int(
        bur["num_active_loans"] >= 3
    )

    # ── Bank Features ─────────────────
    features["total_emi_bounces"] = int(
        bank["emi_bounces"].sum()
    )

    features["avg_emi_bounces"] = float(
        bank["emi_bounces"].mean()
    )

    features["avg_min_balance"] = float(
        bank["min_eod_balance"].mean()
    )

    features["avg_credits"] = float(
        bank["total_credits"].mean()
    )

    features["income_bank_mismatch"] = float(
        abs(
            loan["monthly_income"]
            - features["avg_credits"]
        )
        / max(loan["monthly_income"], 1)
        * 100
    )

    features["has_emi_bounces"] = int(
        features["total_emi_bounces"] > 0
    )

    features["low_balance_flag"] = int(
        features["avg_min_balance"] < 5000
    )

    features["inquiry_bounce_combo"] = int(
        features["high_inquiries"] == 1 and features["has_emi_bounces"] == 1
    )

    if "cheque_bounces" in bank.columns:
        features["total_cheque_bounces"] = int(bank["cheque_bounces"].sum())
        features["has_cheque_bounces"] = int(features["total_cheque_bounces"] > 0)
    else:
        features["total_cheque_bounces"] = 0
        features["has_cheque_bounces"] = 0

    if "salary_credit" in bank.columns:
        salary_months = bank[bank["salary_credit"] > 0]
        features["salary_months"] = int(len(salary_months))
        features["irregular_salary"] = int(len(salary_months) < max(len(bank) * 0.7, 1))
    else:
        features["salary_months"] = 0
        features["irregular_salary"] = 0

    # ── GST Features ─────────────────
    missing_gst = gst[
        gst["filing_status"] == "Missing"
    ]

    features["gst_missing_quarters"] = len(
        missing_gst
    )

    features["is_self_employed"] = int(
        loan["employment_type"]
        == "Self-Employed"
    )

    features["self_emp_gst_risk"] = int(
        features["is_self_employed"] == 1 and features["gst_missing_quarters"] >= 2
    )

    # ── Behavioural / Application Features ─────────────────
    features["night_high_foir"] = int(
        loan["is_night_application"] == 1 and loan["foir"] > 50
    )

    # ── Return all features ─────────────────
    return features


# ── API Bridge Function ─────────────────
def compute_features_for_application(
    application_id: str
) -> dict:

    # Reload fresh CSVs every API call
    loans_df = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "loan_applications.csv"
        )
    )

    bank_df = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "bank_statements.csv"
        )
    )

    bur_df = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "bureau_data.csv"
        )
    )

    gst_df = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "gst_filings.csv"
        )
    )

    # Validate application id
    if application_id not in loans_df[
        "application_id"
    ].values:

        raise ValueError(
            f"Application ID '{application_id}' not found."
        )

    # Compute features
    features = compute_features(
        application_id,
        loans_df=loans_df,
        bank_df=bank_df,
        bur_df=bur_df,
        gst_df=gst_df
    )

    return features


# ── Run script directly ─────────────────
if __name__ == "__main__":

    application_id = "APP-000001"

    result = compute_features(
        application_id
    )

    print("=" * 60)
    print("FEATURE ENGINEERING OUTPUT")
    print("=" * 60)

    print(
        f"Application ID: {application_id}"
    )

    print(
        f"Total Features: {len(result)}"
    )

    print("\nFeature Names:")
    print(list(result.keys()))

    print("\nFeature Values:")

    for key, value in result.items():
        print(f"{key}: {value}")
