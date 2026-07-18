# Source Register - Omnichannel Retail Performance Command Centre

| Source ID | Source | Type | Provider | Date/version | Access date | URL/path | Reliability | Use and boundary |
|---|---|---|---|---|---|---|---|---|
| SRC-001 | Online Retail | Public transaction dataset | Daqing Chen / UCI Machine Learning Repository | Donated 2015; records 2010-12-01 to 2011-12-09 | 2026-07-18 | https://doi.org/10.24432/C5BW33; `01_inputs/data/raw/public/uci-online-retail/Online Retail.xlsx` | Strong for recorded fields; historical | Immutable public core; CC BY 4.0; non-store UK retailer |
| SRC-002 | Omnichannel simulated extensions | Generated business-case data | Project pipeline | Simulation v1, seed `20260718` | 2026-07-18 | `02_analysis/code/build_analytics_data.py`; processed CSV outputs | Limited to internal coherence | Store, web, campaign, cost, category, and attribution fields; never presented as observed company data |
| SRC-LEG-001 | DATA_MA_SET1.xlsx | Legacy workbook | Unknown original provider | Modified 2026-05-21 | 2026-07-18 | `../2026-07-legacy-ma-set1-bi-strategy/01_inputs/data/raw/DATA_MA_SET1.xlsx` | Limited | Reference-only; SHA-256 `eb654fca88a165ec6ac3ea5c65f65925d79cd4b287ecb5df46c4c7f3a592abb9`; raw provenance absent |
| SRC-LEG-002 | MA-SET1 analytical report | Legacy derived document | Harkirat Singh | 2026-05-21 | 2026-07-18 | `../2026-07-legacy-ma-set1-bi-strategy/04_deliverables/final/Harkirat_Singh_240800_Analytical_Report.docx` | Unverified secondary source | Reference-only; SHA-256 `8fd9bb0184723e35b499386d9beaf0eb6aa4ef564529e49797965a21ec29908a` |
| SRC-LEG-003 | MA-SET1 slide deck | Legacy derived presentation | Harkirat Singh | 2026-05-21 | 2026-07-18 | `../2026-07-legacy-ma-set1-bi-strategy/04_deliverables/final/Harkirat_Singh_240800_Slide_Deck.pptx` | Unverified secondary source | Reference-only; SHA-256 `43faed34c33e3a48edd67771d14837c4b17e13cb93288b6f53d61d34b66144f2` |

## Required attribution

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed CC BY 4.0.
