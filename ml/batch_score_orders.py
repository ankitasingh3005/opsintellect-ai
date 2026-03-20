import joblib
import pandas as pd
import psycopg2
from datetime import datetime

# Load trained model
model = joblib.load("ml/sla_risk_model.pkl")

# Connect to DB
conn = psycopg2.connect(
    host="localhost",
    database="opsintellect",
    user="ops",
    password="ops"
)
cursor = conn.cursor()

# Pull feature data from Silver
query = """
SELECT
    order_id,
    drivers_available,
    traffic_index,
    system_latency_ms,
    priority,
    promised_mins
FROM silver.order_features;
"""

df = pd.read_sql(query, conn)

# Predict probabilities
probs = model.predict_proba(df.drop(columns=["order_id"]))[:, 0]

df["sla_risk_probability"] = probs

# Risk category logic
def categorize(p):
    if p >= 0.7:
        return "HIGH"
    elif p >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"

df["risk_category"] = df["sla_risk_probability"].apply(categorize)
df["prediction_timestamp"] = datetime.now()

# Insert into Gold table
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO gold.order_risk_predictions
        (order_id, sla_risk_probability, risk_category, prediction_timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (order_id)
        DO UPDATE SET
            sla_risk_probability = EXCLUDED.sla_risk_probability,
            risk_category = EXCLUDED.risk_category,
            prediction_timestamp = EXCLUDED.prediction_timestamp;
    """, (
        row["order_id"],
        float(row["sla_risk_probability"]),
        row["risk_category"],
        row["prediction_timestamp"]
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Batch scoring complete. Gold table updated.")