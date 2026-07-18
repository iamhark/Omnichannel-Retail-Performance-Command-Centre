# Project Brief - Omnichannel Retail Performance Command Centre

## Question and purpose

**Business question:** Which customer segments, product categories, channels, and store locations require action to improve revenue, retention, and operating performance?

**Why this matters now:** The prior MA-SET1 work contains useful retail themes but cannot evidence a coherent omnichannel model. Its modules lack common keys, cost fields, session-level behavior, campaign attribution, and source provenance. This project replaces those constraints with an auditable public core, clearly labelled simulation, PostgreSQL transformations, SQL metrics, and a decision-focused Power BI specification.

**Audience and decision/use:** Retail executive committee deciding where to intervene across customer retention, product margin, store performance, and marketing efficiency.

## Scope

**In scope:** Net revenue, gross margin, contribution margin, month-over-month growth, AOV, monthly retention, repeat purchase, observed historical CLV, RFM, product and category margin, store peer variance, funnel performance, campaign ROAS and ROI, PostgreSQL dimensional modeling, DAX, decision memo, and portfolio documentation.

**Out of scope:** Predictive CLV, causal campaign lift, real current-market performance, inventory optimization, Power BI Service publishing, scheduled refresh, row-level security, and public GitHub release.

**Population, setting, and time period:** UK-based non-store retail transactions from 1 December 2010 through 9 December 2011, extended with deterministic simulated UK stores, web sessions, and campaigns over the same period.

## Deliverables and success criteria

| Deliverable | Audience | Status gate | What makes it successful? |
|---|---|---|---|
| Power BI command centre source | Hiring managers and retail analysts | Requires Power BI Desktop | Four named 16:9 pages; accessible design; correct filter behavior; SQL/DAX reconciliation; provenance note on every page |
| Dashboard PDF export | Retail executive committee | Requires Power BI Desktop | Four legible pages matching the approved source report |
| Two-page decision memo, DOCX and PDF | Retail executive committee | Analysis required | Exactly three findings and three actions; specific limitations; monitoring metrics; all claims trace to outputs |
| Technical portfolio pack | Hiring managers and reviewers | Local build | PostgreSQL schema/views, Python pipeline, DAX catalog, model spec, ERD, data dictionary, validation evidence, and reproduction instructions |

## Known inputs and risks

- **Primary source:** `SRC-001`, UCI Online Retail, CC BY 4.0, DOI `10.24432/C5BW33`.
- **Raw checksum:** SHA-256 `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`.
- **Raw profile:** 541,909 rows and 8 columns; 135,080 missing customer IDs; 1,454 missing descriptions; 5,268 exact duplicate rows; 9,288 cancellation-coded lines; 10,624 negative-quantity lines; 2,517 non-positive-price lines.
- **Simulation:** Seed `20260718`; eight UK stores; twelve campaigns; five marketing channels; 150,000 physical-store lines; 300,000 web sessions.
- **Legacy references:** MA-SET1 workbook, report, and deck are reference-only; their claims are not imported.
- **Runtime status:** PostgreSQL 18.4 and Power BI Desktop 2.155.756.0 were detected and used on 2026-07-18. PostgreSQL execution, PBIX authoring, six-scenario DAX reconciliation, and the four-page PDF export are complete.
- **Currency:** GBP. Historical values are not inflation-adjusted.
- **Privacy:** Customer identifiers are pseudonymous; no direct personal identifiers are present.
- **Rubric:** None supplied. Professional portfolio and workspace quality gates apply.

## Dataset profile

| Field | Type | Nulls | Analytical treatment |
|---|---|---:|---|
| InvoiceNo | identifier | 0 | Cancellation prefix retained; converted to text |
| StockCode | identifier | 0 | Product natural key |
| Description | text | 1,454 | Filled as `Unknown product`; missingness reported |
| Quantity | integer | 0 | Negative values retained as returns; zero quarantined |
| InvoiceDate | timestamp | 0 | Source for order and date keys |
| UnitPrice | GBP | 0 | Non-positive values quarantined from sales facts |
| CustomerID | identifier | 135,080 | Anonymous sales retained; excluded from customer metrics |
| Country | category | 0 | Online location dimension |

Exact duplicate rows are removed from the analytical copy because the source has no line identifier. The raw workbook remains unchanged.
