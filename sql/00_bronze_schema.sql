CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.orders_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL,
  order_id TEXT NOT NULL,
  region TEXT NOT NULL,
  promised_mins INT NOT NULL,
  priority TEXT NOT NULL,
  base_cost NUMERIC(10,2) NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze.ops_signals (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL,
  region TEXT NOT NULL,
  drivers_available INT NOT NULL,
  traffic_index NUMERIC(5,2) NOT NULL,
  system_latency_ms INT NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze.interventions_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL,
  order_id TEXT NOT NULL,
  action TEXT NOT NULL,
  extra_cost NUMERIC(10,2) NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze.outcomes_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL,
  order_id TEXT NOT NULL,
  actual_delivery_mins INT NOT NULL,
  sla_met BOOLEAN NOT NULL,
  payload JSONB NOT NULL
);