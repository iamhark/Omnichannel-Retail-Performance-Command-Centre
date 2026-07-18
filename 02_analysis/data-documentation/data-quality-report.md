# Data Quality Report

**Run date:** 2026-07-18  
**Status:** Passed for local CSV reference analysis, PostgreSQL execution, and Power BI reconciliation.

## Raw source inventory

| Check | Result | Treatment |
|---|---:|---|
| Raw rows | 541,909 | Preserved unchanged |
| Raw columns | 8 | All expected fields present |
| Exact duplicate rows | 5,268 | Removed from analytical copy; raw file retained |
| Missing customer IDs | 135,080 | Anonymous sales retained; excluded from customer metrics |
| Missing descriptions | 1,454 | Filled as `Unknown product`; count retained |
| Cancellation-coded lines | 9,288 | Retained as signed returns where price is positive |
| Negative-quantity lines | 10,624 | Retained as signed returns where price is positive |
| Non-positive-price lines | 2,517 | Quarantined after deduplication; 2,512 unique rows excluded |

The UCI repository metadata reports no missing values, but the downloaded workbook contains 135,080 blank customer IDs and 1,454 blank descriptions. This project uses the workbook profile as the source of truth for missingness.

## Processed outputs

| Output | Rows | Status |
|---|---:|---|
| Public sales fact | 534,129 | passed |
| Simulated physical-store sales | 150,000 | passed |
| Combined sales fact | 684,129 | passed |
| Simulated web sessions | 300,000 | passed |
| Simulated campaign-spend records | 1,122 | passed |

## Integrity tests

- Sales, session, and spend identifiers are unique.
- Sales product, location, channel, and campaign natural keys resolve.
- Required provenance fields contain no nulls.
- Every simulated sales row carries `omnichannel-sim-v1`.
- Revenue arithmetic maximum absolute error is `1.46e-11`, below the £0.01 tolerance.
- All 9,892 attributed conversions reference existing orders with a zero-to-six-day lag.
- Retention rates remain between zero and one.
- RFM excludes anonymous customer rows.
- Campaign ROI recomputes from attributed gross margin and spend without discrepancy.

Evidence: `02_analysis/outputs/logs/validation-results.json` and `validation-results-extended.json`.

## Remaining risks

- Product categories, costs, fulfilment costs, physical stores, web sessions, campaigns, and attribution are simulated.
- The public source is historical and online-only.
- December 2011 covers only nine days; it is not a complete-month comparison.
- PostgreSQL DDL, constraints, views, and reconciliation checks executed successfully in PostgreSQL 18.4.
- Power BI imported the approved PostgreSQL model. Six DAX scenarios matched PostgreSQL exactly; the four-page export passed text and rendered-page inspection.
