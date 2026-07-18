# Methods and Run Log - Omnichannel Retail Performance Command Centre

| Date | Activity / run | Inputs | Method / tool | Key assumptions | Outputs created | Status |
|---|---|---|---|---|---|---|
| 2026-07-18 | Raw workbook acquisition | UCI download | HTTPS download; SHA-256 | Official archive is the source package | Raw ZIP and XLSX | complete |
| 2026-07-18 | Raw profile | `Online Retail.xlsx` | pandas/openpyxl | Raw file read without modification | Profile in `00_admin/brief.md` | complete |
| 2026-07-18 | Deterministic data build | SRC-001 | pandas/numpy; seed `20260718` | Exact duplicates removed; invalid prices/zero quantities quarantined; returns retained; generated fields labelled | Nine processed CSVs, quarantine CSV, five metric tables | complete - validation passed |
| 2026-07-18 | Local integrity validation | Processed CSVs | Python assertions and reconciliation | £0.01 arithmetic tolerance; attribution lag 0-6 days | `outputs/logs/validation-results*.json` | complete - 19 of 19 checks passed |
| 2026-07-18 | PostgreSQL implementation | Nine processed CSVs | PostgreSQL 18.4; pgAdmin; server-side CSV COPY; idempotent DDL/views | Dedicated `omnichannel_retail` database; local server can read immutable project inputs | `raw`, `staging`, and `analytics` schemas; six dimensions, three facts, five analytical views | complete |
| 2026-07-18 | PostgreSQL validation and reconciliation | PostgreSQL analytics schema; independent CSV reference values | Seven SQL integrity checks plus six metric/scenario comparisons | Currency tolerance £0.01; rate tolerance 0.1 percentage points | `outputs/logs/postgres-reconciliation.csv`; `analytics.v_validation_results` | complete - all checks passed |
| 2026-07-18 | Power BI implementation | PostgreSQL analytical schema | Power BI Import mode, TMDL, DAX query view, PDF export | 14 imported objects; 15 relationships; 38 measures; complete-month retention excludes partial December | Final PBIX, four-page PDF, `outputs/logs/powerbi-reconciliation.csv` | complete - six scenarios matched exactly |
| 2026-07-18 | Decision memo production | Validated local reference outputs | Markdown source, docx-js, LibreOffice conversion, DOCX validation, rendered PDF inspection | Exactly three findings and three actions; A4 two-page limit | Review DOCX/PDF | complete - QA passed |
| 2026-07-18 | Dashboard design prototype | Validated local reference outputs | Programmatic four-page 16:9 PDF; rendered-page inspection | Review aid only; not a Power BI export | Review PDF | complete - review only |
| 2026-07-18 | Analytical-depth and visual refinement | Validated facts, metric tables, and final PBIX | Provenance-isolated repeat analysis, one-store-month peer comparison, decision-table generation, corrected DAX, and rendered-page inspection | Combined-model repeat rate is not decision evidence; store peer variance must be computed at store-month grain | Eight decision tables, `depth-review-metrics.json`, refined PBIX/PDF, revised memo evidence | complete - decision metrics and all four pages inspected |

## Cleaning rules

1. Preserve the raw ZIP and XLSX unchanged.
2. Remove exact duplicate rows from the analytical copy; record the count.
3. Fill missing descriptions as `Unknown product` but retain the missingness count.
4. Retain cancellation-coded and negative-quantity lines as signed returns.
5. Quarantine rows with non-positive unit prices or zero quantity.
6. Retain anonymous revenue but exclude blank customer IDs from customer metrics.
7. Treat product cost, category, store, session, campaign, and attribution fields as simulated.

## Metric boundary

The local CSV metric tables are independently calculated reference outputs. PostgreSQL matched them before Power BI approval. DAX query view then matched six approved PostgreSQL scenarios exactly: overall net revenue, overall gross margin, May 2011 revenue, Manchester store revenue, Online channel revenue, and average retention for January-November 2011. Rounded cards were not used as reconciliation evidence.

The refinement added a provenance-clean public-core repeat rate, corrected store peer variance to one store-month grain, and generated decision-ready segment, store, category, channel, funnel, monthly, and exception outputs. The corrected `02_analysis/sql/02_views.sql` is authoritative for the next database rerun. The already-loaded local PostgreSQL view was not refreshed during this refinement because no saved database password was available; the final Power BI visuals use the imported fact model and corrected DAX measures.
