CREATE OR REPLACE VIEW analytics.v_validation_results AS
SELECT 'fact_sales_primary_key' AS test_name,
       CASE WHEN COUNT(*) = COUNT(DISTINCT sales_line_id) THEN 'pass' ELSE 'fail' END AS status,
       COUNT(*)::text AS actual
FROM analytics.fact_sales
UNION ALL
SELECT 'fact_web_sessions_primary_key',
       CASE WHEN COUNT(*) = COUNT(DISTINCT session_id) THEN 'pass' ELSE 'fail' END,
       COUNT(*)::text
FROM analytics.fact_web_sessions
UNION ALL
SELECT 'fact_campaign_spend_primary_key',
       CASE WHEN COUNT(*) = COUNT(DISTINCT spend_id) THEN 'pass' ELSE 'fail' END,
       COUNT(*)::text
FROM analytics.fact_campaign_spend
UNION ALL
SELECT 'sales_provenance_complete',
       CASE WHEN COUNT(*) FILTER (WHERE source_system IS NULL OR source_record_id IS NULL OR is_simulated IS NULL) = 0 THEN 'pass' ELSE 'fail' END,
       COUNT(*) FILTER (WHERE source_system IS NULL OR source_record_id IS NULL OR is_simulated IS NULL)::text
FROM analytics.fact_sales
UNION ALL
SELECT 'simulated_version_complete',
       CASE WHEN COUNT(*) FILTER (WHERE is_simulated AND simulation_version IS NULL) = 0 THEN 'pass' ELSE 'fail' END,
       COUNT(*) FILTER (WHERE is_simulated AND simulation_version IS NULL)::text
FROM analytics.fact_sales
UNION ALL
SELECT 'revenue_arithmetic',
       CASE WHEN MAX(ABS(net_revenue - quantity * unit_price * (1 - discount_rate))) <= 0.01 THEN 'pass' ELSE 'fail' END,
       MAX(ABS(net_revenue - quantity * unit_price * (1 - discount_rate)))::text
FROM analytics.fact_sales
UNION ALL
SELECT 'anonymous_excluded_from_rfm',
       CASE WHEN COUNT(*) FILTER (WHERE customer_key IS NULL) = 0 THEN 'pass' ELSE 'fail' END,
       COUNT(*) FILTER (WHERE customer_key IS NULL)::text
FROM analytics.v_customer_rfm;

SELECT * FROM analytics.v_validation_results ORDER BY test_name;
