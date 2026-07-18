# Decision Log - Omnichannel Retail Performance Command Centre

| Date | Decision | Reason | Consequence |
|---|---|---|---|
| 2026-07-18 | Use PostgreSQL as the primary warehouse | Local reproducibility and visible SQL evidence | Installation is a prerequisite; SQL scripts remain rerunnable and idempotent |
| 2026-07-18 | Use UCI Online Retail as the public analytical core | Accessible source, CC BY 4.0 licence, stable DOI, line-level transactions | The source is online-only and historical; offline and marketing facts require labelled simulation |
| 2026-07-18 | Generate deterministic extensions with seed `20260718` | Creates coherent omnichannel joins without concealing synthetic data | Combined findings are business-case evidence, not real company performance |
| 2026-07-18 | Retain returns but quarantine non-positive price and zero-quantity rows | Preserves net-revenue behavior without treating unusable prices as sales | Gross and net measures reconcile to the cleaned analytical copy, not raw row totals |
| 2026-07-18 | Remove exact duplicate rows from the analytical copy | The source lacks a line ID and contains 5,268 exact duplicates | The removal count is recorded and the raw workbook remains immutable |
| 2026-07-18 | Exclude anonymous customers from RFM, retention, repeat-rate, and CLV | Customer-level metrics require stable identity | Anonymous orders still contribute to revenue and product metrics |
| 2026-07-18 | Define CLV as observed historical contribution | The available period does not support defensible predictive lifetime modeling | All deliverables must use the full label `Observed Historical CLV` |
| 2026-07-18 | Use last non-direct session within seven days for attribution | Simple, auditable v1 rule | Attribution is simulated and must not be interpreted causally |
| 2026-07-18 | Treat MA-SET1 as reference-only | Its raw workbook lacks source provenance and its modules cannot form a coherent star schema | No legacy number may enter a final claim without recomputation |
