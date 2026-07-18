# PostgreSQL Execution

Run against a dedicated local database named `omnichannel_retail`.

```powershell
psql -d omnichannel_retail -f 00_create_staging.sql
python ..\code\load_postgres.py --dsn "postgresql://USER:PASSWORD@localhost:5432/omnichannel_retail"
psql -d omnichannel_retail -f 01_build_analytics.sql
psql -d omnichannel_retail -f 02_views.sql
psql -d omnichannel_retail -f 03_validation.sql
```

`00_create_staging.sql` recreates only this project's staging tables. `01_build_analytics.sql` recreates only the `analytics` schema in the selected database. Do not point these scripts at a database where an unrelated `analytics` schema must be preserved.

The local Python reference tables under `02_analysis/outputs/tables/` provide reconciliation targets until PostgreSQL is installed.
