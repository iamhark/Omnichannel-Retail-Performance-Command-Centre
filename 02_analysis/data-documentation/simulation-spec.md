# Simulation Specification

**Version:** `omnichannel-sim-v1`  
**Random seed:** `20260718`

## Generated components

- Eight named UK stores across London, Manchester, Birmingham, Leeds, Glasgow, Bristol, Liverpool, and Edinburgh.
- Exactly 150,000 physical-store sale lines grouped into 50,000 three-line orders.
- Exactly 300,000 web sessions across Paid Search, Organic Search, Email, Social, and Direct.
- Twelve quarterly campaigns: four each for Paid Search, Email, and Social.
- Daily impressions, clicks, and spend for each campaign.
- Product category, standard cost, discount, fulfilment cost, store demand, device, funnel behavior, and campaign attribution fields.

## Integrity controls

- The generator is deterministic for the fixed seed.
- Generated records use `is_simulated=true` and `simulation_version=omnichannel-sim-v1`.
- The public UCI workbook remains unchanged.
- A provenance filter and visible notice are required in Power BI and the memo.
- Simulated correlations support workflow testing and business-case decisions only. They are not estimates of a real retailer's performance.
