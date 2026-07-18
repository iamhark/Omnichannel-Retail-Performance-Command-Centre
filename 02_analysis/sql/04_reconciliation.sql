-- PostgreSQL-to-reference reconciliation.
-- Reference values were independently computed from the processed CSV files.

WITH calculated AS (
    SELECT 'overall'::text AS scope, 'net_revenue'::text AS metric,
           SUM(net_revenue)::numeric AS postgres_value,
           13275371.3875::numeric AS reference_value
    FROM analytics.fact_sales

    UNION ALL
    SELECT 'overall', 'gross_margin',
           SUM(net_revenue - cogs), 6213555.4502::numeric
    FROM analytics.fact_sales

    UNION ALL
    SELECT '2011-05', 'net_revenue',
           SUM(net_revenue), 1196818.6590::numeric
    FROM analytics.fact_sales
    WHERE transaction_timestamp >= TIMESTAMP '2011-05-01'
      AND transaction_timestamp < TIMESTAMP '2011-06-01'

    UNION ALL
    SELECT 'sales_channel=SALES_ONLINE', 'net_revenue',
           SUM(f.net_revenue), 9748131.0740::numeric
    FROM analytics.fact_sales f
    JOIN analytics.dim_channel c USING (channel_key)
    WHERE c.channel_id = 'SALES_ONLINE'

    UNION ALL
    SELECT 'location=STORE-MANCHESTER-CITY', 'net_revenue',
           SUM(f.net_revenue), 620233.2390::numeric
    FROM analytics.fact_sales f
    JOIN analytics.dim_location l USING (location_key)
    WHERE l.location_id = 'STORE-MANCHESTER-CITY'

    UNION ALL
    SELECT '2011-01_to_2011-11', 'retention_rate',
           AVG(retention_rate), 0.6574811813::numeric
    FROM analytics.v_customer_retention
    WHERE month_start >= DATE '2011-01-01'
      AND month_start < DATE '2011-12-01'
)
SELECT scope, metric,
       ROUND(postgres_value, 10) AS postgres_value,
       reference_value,
       ROUND(postgres_value - reference_value, 10) AS variance,
       CASE
           WHEN metric = 'retention_rate'
               THEN CASE WHEN ABS(postgres_value - reference_value) <= 0.001 THEN 'pass' ELSE 'fail' END
           ELSE CASE WHEN ABS(postgres_value - reference_value) <= 0.01 THEN 'pass' ELSE 'fail' END
       END AS status
FROM calculated
ORDER BY scope, metric;
