-- Local pgAdmin execution helper for this workstation.
-- PostgreSQL server-side COPY requires absolute paths. Update the base path
-- when running the project from a different location.

TRUNCATE TABLE staging.dim_customer;
COPY staging.dim_customer FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_customer.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.dim_product;
COPY staging.dim_product FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_product.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.dim_date;
COPY staging.dim_date FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_date.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.dim_location;
COPY staging.dim_location FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_location.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.dim_channel;
COPY staging.dim_channel FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_channel.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.dim_campaign;
COPY staging.dim_campaign FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/dim_campaign.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.fact_sales;
COPY staging.fact_sales FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/fact_sales.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.fact_web_sessions;
COPY staging.fact_web_sessions FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/fact_web_sessions.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

TRUNCATE TABLE staging.fact_campaign_spend;
COPY staging.fact_campaign_spend FROM 'C:/Users/harki/Desktop/education-research-workflow/10_projects/2026-07-omnichannel-retail-performance-command-centre/02_analysis/data/processed/fact_campaign_spend.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count FROM staging.dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM staging.dim_product
UNION ALL SELECT 'dim_date', COUNT(*) FROM staging.dim_date
UNION ALL SELECT 'dim_location', COUNT(*) FROM staging.dim_location
UNION ALL SELECT 'dim_channel', COUNT(*) FROM staging.dim_channel
UNION ALL SELECT 'dim_campaign', COUNT(*) FROM staging.dim_campaign
UNION ALL SELECT 'fact_sales', COUNT(*) FROM staging.fact_sales
UNION ALL SELECT 'fact_web_sessions', COUNT(*) FROM staging.fact_web_sessions
UNION ALL SELECT 'fact_campaign_spend', COUNT(*) FROM staging.fact_campaign_spend
ORDER BY table_name;
