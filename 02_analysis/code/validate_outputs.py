from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]
DATA = PROJECT / "02_analysis" / "data" / "processed"
TABLES = PROJECT / "02_analysis" / "outputs" / "tables"
LOGS = PROJECT / "02_analysis" / "outputs" / "logs"
RAW = PROJECT / "01_inputs" / "data" / "raw" / "public" / "uci-online-retail" / "Online Retail.xlsx"
EXPECTED_HASH = "43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d"


def main() -> None:
    sales = pd.read_csv(DATA / "fact_sales.csv", low_memory=False)
    sessions = pd.read_csv(DATA / "fact_web_sessions.csv", low_memory=False)
    spend = pd.read_csv(DATA / "fact_campaign_spend.csv")
    products = pd.read_csv(DATA / "dim_product.csv")
    locations = pd.read_csv(DATA / "dim_location.csv")
    channels = pd.read_csv(DATA / "dim_channel.csv")
    campaigns = pd.read_csv(DATA / "dim_campaign.csv")
    rfm = pd.read_csv(TABLES / "customer_rfm.csv")
    retention = pd.read_csv(TABLES / "customer_retention.csv")
    campaign_efficiency = pd.read_csv(TABLES / "campaign_efficiency.csv")

    order_dates = pd.to_datetime(sales.groupby("order_id")["transaction_timestamp"].min())
    attributed = sessions.loc[sessions["converted"].eq(True) & sessions["attributed_order_id"].notna(),
                              ["session_timestamp", "attributed_order_id"]].copy()
    attributed["session_date"] = pd.to_datetime(attributed["session_timestamp"]).dt.normalize()
    attributed["order_date"] = attributed["attributed_order_id"].map(order_dates).dt.normalize()
    attributed["lag_days"] = (attributed["order_date"] - attributed["session_date"]).dt.days

    revenue_error = (sales["net_revenue"] - sales["quantity"] * sales["unit_price"] * (1 - sales["discount_rate"])).abs().max()
    roi_expected = (campaign_efficiency["attributed_gross_margin"] - campaign_efficiency["spend"]) / campaign_efficiency["spend"]

    tests = {
        "raw_checksum": hashlib.sha256(RAW.read_bytes()).hexdigest() == EXPECTED_HASH,
        "sales_primary_key": sales["sales_line_id"].is_unique,
        "session_primary_key": sessions["session_id"].is_unique,
        "spend_primary_key": spend["spend_id"].is_unique,
        "expected_store_rows": int((sales["source_system"] == "Simulated extension").sum()) == 150_000,
        "expected_session_rows": len(sessions) == 300_000,
        "revenue_arithmetic": float(revenue_error) <= 0.01,
        "provenance_complete": not sales[["source_system", "source_record_id", "is_simulated"]].isna().any().any(),
        "simulation_version_complete": not sales.loc[sales["is_simulated"].eq(True), "simulation_version"].isna().any(),
        "product_fk": sales["product_id"].isin(products["product_id"]).all(),
        "location_fk": sales["location_id"].isin(locations["location_id"]).all(),
        "channel_fk": sales["channel_id"].isin(channels["channel_id"]).all(),
        "campaign_fk": sales["campaign_id"].dropna().isin(campaigns["campaign_id"]).all(),
        "attribution_order_exists": attributed["order_date"].notna().all(),
        "attribution_window": attributed["lag_days"].between(0, 6).all(),
        "positive_campaign_spend": (spend["spend"] > 0).all(),
        "retention_bounds": retention["retention_rate"].dropna().between(0, 1).all(),
        "rfm_excludes_anonymous": not rfm["customer_id"].isna().any(),
        "campaign_roi_formula": np.allclose(campaign_efficiency["roi"], roi_expected, atol=1e-10, equal_nan=True),
    }
    tests = {name: bool(value) for name, value in tests.items()}
    result = {
        "status": "pass" if all(tests.values()) else "fail",
        "tests": tests,
        "metrics": {
            "fact_sales_rows": len(sales),
            "web_session_rows": len(sessions),
            "campaign_spend_rows": len(spend),
            "revenue_arithmetic_max_abs_error": float(revenue_error),
            "attributed_orders_checked": len(attributed),
            "attribution_lag_min_days": int(attributed["lag_days"].min()),
            "attribution_lag_max_days": int(attributed["lag_days"].max()),
        },
    }
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "validation-results-extended.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
