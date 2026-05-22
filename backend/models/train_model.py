import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# Load updated 43-feature dataset
features = pd.read_csv('features_final.csv')
df_rep = pd.read_csv('repayment_history.csv')

# Merge target
df = features.merge(
    df_rep[['application_id', 'is_default']],
    on='application_id'
)

# Drop unwanted columns
drop_cols = ['application_id']

for col in drop_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# Identify categorical columns for encoding
categorical_cols = ['employment_type', 'city_tier']

# Apply one-hot encoding to categorical columns
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Fill missing values
df = df.fillna(df.median(numeric_only=True))

# Split features and target
X = df.drop(columns=['is_default'])
y = df['is_default']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Calculate scale_pos_weight
negative_samples = sum(y_train == 0)
positive_samples = sum(y_train == 1)

ratio = negative_samples / positive_samples

print("scale_pos_weight =", ratio)

# Final LightGBM model
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

# Train
model.fit(X_train, y_train)

# Predict
preds = model.predict_proba(X_test)[:, 1]

# AUC
auc = roc_auc_score(y_test, preds)

print(f"\nNew AUC Score: {auc:.4f}")

# Feature importance
importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Features:")
print(importance.head(10).to_string(index=False))

# Save model
model_name = f'lightgbm_{auc:.4f}.pkl'

joblib.dump(model, model_name)                  

print(f"\nModel saved as: {model_name}")
