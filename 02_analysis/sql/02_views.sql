CREATE OR REPLACE VIEW analytics.v_monthly_performance AS
WITH sales AS (
    SELECT d.month_start,
           SUM(f.net_revenue) AS net_revenue,
           SUM(f.cogs) AS cogs,
           SUM(f.net_revenue - f.cogs) AS gross_margin,
           SUM(f.fulfilment_cost) AS fulfilment_cost,
           COUNT(DISTINCT f.order_id) FILTER (WHERE NOT f.is_return AND f.net_revenue > 0) AS orders,
           COUNT(DISTINCT f.customer_key) FILTER (WHERE NOT f.is_return AND f.net_revenue > 0) AS active_customers
    FROM analytics.fact_sales f
    JOIN analytics.dim_date d USING (date_key)
    GROUP BY d.month_start
), spend AS (
    SELECT d.month_start, SUM(f.spend) AS campaign_spend
    FROM analytics.fact_campaign_spend f
    JOIN analytics.dim_date d USING (date_key)
    GROUP BY d.month_start
)
SELECT s.*, COALESCE(p.campaign_spend, 0) AS campaign_spend,
       s.gross_margin - s.fulfilment_cost - COALESCE(p.campaign_spend, 0) AS contribution_margin,
       s.net_revenue / NULLIF(s.orders, 0) AS average_order_value,
       s.net_revenue / NULLIF(LAG(s.net_revenue) OVER (ORDER BY s.month_start), 0) - 1 AS revenue_mom_pct
FROM sales s
LEFT JOIN spend p USING (month_start);

CREATE OR REPLACE VIEW analytics.v_customer_retention AS
WITH active AS (
    SELECT DISTINCT d.month_start, f.customer_key
    FROM analytics.fact_sales f
    JOIN analytics.dim_date d USING (date_key)
    WHERE f.customer_key IS NOT NULL AND NOT f.is_return AND f.net_revenue > 0
), months AS (
    SELECT month_start, COUNT(*) AS active_customers FROM active GROUP BY month_start
), retained AS (
    SELECT current.month_start, COUNT(*) AS retained_customers
    FROM active current
    JOIN active prior ON prior.customer_key = current.customer_key
                     AND prior.month_start = current.month_start - INTERVAL '1 month'
    GROUP BY current.month_start
)
SELECT m.month_start, m.active_customers,
       LAG(m.active_customers) OVER (ORDER BY m.month_start) AS prior_month_customers,
       COALESCE(r.retained_customers, 0) AS retained_customers,
       COALESCE(r.retained_customers, 0)::numeric /
           NULLIF(LAG(m.active_customers) OVER (ORDER BY m.month_start), 0) AS retention_rate
FROM months m LEFT JOIN retained r USING (month_start);

CREATE OR REPLACE VIEW analytics.v_customer_rfm AS
WITH base AS (
    SELECT f.customer_key, MAX(f.transaction_timestamp)::date AS last_purchase,
           COUNT(DISTINCT f.order_id) AS frequency,
           SUM(f.net_revenue) AS monetary,
           SUM(f.net_revenue - f.cogs - f.fulfilment_cost) AS observed_historical_clv
    FROM analytics.fact_sales f
    WHERE f.customer_key IS NOT NULL AND NOT f.is_return AND f.net_revenue > 0
    GROUP BY f.customer_key
), scored AS (
    SELECT b.*,
           (SELECT MAX(full_date) + 1 FROM analytics.dim_date) - b.last_purchase AS recency_days,
           6 - NTILE(5) OVER (ORDER BY ((SELECT MAX(full_date) + 1 FROM analytics.dim_date) - b.last_purchase)) AS r_score,
           NTILE(5) OVER (ORDER BY b.frequency) AS f_score,
           NTILE(5) OVER (ORDER BY b.monetary) AS m_score
    FROM base b
)
SELECT s.*, c.customer_id, c.country,
       CASE
           WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
           WHEN r_score >= 3 AND f_score >= 4 THEN 'Loyal'
           WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists'
           WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
           WHEN r_score = 1 AND f_score <= 2 THEN 'Lost'
           ELSE 'Other'
       END AS rfm_segment
FROM scored s JOIN analytics.dim_customer c USING (customer_key);

CREATE OR REPLACE VIEW analytics.v_product_store_performance AS
WITH store_month AS (
    SELECT d.month_start, l.location_key, l.location_id, l.location_name,
           l.store_format,
           SUM(f.net_revenue) AS net_revenue,
           SUM(f.net_revenue - f.cogs) AS gross_margin,
           COUNT(DISTINCT f.order_id) AS orders,
           COUNT(*) FILTER (WHERE f.is_return) AS return_lines
    FROM analytics.fact_sales f
    JOIN analytics.dim_date d USING (date_key)
    JOIN analytics.dim_location l USING (location_key)
    WHERE l.location_type = 'Physical store'
    GROUP BY d.month_start, l.location_key, l.location_id, l.location_name, l.store_format
), peer AS (
    SELECT *, AVG(net_revenue) OVER (PARTITION BY month_start, store_format) AS peer_average_revenue
    FROM store_month
)
SELECT *, net_revenue - peer_average_revenue AS store_variance,
       (net_revenue - peer_average_revenue) / NULLIF(peer_average_revenue, 0) AS store_variance_pct
FROM peer;

CREATE OR REPLACE VIEW analytics.v_campaign_efficiency AS
WITH spend AS (
    SELECT campaign_key, SUM(impressions) AS impressions, SUM(clicks) AS clicks, SUM(spend) AS spend
    FROM analytics.fact_campaign_spend GROUP BY campaign_key
), sessions AS (
    SELECT campaign_key, COUNT(*) AS sessions, COUNT(*) FILTER (WHERE converted) AS conversions
    FROM analytics.fact_web_sessions WHERE campaign_key IS NOT NULL GROUP BY campaign_key
), attributed AS (
    SELECT campaign_key, SUM(net_revenue) AS attributed_revenue,
           SUM(net_revenue - cogs) AS attributed_gross_margin,
           COUNT(DISTINCT order_id) AS attributed_orders
    FROM analytics.fact_sales WHERE campaign_key IS NOT NULL GROUP BY campaign_key
)
SELECT c.campaign_key, c.campaign_id, c.campaign_name, c.channel_key,
       s.impressions, s.clicks, s.spend, w.sessions, w.conversions,
       COALESCE(a.attributed_revenue, 0) AS attributed_revenue,
       COALESCE(a.attributed_gross_margin, 0) AS attributed_gross_margin,
       COALESCE(a.attributed_orders, 0) AS attributed_orders,
       s.clicks::numeric / NULLIF(s.impressions, 0) AS ctr,
       w.conversions::numeric / NULLIF(w.sessions, 0) AS conversion_rate,
       COALESCE(a.attributed_revenue, 0) / NULLIF(s.spend, 0) AS roas,
       (COALESCE(a.attributed_gross_margin, 0) - s.spend) / NULLIF(s.spend, 0) AS roi,
       s.spend / NULLIF(w.conversions, 0) AS cac
FROM analytics.dim_campaign c
JOIN spend s USING (campaign_key)
LEFT JOIN sessions w USING (campaign_key)
LEFT JOIN attributed a USING (campaign_key);
