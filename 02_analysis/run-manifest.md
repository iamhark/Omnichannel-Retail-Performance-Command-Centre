# Run Manifest

| Run | Command | Output | Status |
|---|---|---|---|
| Build | Bundled Python `02_analysis/code/build_analytics_data.py` | Processed dimensions/facts, metric tables, base validation JSON | pass |
| Extended validation | Bundled Python `02_analysis/code/validate_outputs.py` | Extended validation JSON | pass |
| Python syntax | `python -m py_compile` on three project scripts | No output on success | pass |
| PostgreSQL | See `02_analysis/sql/README.md` | Analytics schema/views and reconciliation output | complete - PostgreSQL 18.4 |
| Power BI | PostgreSQL Import model, TMDL measures, DAX query reconciliation, four-page PDF export | Final PBIX, PDF, and `outputs/logs/powerbi-reconciliation.csv` | pass - Power BI Desktop 2.155.756.0 |

**Simulation seed:** `20260718`  
**Simulation version:** `omnichannel-sim-v1`  
**Raw SHA-256:** `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`
