CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.fact_campaign_spend;
DROP TABLE IF EXISTS staging.fact_web_sessions;
DROP TABLE IF EXISTS staging.fact_sales;
DROP TABLE IF EXISTS staging.dim_campaign;
DROP TABLE IF EXISTS staging.dim_channel;
DROP TABLE IF EXISTS staging.dim_location;
DROP TABLE IF EXISTS staging.dim_date;
DROP TABLE IF EXISTS staging.dim_product;
DROP TABLE IF EXISTS staging.dim_customer;

CREATE TABLE staging.dim_customer (
    customer_id text, country text, signup_date timestamp, last_observed_date timestamp,
    source_system text, is_simulated boolean, simulation_version text
);

CREATE TABLE staging.dim_product (
    product_id text, product_name text, median_unit_price numeric, category text,
    cost_ratio numeric, standard_cost numeric, source_system text,
    is_simulated_category boolean, is_simulated_cost boolean, simulation_version text
);

CREATE TABLE staging.dim_date (
    date_key integer, full_date date, year integer, quarter text, month_number integer,
    month_name text, month_start date, week_number integer, day_of_week_number integer,
    day_name text, is_weekend boolean
);

CREATE TABLE staging.dim_location (
    location_id text, location_name text, city text, region text, country text,
    store_format text, location_type text, is_simulated boolean,
    source_system text, simulation_version text
);

CREATE TABLE staging.dim_channel (
    channel_id text, channel_name text, channel_type text, is_simulated boolean,
    source_system text, simulation_version text
);

CREATE TABLE staging.dim_campaign (
    campaign_id text, campaign_name text, channel_id text, start_date date, end_date date,
    objective text, source_system text, is_simulated boolean, simulation_version text
);

CREATE TABLE staging.fact_sales (
    sales_line_id text, order_id text, transaction_timestamp timestamp, date_key integer,
    customer_id text, product_id text, location_id text, channel_id text, campaign_id text,
    quantity integer, unit_price numeric, discount_rate numeric, net_revenue numeric,
    cogs numeric, fulfilment_cost numeric, is_return boolean, source_system text,
    source_record_id text, is_simulated boolean, simulation_version text
);

CREATE TABLE staging.fact_web_sessions (
    session_id text, session_timestamp timestamp, date_key integer, customer_id text,
    location_id text, channel_id text, campaign_id text, device_type text,
    page_views integer, product_views integer, add_to_cart boolean,
    checkout_started boolean, converted boolean, attributed_order_id text,
    source_system text, source_record_id text, is_simulated boolean, simulation_version text
);

CREATE TABLE staging.fact_campaign_spend (
    spend_id text, date_key integer, campaign_id text, channel_id text, location_id text,
    impressions bigint, clicks bigint, spend numeric, source_system text,
    source_record_id text, is_simulated boolean, simulation_version text
);
