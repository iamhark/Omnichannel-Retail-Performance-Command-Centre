DROP SCHEMA IF EXISTS analytics CASCADE;
CREATE SCHEMA analytics;

CREATE TABLE analytics.dim_date AS
SELECT date_key, full_date, year, quarter, month_number, month_name, month_start,
       week_number, day_of_week_number, day_name, is_weekend
FROM staging.dim_date;
ALTER TABLE analytics.dim_date ADD PRIMARY KEY (date_key);

CREATE TABLE analytics.dim_customer AS
SELECT row_number() OVER (ORDER BY customer_id)::integer AS customer_key, *
FROM staging.dim_customer;
ALTER TABLE analytics.dim_customer ADD PRIMARY KEY (customer_key);
ALTER TABLE analytics.dim_customer ADD UNIQUE (customer_id);

CREATE TABLE analytics.dim_product AS
SELECT row_number() OVER (ORDER BY product_id)::integer AS product_key, *
FROM staging.dim_product;
ALTER TABLE analytics.dim_product ADD PRIMARY KEY (product_key);
ALTER TABLE analytics.dim_product ADD UNIQUE (product_id);

CREATE TABLE analytics.dim_location AS
SELECT row_number() OVER (ORDER BY location_id)::integer AS location_key, *
FROM staging.dim_location;
ALTER TABLE analytics.dim_location ADD PRIMARY KEY (location_key);
ALTER TABLE analytics.dim_location ADD UNIQUE (location_id);

CREATE TABLE analytics.dim_channel AS
SELECT row_number() OVER (ORDER BY channel_id)::integer AS channel_key, *
FROM staging.dim_channel;
ALTER TABLE analytics.dim_channel ADD PRIMARY KEY (channel_key);
ALTER TABLE analytics.dim_channel ADD UNIQUE (channel_id);

CREATE TABLE analytics.dim_campaign AS
SELECT row_number() OVER (ORDER BY campaign_id)::integer AS campaign_key,
       c.*, ch.channel_key
FROM staging.dim_campaign c
JOIN analytics.dim_channel ch USING (channel_id);
ALTER TABLE analytics.dim_campaign ADD PRIMARY KEY (campaign_key);
ALTER TABLE analytics.dim_campaign ADD UNIQUE (campaign_id);

CREATE TABLE analytics.fact_sales AS
SELECT s.sales_line_id, s.order_id, s.transaction_timestamp, s.date_key,
       c.customer_key, p.product_key, l.location_key, ch.channel_key, cp.campaign_key,
       s.quantity, s.unit_price, s.discount_rate, s.net_revenue, s.cogs,
       s.fulfilment_cost, s.is_return, s.source_system, s.source_record_id,
       s.is_simulated, s.simulation_version
FROM staging.fact_sales s
JOIN analytics.dim_date d ON d.date_key = s.date_key
LEFT JOIN analytics.dim_customer c ON c.customer_id = s.customer_id
JOIN analytics.dim_product p ON p.product_id = s.product_id
JOIN analytics.dim_location l ON l.location_id = s.location_id
JOIN analytics.dim_channel ch ON ch.channel_id = s.channel_id
LEFT JOIN analytics.dim_campaign cp ON cp.campaign_id = s.campaign_id;
ALTER TABLE analytics.fact_sales ADD PRIMARY KEY (sales_line_id);
CREATE INDEX fact_sales_date_idx ON analytics.fact_sales (date_key);
CREATE INDEX fact_sales_customer_idx ON analytics.fact_sales (customer_key);
CREATE INDEX fact_sales_product_idx ON analytics.fact_sales (product_key);
CREATE INDEX fact_sales_location_idx ON analytics.fact_sales (location_key);
CREATE INDEX fact_sales_channel_idx ON analytics.fact_sales (channel_key);
CREATE INDEX fact_sales_campaign_idx ON analytics.fact_sales (campaign_key);

CREATE TABLE analytics.fact_web_sessions AS
SELECT s.session_id, s.session_timestamp, s.date_key, c.customer_key,
       l.location_key, ch.channel_key, cp.campaign_key, s.device_type,
       s.page_views, s.product_views, s.add_to_cart, s.checkout_started,
       s.converted, s.attributed_order_id, s.source_system, s.source_record_id,
       s.is_simulated, s.simulation_version
FROM staging.fact_web_sessions s
JOIN analytics.dim_date d ON d.date_key = s.date_key
LEFT JOIN analytics.dim_customer c ON c.customer_id = s.customer_id
JOIN analytics.dim_location l ON l.location_id = s.location_id
JOIN analytics.dim_channel ch ON ch.channel_id = s.channel_id
LEFT JOIN analytics.dim_campaign cp ON cp.campaign_id = s.campaign_id;
ALTER TABLE analytics.fact_web_sessions ADD PRIMARY KEY (session_id);
CREATE INDEX fact_web_sessions_date_idx ON analytics.fact_web_sessions (date_key);
CREATE INDEX fact_web_sessions_customer_idx ON analytics.fact_web_sessions (customer_key);
CREATE INDEX fact_web_sessions_campaign_idx ON analytics.fact_web_sessions (campaign_key);

CREATE TABLE analytics.fact_campaign_spend AS
SELECT s.spend_id, s.date_key, cp.campaign_key, ch.channel_key, l.location_key,
       s.impressions, s.clicks, s.spend, s.source_system, s.source_record_id,
       s.is_simulated, s.simulation_version
FROM staging.fact_campaign_spend s
JOIN analytics.dim_date d ON d.date_key = s.date_key
JOIN analytics.dim_campaign cp ON cp.campaign_id = s.campaign_id
JOIN analytics.dim_channel ch ON ch.channel_id = s.channel_id
JOIN analytics.dim_location l ON l.location_id = s.location_id;
ALTER TABLE analytics.fact_campaign_spend ADD PRIMARY KEY (spend_id);
CREATE INDEX fact_campaign_spend_date_idx ON analytics.fact_campaign_spend (date_key);
CREATE INDEX fact_campaign_spend_campaign_idx ON analytics.fact_campaign_spend (campaign_key);

ALTER TABLE analytics.fact_sales
    ADD FOREIGN KEY (date_key) REFERENCES analytics.dim_date(date_key),
    ADD FOREIGN KEY (customer_key) REFERENCES analytics.dim_customer(customer_key),
    ADD FOREIGN KEY (product_key) REFERENCES analytics.dim_product(product_key),
    ADD FOREIGN KEY (location_key) REFERENCES analytics.dim_location(location_key),
    ADD FOREIGN KEY (channel_key) REFERENCES analytics.dim_channel(channel_key),
    ADD FOREIGN KEY (campaign_key) REFERENCES analytics.dim_campaign(campaign_key);

ALTER TABLE analytics.fact_web_sessions
    ADD FOREIGN KEY (date_key) REFERENCES analytics.dim_date(date_key),
    ADD FOREIGN KEY (customer_key) REFERENCES analytics.dim_customer(customer_key),
    ADD FOREIGN KEY (location_key) REFERENCES analytics.dim_location(location_key),
    ADD FOREIGN KEY (channel_key) REFERENCES analytics.dim_channel(channel_key),
    ADD FOREIGN KEY (campaign_key) REFERENCES analytics.dim_campaign(campaign_key);

ALTER TABLE analytics.fact_campaign_spend
    ADD FOREIGN KEY (date_key) REFERENCES analytics.dim_date(date_key),
    ADD FOREIGN KEY (campaign_key) REFERENCES analytics.dim_campaign(campaign_key),
    ADD FOREIGN KEY (channel_key) REFERENCES analytics.dim_channel(channel_key),
    ADD FOREIGN KEY (location_key) REFERENCES analytics.dim_location(location_key);
