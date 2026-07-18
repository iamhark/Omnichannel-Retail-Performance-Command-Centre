# Data Dictionary

## Shared fact fields

| Field | Meaning |
|---|---|
| `date_key` | Integer calendar key in `YYYYMMDD` format |
| `source_system` | Public or simulated origin |
| `source_record_id` | Stable source or generated record identifier |
| `is_simulated` | `true` only for generated business-case records |
| `simulation_version` | `omnichannel-sim-v1` for generated records; blank for public records |

## Sales measures

| Field | Definition |
|---|---|
| `net_revenue` | `quantity * unit_price * (1 - discount_rate)`; returns remain signed |
| `cogs` | Signed quantity multiplied by simulated standard product cost |
| `fulfilment_cost` | Simulated per-unit fulfilment or return-handling cost; always a cost |
| `is_return` | Cancellation-coded or negative-quantity line |

## Customer measures

| Metric | Definition |
|---|---|
| Monthly retention | Prior-month customers who buy again in the current month divided by prior-month active customers |
| Repeat purchase rate | Identified customers with at least two completed orders divided by identified purchasing customers |
| Observed Historical CLV | Cumulative gross margin minus fulfilment cost across the observed period; not predictive |
| RFM | Quintile scores: low recency is better; high frequency and monetary value are better |

## Campaign measures

| Metric | Definition |
|---|---|
| Attribution | Last non-direct simulated session within seven days before a public online order |
| ROAS | Attributed net revenue divided by campaign spend |
| ROI | `(attributed gross margin - campaign spend) / campaign spend` |
| CAC | Campaign spend divided by converted sessions |
