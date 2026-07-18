# Decision Memo - Omnichannel Retail Performance Command Centre

**To:** Retail Executive Committee  
**From:** Harkirat Singh  
**Date:** 18 July 2026  
**Decision:** Reallocate retention, store-diagnostic, and marketing attention using the validated business-case model.

## Basis

The model combines the CC BY 4.0 UCI Online Retail transaction dataset with deterministic simulated physical-store, product-cost, web-session, campaign, and attribution extensions. The public records cover 1 December 2010 to 9 December 2011. All store and marketing results below are simulated business-case evidence, not observed company performance.

## Three findings and actions

### 1. Protect concentrated customer value; separate retention from reactivation

Champions comprise 714 of 4,371 identified customers (16.3%) but generate 46.1% of monetary value and average £1,793 observed historical CLV. At Risk and Lost segments contain 1,335 customers, or 30.5% of the identified base. In the unsimulated UCI transaction core, 65.6% of 4,338 identified purchasing customers place at least two completed orders. A single retention offer would mix two different jobs: protecting high-value relationships and testing whether lapsed demand remains recoverable.

**Action 1:** Protect Champions with service and loyalty treatment. Run a capped reactivation test for At Risk customers, then suppress Lost customers after two failed contacts. Monitor segment migration, public-core repeat purchase, retention, contribution per customer, and offer cost.

### 2. Diagnose matched-store gaps before changing network-wide targets

Within the simulated large-store tier, Manchester finishes £94,542 (+18.0%) above the peer baseline while Birmingham is £94,542 (-18.0%) below. Leeds is £44,976 (+11.4%) above the standard-store baseline; Bristol is £27,233 (-6.9%) below. The matched-format pairs provide a better diagnostic than a network average because format is held constant.

**Action 2:** Compare Manchester with Birmingham and Leeds with Bristol on category mix, returns, conversion, discounting, and staffing. Transfer only practices that survive those checks; do not impose uniform targets from this simulation.

### 3. Stop simulated Social spend from absorbing margin

Simulated Social campaigns produce -47.0% aggregate ROI and £421 acquisition cost. Email produces +52.4% ROI at £168 per conversion; Paid Search produces +51.1% ROI at £165. Last-touch attribution can under-credit Social-assisted demand, but the modeled gap is too large to ignore.

**Action 3:** Reduce Social prospecting allocation in the next simulated planning cycle, move the test budget to Email and Paid Search, and preserve a Social holdout to measure incrementality before a permanent decision.

## Limitations

- The public source is historical and online-only; it does not represent current retail conditions.
- Physical stores, costs, product categories, sessions, campaigns, spend, and attribution are simulated.
- Last non-direct attribution assigns credit; it does not estimate causal lift.
- Customer IDs are missing for 135,080 raw rows, so customer metrics exclude anonymous transactions.
- December 2011 contains nine days and is excluded from complete-month comparisons.
- DAX-to-SQL reconciliation covers six scenarios; other filter combinations remain untested.

## Metrics to monitor

| Decision area | Metrics | Cadence | Trigger |
|---|---|---|---|
| Customer value | Monthly retention, public-core repeat rate, segment migration, observed historical CLV, contribution per customer | Monthly | Two consecutive declines or rising At Risk share |
| Store operations | Net revenue, gross-margin rate, return rate, peer variance by store format and category | Weekly / monthly | Negative peer variance for two complete periods |
| Marketing | Spend, conversion, CAC, attributed revenue, ROAS, ROI, holdout lift | Weekly / campaign close | Negative ROI or CAC above customer contribution |

**Evidence:** `CLM-002` to `CLM-008` in `03_synthesis/evidence-register.md`. Computed tables are under `02_analysis/outputs/tables/`.  
**Source:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. CC BY 4.0.
