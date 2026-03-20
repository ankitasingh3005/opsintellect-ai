from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="SLA Risk API", version="1.0")
model = joblib.load("ml/sla_risk_model.pkl")

class OrderFeatures(BaseModel):
    drivers_available: int
    traffic_index: float
    system_latency_ms: int
    priority: str
    promised_mins: int

def build_reasoning(order):
    reasons = []
    improvements = []

    if order.drivers_available <= 5:
        reasons.append("driver availability is very low")
        improvements.append("increase available drivers")
    elif order.drivers_available <= 15:
        reasons.append("driver availability is somewhat limited")
        improvements.append("add a few more drivers")

    if order.traffic_index >= 3.0:
        reasons.append("traffic is very high")
        improvements.append("reduce traffic impact or add delivery buffer")
    elif order.traffic_index >= 1.5:
        reasons.append("traffic is moderately high")
        improvements.append("monitor traffic and keep some delivery buffer")

    if order.system_latency_ms >= 400:
        reasons.append("system latency is very high")
        improvements.append("reduce system latency")
    elif order.system_latency_ms >= 150:
        reasons.append("system latency is elevated")
        improvements.append("stabilize dispatch system latency")

    if order.promised_mins <= 25:
        reasons.append("promised time is very tight")
        improvements.append("increase promised time")
    elif order.promised_mins <= 35:
        reasons.append("promised time is moderately tight")
        improvements.append("slightly relax promised time")

    if order.priority == "HIGH":
        reasons.append("high priority adds operational pressure")
    elif order.priority == "MEDIUM":
        reasons.append("medium priority adds moderate operational pressure")

    if not reasons:
        reasons.append("inputs look operationally stable overall")

    if not improvements:
        improvements.append("continue normal monitoring")

    return reasons, list(dict.fromkeys(improvements))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(order: OrderFeatures):
    df = pd.DataFrame([order.model_dump()])
    success_prob = float(model.predict_proba(df)[0][1])
    risk_prob = 1 - success_prob

    if risk_prob >= 0.80:
        risk_category = "HIGH"
        conclusion = "This order is likely to MISS the SLA."
    elif risk_prob >= 0.40:
        risk_category = "MEDIUM"
        conclusion = "This order has moderate SLA risk."
    else:
        risk_category = "LOW"
        conclusion = "This order is likely to MEET the SLA."

    reasons, improvements = build_reasoning(order)

    return {
        "input": order.model_dump(),
        "probability_sla_met": round(success_prob, 3),
        "probability_sla_fail": round(risk_prob, 3),
        "risk_category": risk_category,
        "conclusion": conclusion,
        "reasoning": reasons,
        "improvements": improvements
    }