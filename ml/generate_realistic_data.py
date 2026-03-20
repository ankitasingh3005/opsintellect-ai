import psycopg2
import random
import math
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost",
    database="opsintellect",
    user="ops",
    password="ops"
)
cursor = conn.cursor()

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def pick_priority(weight_low, weight_med, weight_high):
    return random.choices(
        ["LOW", "MEDIUM", "HIGH"],
        weights=[weight_low, weight_med, weight_high],
        k=1
    )[0]

rows_per_band = 2500
base_time = datetime.now() - timedelta(hours=2)
row_num = 0

for band in ["easy", "medium", "hard"]:
    for _ in range(rows_per_band):
        order_id = f"REAL_{row_num}"

        if band == "easy":
            drivers = random.randint(20, 50)
            traffic = round(random.uniform(0.1, 1.4), 2)
            latency = random.randint(20, 180)
            promised = random.randint(35, 60)
            priority = pick_priority(0.6, 0.3, 0.1)

        elif band == "medium":
            drivers = random.randint(8, 28)
            traffic = round(random.uniform(1.0, 2.6), 2)
            latency = random.randint(80, 320)
            promised = random.randint(25, 45)
            priority = pick_priority(0.25, 0.5, 0.25)

        else:
            drivers = random.randint(0, 4)
            traffic = round(random.uniform(3.5, 5.0), 2)
            latency = random.randint(450, 900)
            promised = random.randint(5, 18)
            priority = pick_priority(0.02, 0.18, 0.80)

        priority_weight = {"LOW": -0.10, "MEDIUM": 0.25, "HIGH": 0.90}[priority]

        stress = (
            traffic * 1.35
            + (22 / (drivers + 2))
            + (latency / 180)
            + ((42 - promised) / 6)
            + priority_weight
            + random.uniform(-0.15, 0.15)
        )

        p_fail = sigmoid(stress - 2.9)
        fail = random.random() < p_fail

        if fail:
            actual_delivery = promised + random.randint(3, 25)
        else:
            actual_delivery = max(1, promised - random.randint(0, 8))

        order_time = base_time + timedelta(seconds=row_num * 2)
        signal_time = order_time - timedelta(seconds=5)
        outcome_time = order_time + timedelta(minutes=1)

        cursor.execute(
            """
            INSERT INTO bronze.ops_signals
            (event_time, region, drivers_available, traffic_index, system_latency_ms, payload)
            VALUES (%s, 'OH', %s, %s, %s, '{}'::jsonb)
            """,
            (signal_time, drivers, traffic, latency)
        )

        cursor.execute(
            """
            INSERT INTO bronze.orders_events
            (event_time, order_id, region, promised_mins, priority, base_cost, payload)
            VALUES (%s, %s, 'OH', %s, %s, 20.0, '{}'::jsonb)
            """,
            (order_time, order_id, promised, priority)
        )

        cursor.execute(
            """
            INSERT INTO bronze.outcomes_events
            (event_time, order_id, actual_delivery_mins, sla_met, payload)
            VALUES (%s, %s, %s, %s, '{}'::jsonb)
            """,
            (outcome_time, order_id, actual_delivery, not fail)
        )

        row_num += 1

conn.commit()
cursor.close()
conn.close()

print("✅ New balanced Bronze data generated successfully.")