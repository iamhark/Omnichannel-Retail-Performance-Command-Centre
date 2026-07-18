# Analysis Plan

## Decision sequence

1. Establish whether revenue and contribution are improving by month and sales channel.
2. Identify customer segments that concentrate value or show elevated lapse risk.
3. Isolate product-category and same-format store performance gaps.
4. Compare campaign spend against attributed revenue, attributed gross margin, conversion, CAC, ROAS, and ROI.

## Required outputs

| Output | Source | Method | Decision supported |
|---|---|---|---|
| Monthly performance | `fact_sales`, `fact_campaign_spend` | SQL view and DAX | Executive trend and margin intervention |
| Customer retention | Identified positive orders | Consecutive calendar-month intersection | Retention monitoring |
| RFM and observed CLV | Identified positive orders | Quintile scoring and cumulative contribution | Segment treatment |
| Product/store performance | Simulated store sales | Same-format monthly peer comparison | Store and category action |
| Campaign efficiency | Simulated sessions/spend plus attributed public orders | Last non-direct within seven days | Budget reallocation |

## Interpretation controls

- Do not treat simulated channel, store, cost, or campaign patterns as real company observations.
- Do not interpret correlation or attribution as causal lift.
- Do not compare the partial December 2011 period with complete months without flagging the incomplete period.
- Keep public-only and combined business-case metrics distinguishable through provenance fields.
