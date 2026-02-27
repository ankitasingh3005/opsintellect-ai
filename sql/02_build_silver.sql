INSERT INTO silver.order_features
SELECT
  o.order_id,
  o.event_time AS order_time,
  o.region,
  o.promised_mins,
  o.priority,
  o.base_cost,

  s.drivers_available,
  s.traffic_index,
  s.system_latency_ms,

  COALESCE(i.interventions_count, 0) AS interventions_count,
  COALESCE(i.total_extra_cost, 0) AS total_extra_cost,

  out.actual_delivery_mins,
  out.sla_met
FROM bronze.orders_events o

-- latest ops signal at or before order time (same region)
LEFT JOIN LATERAL (
  SELECT *
  FROM bronze.ops_signals s
  WHERE s.region = o.region
    AND s.event_time <= o.event_time
  ORDER BY s.event_time DESC
  LIMIT 1
) s ON true

-- intervention summary per order
LEFT JOIN (
  SELECT
    order_id,
    COUNT(*) AS interventions_count,
    SUM(extra_cost) AS total_extra_cost
  FROM bronze.interventions_events
  GROUP BY order_id
) i ON o.order_id = i.order_id

-- final outcome
LEFT JOIN bronze.outcomes_events out
  ON o.order_id = out.order_id;