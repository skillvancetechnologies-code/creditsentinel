import pandas as pd
import lightgbm as lgb
import joblib
import re

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# =====================================================
# RETRAINING TRIGGER
# =====================================================

NEW_APPLICATIONS = 1200

if NEW_APPLICATIONS < 1000:
    print("No retraining required.")
    exit()

print("ALERT: Retraining Triggered")

# =====================================================
# LOAD DATA
# =====================================================

features = pd.read_csv("features_final.csv")
repayment = pd.read_csv("repayment_history.csv")

df = features.merge(
    repayment[["application_id", "is_default"]],
    on="application_id"
)

# =====================================================
# LAST 5000 APPLICATIONS
# =====================================================

df = df.sort_values("application_id")
df = df.tail(5000)

# =====================================================
# PREPROCESSING
# =====================================================

if "application_id" in df.columns:
    df.drop(columns=["application_id"], inplace=True)

categorical_cols = [
    "employment_type",
    "city_tier"
]

df = pd.get_dummies(
    df,
    columns=categorical_cols,
    drop_first=True
)

def sanitize_col_names(df):
    cols = []

    for col in df.columns:
        col = re.sub(r'[^A-Za-z0-9_]+', '_', col)
        col = re.sub(r'__+', '_', col)
        col = col.strip('_')
        cols.append(col)

    df.columns = cols
    return df

df = sanitize_col_names(df)

df = df.fillna(df.median(numeric_only=True))

# =====================================================
# FEATURES / TARGET
# =====================================================

X = df.drop(columns=["is_default"])
y = df["is_default"]

# =====================================================
# LEAKAGE CHECK
# =====================================================

leakage_columns = [
    "future_payment",
    "repayment_status"
]

found_leakage = [
    col for col in leakage_columns
    if col in X.columns
]

leakage_pass = len(found_leakage) == 0

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =====================================================
# CLASS IMBALANCE
# =====================================================

negative = sum(y_train == 0)
positive = sum(y_train == 1)

ratio = negative / positive

# =====================================================
# CURRENT MODEL
# =====================================================

current_model = joblib.load(
    "lightgbm_0.8106.pkl"
)

current_auc = 0.8106

# =====================================================
# TRAIN NEW MODEL
# =====================================================

model = lgb.LGBMClassifier(
    scale_pos_weight=ratio,
    n_estimators=200,
    max_depth=3,
    learning_rate=0.05,
    num_leaves=50,
    min_child_samples=20,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=42,
    verbose=-1
)

model.fit(X_train, y_train)

preds = model.predict_proba(X_test)[:, 1]

new_auc = roc_auc_score(
    y_test,
    preds
)

# =====================================================
# AUC VALIDATION
# =====================================================

auc_pass = new_auc >= 0.86

# =====================================================
# FEATURE IMPORTANCE VALIDATION
# =====================================================

new_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

new_top10 = set(
    new_importance
    .sort_values("importance", ascending=False)
    .head(10)["feature"]
)

current_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": current_model.feature_importances_
})

current_top10 = set(
    current_importance
    .sort_values("importance", ascending=False)
    .head(10)["feature"]
)

overlap = len(
    current_top10.intersection(new_top10)
)

importance_pass = overlap >= 7

# =====================================================
# DEPLOYMENT DECISION
# =====================================================

if auc_pass and importance_pass and leakage_pass:

    decision = "DEPLOY"

    joblib.dump(
        model,
        "production_model.pkl"
    )

    print("ALERT: New Model Deployed")

else:

    decision = "REJECT"

    print("ALERT: Model Rejected")

# =====================================================
# LOGGING
# =====================================================

log_line = (
    f"{datetime.now()} | "
    f"Applications=5000 | "
    f"CurrentAUC={current_auc:.4f} | "
    f"NewAUC={new_auc:.4f} | "
    f"FeatureOverlap={overlap}/10 | "
    f"Decision={decision}\n"
)

with open("MODEL_RETRAINING_LOG.txt", "a") as f:
    f.write(log_line)
# =====================================================
# SUMMARY
# =====================================================

print("\n===== RETRAINING SUMMARY =====")

print(f"Current AUC : {current_auc:.4f}")
print(f"New AUC     : {new_auc:.4f}")

print(f"AUC Pass            : {auc_pass}")
print(f"Importance Pass     : {importance_pass}")
print(f"Leakage Pass        : {leakage_pass}")

print(f"Top10 Overlap       : {overlap}/10")

print(f"Decision            : {decision}")