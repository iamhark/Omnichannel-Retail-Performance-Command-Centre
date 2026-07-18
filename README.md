# Project README - Omnichannel Retail Performance Command Centre

**Project code:** `omnichannel-retail-performance-command-centre`  
**Status:** complete - PostgreSQL, Power BI, memo, and technical package approved  
**Last updated:** 2026-07-18  
**Next action:** retain the final artifacts and rerun the documented pipeline only when the source or metric contract changes.

## Purpose

**Business question:** Which customer segments, product categories, channels, and store locations require action to improve revenue, retention, and operating performance?

**Audience and decision supported:** Retail executive committee allocating commercial, retention, store-operations, and marketing attention.

**Deliverables:**

- [x] Power BI command centre source (`.pbix`)
- [x] Four-page Power BI PDF export
- [x] Two-page executive decision memo in DOCX and PDF
- [x] PostgreSQL, DAX, model, validation, and reproducibility technical pack

## GitHub package scope

This repository publishes reproducible code, SQL, DAX, aggregate outputs, final deliverables, and governance records. It excludes the UCI raw workbook/ZIP, regenerable fact-level sales and web-session CSVs, local Python vendor files, temporary renders, and superseded review copies. Retrieve the immutable public source from `SRC-001` in `01_inputs/source-register.md`, then run the documented reproduction order to rebuild excluded data.

## Provenance boundary

The analytical core is the CC BY 4.0 UCI Online Retail dataset. Physical-store sales, product categories and costs, web sessions, campaigns, attribution, and campaign spend are deterministic simulated extensions created for a business-case exercise. Every mixed fact row carries provenance fields. The legacy MA-SET1 workbook, report, and deck are reference-only and are not evidence for this project.

## Current truth

- Scope: `00_admin/brief.md`
- Sources: `01_inputs/source-register.md`
- Methods and runs: `02_analysis/methods-and-run-log.md`
- Data quality: `02_analysis/data-documentation/data-quality-report.md`
- Evidence: `03_synthesis/evidence-register.md`
- Insights: `03_synthesis/insight-register.md`
- Final outputs: `04_deliverables/final/`

## Reproduction order

1. Install Python requirements from `02_analysis/environment/requirements.txt`.
2. Run `02_analysis/code/build_analytics_data.py`.
3. Install PostgreSQL and run `02_analysis/sql/00_create_staging.sql` from `psql`.
4. Run `02_analysis/code/load_postgres.py` with a local connection string.
5. Run `02_analysis/sql/run_after_load.sql` from `psql` to build views and execute SQL validation.
6. Connect Power BI Desktop to the `analytics` views using Import mode and follow `02_analysis/powerbi/model-spec.md`.
7. Reconcile SQL and DAX totals before approving final dashboard files.

## Completion check

- [x] PostgreSQL schema and views execute without error.
- [x] Local reference facts and PostgreSQL facts have zero tested key orphans and complete provenance.
- [x] Six SQL and DAX scenarios reconcile exactly; currency variance is £0.00 and the rate variance is 0.0 percentage points.
- [x] The two-page memo and four-page Power BI export pass structural and rendered-page QA.
- [x] Every substantive memo claim maps to an evidence or analysis output.
- [x] The delivery manifest names one authoritative final file for each required deliverable.
