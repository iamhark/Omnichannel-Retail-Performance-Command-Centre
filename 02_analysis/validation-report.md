# Validation Report

## Completed gates

| Gate | Evidence | Result |
|---|---|---|
| Raw checksum | `validation-results-extended.json` | pass |
| Deterministic row counts | `validation-results.json` | pass |
| Fact primary keys | Both validation JSON files | pass |
| Provenance completeness | Both validation JSON files | pass |
| Simulation labels | Both validation JSON files | pass |
| Revenue arithmetic | Both validation JSON files | pass |
| Natural-key coverage | Both validation JSON files | pass |
| Attribution window | `validation-results-extended.json` | pass |
| Retention bounds | `validation-results-extended.json` | pass |
| RFM identity boundary | `validation-results-extended.json` | pass |
| Campaign ROI formula | `validation-results-extended.json` | pass |
| Repeat-purchase provenance boundary | `depth-review-metrics.json`; Power BI diagnostic query | pass - public UCI core rate is 65.6%; combined-model 100% artifact is excluded from decision reporting |
| Store-peer comparison grain | `store_peer_summary.csv`; `product_store_performance.csv`; Power BI diagnostic query | pass - one store-month row before same-format peer comparison |

## Runtime and delivery gates

| Gate | Evidence | Result |
|---|---|---|
| PostgreSQL execution | PostgreSQL 18.4; `analytics.v_validation_results` | pass - schema, dimensions, facts, views, and all seven SQL checks executed |
| SQL-to-reference reconciliation | `02_analysis/outputs/logs/postgres-reconciliation.csv` | pass - six checks have zero variance |
| PBIX authoring | Final PBIX; Power BI Desktop 2.155.756.0 | pass - 14 imported objects, 15 relationships, 38 measures, and four named pages |
| DAX-to-SQL reconciliation | `02_analysis/outputs/logs/powerbi-reconciliation.csv` | pass - six checks match exactly; currency variance £0.00 and rate variance 0.0 percentage points |
| Refined DAX diagnostics | `depth-review-metrics.json`; Power BI diagnostic query | pass - public-core repeat 65.6%, Champions monetary share 46.1%, At Risk/Lost share 30.5%, latest complete-month revenue £1,689,485, and MoM 25.2% |
| Genuine Power BI PDF export | Final dashboard PDF and rendered PNG inspection | pass - exactly four pages, expected KPI text, provenance note on every page, no blank variance card, and no invalid channel ROI visual |

The authoritative PBIX and its four-page Power BI export are recorded in `04_deliverables/delivery-manifest.md`.

The corrected PostgreSQL view definition is staged in `02_analysis/sql/02_views.sql` for the next credentialed rerun. This refinement did not reapply that view to the local server; store-peer visuals were validated from the imported fact model using corrected DAX.
