CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.order_features (
  order_id TEXT PRIMARY KEY,

  -- Order info
  order_time TIMESTAMPTZ,
  region TEXT,
  promised_mins INT,
  priority TEXT,
  base_cost NUMERIC(10,2),

  -- Ops signals (latest before order)
  drivers_available INT,
  traffic_index NUMERIC(5,2),
  system_latency_ms INT,

  -- Interventions summary
  interventions_count INT,
  total_extra_cost NUMERIC(10,2),

  -- Outcome (label)
  actual_delivery_mins INT,
  sla_met BOOLEAN
);