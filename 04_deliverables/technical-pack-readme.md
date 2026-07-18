# Technical Portfolio Pack

This package contains the reproducible analytical design, validated reference outputs, governance records, and decision evidence for the Omnichannel Retail Performance Command Centre.

## Included

- project brief, decisions, source register, evidence register, insight register, and limitations;
- Python build, PostgreSQL load, validation, memo, and dashboard-prototype source code;
- PostgreSQL staging, star-schema, analytical-view, validation, and reconciliation scripts;
- Power BI model specification, DAX measure catalog, and Power BI reconciliation output;
- data catalog, dictionary, simulation specification, analysis plan, and methods log;
- aggregate analytical tables, eight decision-analysis tables, and machine-readable validation results;
- delivery manifest and pre-delivery QA report.

## Excluded

The 22 MB UCI workbook, raw ZIP, large processed fact CSVs, and 36 MB PBIX are excluded to keep this technical package compact. Retrieve the immutable source from DOI `10.24432/C5BW33`. The expected XLSX SHA-256 is `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`. The authoritative PBIX is delivered separately under `04_deliverables/final/`.

## Runtime validation

The Python reference model passed 19 of 19 extended integrity checks. PostgreSQL 18.4 executed the schema, views, seven SQL integrity checks, and six reference reconciliations successfully. Power BI Desktop 2.155.756.0 imported the PostgreSQL model, applied 38 DAX measures, and matched six approved SQL scenarios exactly. The refinement also validated the public-core repeat boundary and corrected store-month peer comparison. Its four-page PDF export passed text extraction and rendered-page inspection.
