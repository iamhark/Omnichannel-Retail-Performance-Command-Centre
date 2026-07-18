from __future__ import annotations

import argparse
from pathlib import Path

import psycopg

PROJECT = Path(__file__).resolve().parents[2]
DATA = PROJECT / "02_analysis" / "data" / "processed"

TABLES = [
    "dim_customer", "dim_product", "dim_date", "dim_location", "dim_channel", "dim_campaign",
    "fact_sales", "fact_web_sessions", "fact_campaign_spend",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load processed CSVs into PostgreSQL staging tables.")
    parser.add_argument("--dsn", required=True, help="PostgreSQL DSN, for example postgresql://user:pass@localhost:5432/omnichannel_retail")
    args = parser.parse_args()

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            for name in TABLES:
                path = DATA / f"{name}.csv"
                if not path.exists():
                    raise FileNotFoundError(path)
                cur.execute(f'TRUNCATE TABLE staging."{name}"')
                with path.open("r", encoding="utf-8") as source:
                    with cur.copy(f'COPY staging."{name}" FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL \'\')') as copy:
                        while chunk := source.read(1024 * 1024):
                            copy.write(chunk)
        conn.commit()
    print("Loaded processed CSVs into staging. Run 01_build_analytics.sql, 02_views.sql, and 03_validation.sql next.")


if __name__ == "__main__":
    main()
