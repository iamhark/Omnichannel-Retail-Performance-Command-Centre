# Pre-delivery QA Report

**Date:** 2026-07-18  
**Scope:** PostgreSQL analytical model, Power BI source report and export, decision memo, and technical portfolio package.  
**Outcome:** all required runtime, analytical, evidence, and delivery gates passed.

## Input and evidence checks

- Current project inventory: 114 readable files plus two inaccessible vendored `defusedxml` directories that are irrelevant dependency remnants; 10 `.gitkeep` placeholders contain no analytical content.
- No malformed analytical file was found. UCI ZIP/workbook integrity and the Office, CSV, JSON, SQL, DAX, PBIX, PDF, PNG, and ZIP artifacts used for delivery are readable.
- The immutable UCI workbook checksum is recorded in the source register.
- Legacy MA-SET1 files remain reference-only and are not cited as analytical evidence.
- All material memo claims map to `CLM-002` through `CLM-008` and named computed tables.

## Analytical checks

- Extended Python validation: 19 of 19 checks passed.
- PostgreSQL validation: seven of seven SQL integrity checks passed.
- PostgreSQL-to-reference reconciliation: six of six scenarios passed with zero variance.
- Power BI-to-PostgreSQL reconciliation: six of six scenarios passed exactly. Net revenue, gross margin, May 2011 revenue, Manchester revenue, Online revenue, and January-November retention match the approved PostgreSQL outputs.
- Fact primary keys are unique; provenance is complete; simulated rows are labelled; natural-key fact-to-dimension orphans are zero.
- Anonymous customers are excluded from customer metrics; attribution checks cover 9,892 attributed orders with a zero-to-six-day lag.
- The public-core repeat-rate boundary replaces the misleading 100% combined-model rate, which was created by deterministic simulated-store behavior.
- Store variance is calculated at one store-month row before comparison with the same-format peer average; the earlier category-row averaging defect is removed.

## Power BI checks

- Power BI Desktop 2.155.756.0 imported 14 PostgreSQL objects in Import mode.
- Semantic model contains 15 relationships and 38 DAX measures.
- Exactly four pages are named: Executive performance; Customer and retention; Product and store operations; Marketing and channel efficiency.
- The dashboard PDF contains exactly four 16:9 pages. Each page includes the required public-core plus simulated-extension provenance note.
- All four rendered pages were inspected. KPI text is legible with no clipping, overlap, black boxes, or broken glyphs. The blank total-context variance card and invalid channel ROI chart were removed; decision trends, corrected store peers, RFM value, and campaign ranking were added.

## Memo and package checks

- Decision memo contains exactly three findings and three actions; its PDF remains exactly two A4 pages.
- DOCX structural validation passed and both memo pages were rendered and inspected.
- Language uses no unsupported causal claims; limitations state the simulated-data and attribution boundaries.
- The delivery manifest names one authoritative PBIX, dashboard PDF, memo DOCX, memo PDF, and technical ZIP.

No open delivery gate remains.
