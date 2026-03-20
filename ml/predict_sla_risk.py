import joblib
import pandas as pd

# Load model
model = joblib.load("ml/sla_risk_model.pkl")

def predict_risk(order_features: dict):

    df = pd.DataFrame([order_features])

    # Probability that SLA will be met (class 1)
    success_prob = float(model.predict_proba(df)[0][1])

    # Convert to failure risk
    risk_prob = 1 - success_prob

    # Risk level categorization
    if risk_prob >= 0.7:
        risk_level = "HIGH RISK 🔴"
    elif risk_prob >= 0.3:
        risk_level = "MEDIUM RISK 🟡"
    else:
        risk_level = "LOW RISK 🟢"

    # English explanation
    if risk_prob >= 0.5:
        message = "This order is likely to MISS the SLA."
    else:
        message = "This order is likely to MEET the SLA."

    print("\n========= SLA RISK PREDICTION =========")
    print("Input Features:")
    print(order_features)
    print("---------------------------------------")
    print(f"Probability SLA will be met : {round(success_prob, 3)}")
    print(f"Probability SLA will fail   : {round(risk_prob, 3)}")
    print(f"Risk Category               : {risk_level}")
    print(f"Conclusion                  : {message}")
    print("=======================================\n")


# Example test
if __name__ == "__main__":

    sample = {
    "drivers_available": 0,
    "traffic_index": 3.5,
    "system_latency_ms": 600,
    "priority": "HIGH",
    "promised_mins": 20
}

    predict_risk(sample)