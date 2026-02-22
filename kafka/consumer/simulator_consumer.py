import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def main():
    conn = psycopg2.connect(
        host="localhost",
        database="opsintellect",
        user="ops",
        password="ops",
    )
    conn.autocommit = True
    cur = conn.cursor()

    consumer = KafkaConsumer(
        "orders_events", "ops_signals", "interventions_events", "outcomes_events",
        bootstrap_servers="localhost:9092",
        group_id="realtime-multi-consumer",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    print("✅ Consumer started. Listening forever... Ctrl+C to stop.\n")

    for msg in consumer:
        topic = msg.topic
        event = msg.value

        print(f"Received [{topic}]: {event}")

        try:
            if topic == "orders_events":
                cur.execute("""
                    INSERT INTO bronze.orders_events
                    (event_time, order_id, region, promised_mins, priority, base_cost, payload)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    parse_ts(event["event_time"]),
                    event["order_id"],
                    event["region"],
                    int(event["promised_mins"]),
                    event["priority"],
                    float(event["base_cost"]),
                    json.dumps(event),
                ))

            elif topic == "ops_signals":
                cur.execute("""
                    INSERT INTO bronze.ops_signals
                    (event_time, region, drivers_available, traffic_index, system_latency_ms, payload)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    parse_ts(event["event_time"]),
                    event["region"],
                    int(event["drivers_available"]),
                    float(event["traffic_index"]),
                    int(event["system_latency_ms"]),
                    json.dumps(event),
                ))

            elif topic == "interventions_events":
                cur.execute("""
                    INSERT INTO bronze.interventions_events
                    (event_time, order_id, action, extra_cost, payload)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    parse_ts(event["event_time"]),
                    event["order_id"],
                    event["action"],
                    float(event["extra_cost"]),
                    json.dumps(event),
                ))

            elif topic == "outcomes_events":
                cur.execute("""
                    INSERT INTO bronze.outcomes_events
                    (event_time, order_id, actual_delivery_mins, sla_met, payload)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    parse_ts(event["event_time"]),
                    event["order_id"],
                    int(event["actual_delivery_mins"]),
                    bool(event["sla_met"]),
                    json.dumps(event),
                ))

            print("Inserted into Postgres!\n")

        except Exception as e:
            print(f"❌ Insert failed topic={topic}: {e}\n")

if __name__ == "__main__":
    main()