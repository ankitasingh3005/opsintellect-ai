import json
import random
import time
from datetime import datetime, timezone, timedelta
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

REGIONS = ["OH", "NJ", "TX", "CA"]
PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

def run_forever(rate_per_sec=1.0, seed=42):
    random.seed(seed)
    i = 0
    sleep_s = 1.0 / max(rate_per_sec, 0.001)

    print(f"✅ Producer started (~{rate_per_sec} orders/sec). Ctrl+C to stop.\n")

    while True:
        i += 1
        t = datetime.now(timezone.utc)
        order_id = f"O{100000000 + i}"

        region = random.choice(REGIONS)
        priority = random.choices(PRIORITIES, weights=[0.5, 0.3, 0.2])[0]
        promised = random.choice([25, 30, 35])
        base_cost = round(random.uniform(8, 25), 2)

        drivers = random.randint(3, 20)
        traffic = round(random.uniform(0.5, 2.0), 2)
        latency = random.randint(50, 350)

        # “true” risk logic (ML learns this later)
        risk = 0.0
        risk += 0.35 if traffic > 1.4 else 0.0
        risk += 0.25 if drivers < 7 else 0.0
        risk += 0.20 if latency > 250 else 0.0
        risk += 0.10 if priority == "HIGH" else 0.0
        risk = min(0.95, risk + random.uniform(0.0, 0.15))

        interventions = []
        if risk > 0.55:
            if random.random() < 0.7:
                interventions.append(("OVERTIME", round(random.uniform(3, 8), 2)))
            if random.random() < 0.5 and priority != "HIGH":
                interventions.append(("EXPEDITE_ROUTE", round(random.uniform(4, 10), 2)))
            if random.random() < 0.4:
                interventions.append(("CUSTOMER_DISCOUNT", round(random.uniform(1, 5), 2)))

        delay_noise = random.randint(-2, 6)
        help_mins = 0
        if any(a == "OVERTIME" for a, _ in interventions):
            help_mins += random.randint(1, 3)
        if any(a == "EXPEDITE_ROUTE" for a, _ in interventions):
            help_mins += random.randint(1, 4)

        actual = promised + int(risk * 12) + delay_noise - help_mins
        actual = max(10, actual)
        sla_met = actual <= promised

        # ----- EVENTS -----
        order_event = {
            "event_time": t.isoformat(),
            "order_id": order_id,
            "region": region,
            "promised_mins": promised,
            "priority": priority,
            "base_cost": base_cost
        }
        ops_event = {
            "event_time": t.isoformat(),
            "region": region,
            "drivers_available": drivers,
            "traffic_index": traffic,
            "system_latency_ms": latency
        }
        outcome_event = {
            "event_time": (t + timedelta(minutes=actual)).isoformat(),
            "order_id": order_id,
            "actual_delivery_mins": actual,
            "sla_met": sla_met
        }

        # Print what we're sending (every record)
        print(f"Produced order: {order_event}")
        print(f"Produced ops:   {ops_event}")

        producer.send("orders_events", order_event)
        producer.send("ops_signals", ops_event)

        for action, extra_cost in interventions:
            intervention_event = {
                "event_time": (t + timedelta(seconds=2)).isoformat(),
                "order_id": order_id,
                "action": action,
                "extra_cost": extra_cost
            }
            print(f"Produced intervention: {intervention_event}")
            producer.send("interventions_events", intervention_event)

        print(f"Produced outcome: {outcome_event}\n")
        producer.send("outcomes_events", outcome_event)

        producer.flush()
        time.sleep(sleep_s)

if __name__ == "__main__":
    run_forever(rate_per_sec=1.0)  # change speed here (ex: 2.0, 5.0)