# Limitations

1. The public source records one historical UK non-store retailer from 2010-2011. It does not represent current retail conditions.
2. Physical stores, product categories, standard costs, fulfilment costs, web sessions, campaigns, spend, and attribution are deterministic simulated extensions.
3. Campaign attribution uses last non-direct touch within seven days. It allocates credit; it does not estimate causal lift.
4. Customer IDs are missing for 135,080 raw rows. Anonymous transactions remain in revenue but are excluded from RFM, retention, repeat-rate, and observed CLV.
5. Exact duplicate rows are removed because the source lacks a line identifier. Some repeated lines could represent legitimate repeated items.
6. Product costs are simulated, so gross margin, contribution margin, CLV, and ROI are business-case measures.
7. December 2011 contains only nine days. Complete-month comparisons exclude it.
8. DAX-to-SQL reconciliation covers six scenarios. Other filter combinations remain untested and should be checked before expanding the report.
