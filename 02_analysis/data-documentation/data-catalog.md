# Data Catalog

| Dataset | Grain | Provenance | Primary use |
|---|---|---|---|
| `dim_customer.csv` | One identified customer | Public UCI fields | Customer filtering, retention, RFM, observed CLV |
| `dim_product.csv` | One stock code | Public description/price plus simulated category/cost | Product and margin analysis |
| `dim_date.csv` | One calendar date | Derived | Time intelligence |
| `dim_location.csv` | One country or simulated physical store | Mixed, labelled | Online-market and store filtering |
| `dim_channel.csv` | One sales or marketing channel | Derived/simulated | Sales-channel and acquisition-channel filtering |
| `dim_campaign.csv` | One simulated campaign | Simulated | Campaign efficiency |
| `fact_sales.csv` | One invoice line | Public online lines plus simulated store lines | Revenue, margin, orders, returns, customer value |
| `fact_web_sessions.csv` | One simulated session | Simulated | Funnel and attribution analysis |
| `fact_campaign_spend.csv` | One campaign-date record | Simulated | Spend, CTR, CAC, ROAS, ROI |
| `quarantine_source_rows.csv` | One unusable public row | Public UCI | Audit only; excluded from facts |

All mixed tables contain `source_system`, `source_record_id`, `is_simulated`, and `simulation_version` where applicable.
