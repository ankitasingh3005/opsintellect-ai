import psycopg2
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier

# -----------------------------
# Connect to Postgres
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    database="opsintellect",
    user="ops",
    password="ops"
)

# -----------------------------
# Load Silver Data
# -----------------------------
query = """
SELECT
  drivers_available,
  traffic_index,
  system_latency_ms,
  promised_mins,
  priority,
  sla_met
FROM silver.order_features
WHERE sla_met IS NOT NULL
"""

df = pd.read_sql(query, conn)

# Features / Target
X = df.drop(columns=["sla_met"])
y = df["sla_met"].astype(int)

# -----------------------------
# Preprocessing
# -----------------------------
num_features = [
    "drivers_available",
    "traffic_index",
    "system_latency_ms",
    "promised_mins"
]

cat_features = ["priority"]

preprocess = ColumnTransformer(
    transformers=[
        ("num", "passthrough", num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
    ]
)

# -----------------------------
# Model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=12,
    min_samples_split=8,
    min_samples_leaf=4,
    random_state=42,
    class_weight="balanced_subsample"
)

pipeline = Pipeline([
    ("preprocess", preprocess),
    ("model", model)
])

# -----------------------------
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

pipeline.fit(X_train, y_train)

# -----------------------------
# Evaluation
# -----------------------------
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

print("\n📊 Classification Report\n")
print(classification_report(y_test, y_pred))

print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.3f}")

# -----------------------------
# Save Model
# -----------------------------
joblib.dump(pipeline, "ml/sla_risk_model.pkl")
print("\n✅ Model trained and saved successfully.")