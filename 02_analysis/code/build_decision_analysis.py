"""Build decision-ready diagnostic tables from the governed processed facts.

This script does not modify raw inputs. It produces compact tables for the
Power BI report, evidence register, and executive memo. Combined-channel
customer results and all store/marketing results retain the simulation caveat.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT / "02_analysis" / "data" / "processed"
TABLES = PROJECT / "02_analysis" / "outputs" / "tables"
LOGS = PROJECT / "02_analysis" / "outputs" / "logs"


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.replace(0, np.nan))


def build() -> dict[str, float | int | str]:
    TABLES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    sales = pd.read_csv(
        PROCESSED / "fact_sales.csv",
        usecols=[
            "order_id",
            "transaction_timestamp",
            "customer_id",
            "product_id",
            "location_id",
            "channel_id",
            "quantity",
            "net_revenue",
            "cogs",
            "fulfilment_cost",
            "is_return",
            "source_system",
            "is_simulated",
        ],
        parse_dates=["transaction_timestamp"],
    )
    sales["month"] = sales["transaction_timestamp"].dt.to_period("M").dt.to_timestamp()
    sales["gross_margin"] = sales["net_revenue"] - sales["cogs"]
    sales["historical_contribution"] = sales["gross_margin"] - sales["fulfilment_cost"]

    products = pd.read_csv(PROCESSED / "dim_product.csv", usecols=["product_id", "category"])
    locations = pd.read_csv(
        PROCESSED / "dim_location.csv",
        usecols=["location_id", "location_name", "store_format", "location_type"],
    )
    channels = pd.read_csv(
        PROCESSED / "dim_channel.csv", usecols=["channel_id", "channel_name", "channel_type"]
    )

    completed = sales.loc[(~sales["is_return"]) & (sales["net_revenue"] > 0)].copy()
    identified = completed.loc[completed["customer_id"].notna()].copy()
    public_identified = identified.loc[identified["source_system"] == "UCI Online Retail"].copy()

    combined_frequency = identified.groupby("customer_id")["order_id"].nunique()
    public_frequency = public_identified.groupby("customer_id")["order_id"].nunique()
    combined_repeat_rate = float((combined_frequency >= 2).mean())
    public_repeat_rate = float((public_frequency >= 2).mean())

    rfm = pd.read_csv(TABLES / "customer_rfm.csv", parse_dates=["last_purchase"])
    segment = (
        rfm.groupby("rfm_segment", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            monetary_value=("monetary", "sum"),
            historical_clv=("observed_historical_clv", "sum"),
            average_clv=("observed_historical_clv", "mean"),
            median_clv=("observed_historical_clv", "median"),
            average_frequency=("frequency", "mean"),
            average_recency_days=("recency_days", "mean"),
        )
        .sort_values("monetary_value", ascending=False)
    )
    segment["customer_share"] = segment["customers"] / segment["customers"].sum()
    segment["monetary_share"] = segment["monetary_value"] / segment["monetary_value"].sum()
    segment["clv_share"] = segment["historical_clv"] / segment["historical_clv"].sum()
    segment["provenance"] = "Public core plus simulated store extension"
    segment.to_csv(TABLES / "customer_segment_summary.csv", index=False)

    store_sales = sales.merge(locations, on="location_id", how="left")
    store_sales = store_sales.loc[store_sales["location_type"] == "Physical store"].copy()
    store_month = (
        store_sales.groupby(
            ["month", "location_id", "location_name", "store_format"], as_index=False
        )
        .agg(
            net_revenue=("net_revenue", "sum"),
            gross_margin=("gross_margin", "sum"),
            orders=("order_id", "nunique"),
            return_lines=("is_return", "sum"),
            sales_lines=("order_id", "size"),
        )
    )
    store_month["peer_average_revenue"] = store_month.groupby(
        ["month", "store_format"]
    )["net_revenue"].transform("mean")
    store_month["store_variance"] = (
        store_month["net_revenue"] - store_month["peer_average_revenue"]
    )
    store_month["store_variance_pct"] = safe_divide(
        store_month["store_variance"], store_month["peer_average_revenue"]
    )
    store_month["gross_margin_pct"] = safe_divide(
        store_month["gross_margin"], store_month["net_revenue"]
    )
    store_month["return_line_rate"] = safe_divide(
        store_month["return_lines"], store_month["sales_lines"]
    )
    store_month["provenance"] = "Deterministic simulated store extension"
    store_month.to_csv(TABLES / "product_store_performance.csv", index=False)

    store_summary = (
        store_month.groupby(
            ["location_id", "location_name", "store_format"], as_index=False
        )
        .agg(
            net_revenue=("net_revenue", "sum"),
            gross_margin=("gross_margin", "sum"),
            orders=("orders", "sum"),
            return_lines=("return_lines", "sum"),
            sales_lines=("sales_lines", "sum"),
            peer_revenue=("peer_average_revenue", "sum"),
            store_variance=("store_variance", "sum"),
        )
    )
    store_summary["store_variance_pct"] = safe_divide(
        store_summary["store_variance"], store_summary["peer_revenue"]
    )
    store_summary["gross_margin_pct"] = safe_divide(
        store_summary["gross_margin"], store_summary["net_revenue"]
    )
    store_summary["return_line_rate"] = safe_divide(
        store_summary["return_lines"], store_summary["sales_lines"]
    )
    store_summary["provenance"] = "Deterministic simulated store extension"
    store_summary = store_summary.sort_values("store_variance", ascending=False)
    store_summary.to_csv(TABLES / "store_peer_summary.csv", index=False)

    category_sales = sales.merge(products, on="product_id", how="left")
    category = (
        category_sales.groupby("category", as_index=False)
        .agg(
            net_revenue=("net_revenue", "sum"),
            gross_margin=("gross_margin", "sum"),
            historical_contribution=("historical_contribution", "sum"),
            orders=("order_id", "nunique"),
            return_lines=("is_return", "sum"),
            sales_lines=("order_id", "size"),
            simulated_lines=("is_simulated", "sum"),
        )
        .sort_values("net_revenue", ascending=False)
    )
    category["revenue_share"] = category["net_revenue"] / category["net_revenue"].sum()
    category["gross_margin_pct"] = safe_divide(category["gross_margin"], category["net_revenue"])
    category["return_line_rate"] = safe_divide(category["return_lines"], category["sales_lines"])
    category["simulated_line_share"] = safe_divide(category["simulated_lines"], category["sales_lines"])
    category["provenance"] = "Simulated category and cost attributes on public and simulated sales"
    category.to_csv(TABLES / "category_performance_summary.csv", index=False)

    campaign = pd.read_csv(TABLES / "campaign_efficiency.csv")
    channel_efficiency = (
        campaign.groupby("channel_id", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            sessions=("sessions", "sum"),
            conversions=("conversions", "sum"),
            attributed_revenue=("attributed_revenue", "sum"),
            attributed_gross_margin=("attributed_gross_margin", "sum"),
            attributed_orders=("attributed_orders", "sum"),
        )
        .merge(channels, on="channel_id", how="left")
    )
    channel_efficiency["ctr"] = safe_divide(
        channel_efficiency["clicks"], channel_efficiency["impressions"]
    )
    channel_efficiency["conversion_rate"] = safe_divide(
        channel_efficiency["conversions"], channel_efficiency["sessions"]
    )
    channel_efficiency["roas"] = safe_divide(
        channel_efficiency["attributed_revenue"], channel_efficiency["spend"]
    )
    channel_efficiency["roi"] = safe_divide(
        channel_efficiency["attributed_gross_margin"] - channel_efficiency["spend"],
        channel_efficiency["spend"],
    )
    channel_efficiency["cac"] = safe_divide(
        channel_efficiency["spend"], channel_efficiency["conversions"]
    )
    channel_efficiency["provenance"] = "Deterministic simulated sessions, spend, costs and attribution"
    channel_efficiency = channel_efficiency.sort_values("roi", ascending=False)
    channel_efficiency.to_csv(TABLES / "channel_efficiency_summary.csv", index=False)

    sessions = pd.read_csv(
        PROCESSED / "fact_web_sessions.csv",
        usecols=[
            "session_id",
            "channel_id",
            "device_type",
            "product_views",
            "add_to_cart",
            "checkout_started",
            "converted",
        ],
    )
    sessions["viewed_product"] = sessions["product_views"] > 0
    funnel = (
        sessions.groupby(["channel_id", "device_type"], as_index=False)
        .agg(
            sessions=("session_id", "nunique"),
            product_view_sessions=("viewed_product", "sum"),
            add_to_cart_sessions=("add_to_cart", "sum"),
            checkout_sessions=("checkout_started", "sum"),
            conversions=("converted", "sum"),
        )
        .merge(channels, on="channel_id", how="left")
    )
    funnel["product_view_rate"] = safe_divide(funnel["product_view_sessions"], funnel["sessions"])
    funnel["add_to_cart_rate"] = safe_divide(funnel["add_to_cart_sessions"], funnel["sessions"])
    funnel["checkout_rate"] = safe_divide(funnel["checkout_sessions"], funnel["sessions"])
    funnel["conversion_rate"] = safe_divide(funnel["conversions"], funnel["sessions"])
    funnel["provenance"] = "Deterministic simulated web sessions"
    funnel.to_csv(TABLES / "web_funnel_summary.csv", index=False)

    monthly = pd.read_csv(TABLES / "monthly_performance.csv", parse_dates=["month"])
    complete_months = monthly.loc[monthly["month"] < monthly["month"].max()].copy()
    complete_months["gross_margin_pct"] = safe_divide(
        complete_months["gross_margin"], complete_months["net_revenue"]
    )
    complete_months["contribution_margin_pct"] = safe_divide(
        complete_months["contribution_margin"], complete_months["net_revenue"]
    )
    complete_months.to_csv(TABLES / "monthly_decision_summary.csv", index=False)

    champions = segment.loc[segment["rfm_segment"] == "Champions"].iloc[0]
    vulnerable = segment.loc[segment["rfm_segment"].isin(["At Risk", "Lost"])].sum(numeric_only=True)
    worst_store = store_summary.iloc[-1]
    best_store = store_summary.iloc[0]
    worst_channel = channel_efficiency.iloc[-1]
    best_channel = channel_efficiency.iloc[0]
    peak_month = complete_months.loc[complete_months["net_revenue"].idxmax()]
    trough_month = complete_months.loc[complete_months["net_revenue"].idxmin()]

    exceptions = pd.DataFrame(
        [
            {
                "priority": 1,
                "domain": "Customer",
                "entity": "At Risk + Lost",
                "metric": "Customer share",
                "value": vulnerable["customer_share"],
                "comparison": "Champions monetary share",
                "comparison_value": champions["monetary_share"],
                "recommended_action": "Separate value protection from capped reactivation",
                "provenance": "Public core plus simulated store extension",
            },
            {
                "priority": 2,
                "domain": "Store",
                "entity": worst_store["location_name"],
                "metric": "Peer variance",
                "value": worst_store["store_variance_pct"],
                "comparison": best_store["location_name"],
                "comparison_value": best_store["store_variance_pct"],
                "recommended_action": "Diagnose matched-format category, returns and conversion gaps",
                "provenance": "Deterministic simulated store extension",
            },
            {
                "priority": 3,
                "domain": "Marketing",
                "entity": worst_channel["channel_name"],
                "metric": "Campaign ROI",
                "value": worst_channel["roi"],
                "comparison": best_channel["channel_name"],
                "comparison_value": best_channel["roi"],
                "recommended_action": "Reallocate with a holdout test for incrementality",
                "provenance": "Deterministic simulated marketing extension",
            },
        ]
    )
    exceptions.to_csv(TABLES / "executive_exception_list.csv", index=False)

    metrics = {
        "combined_repeat_customer_rate": combined_repeat_rate,
        "public_core_repeat_customer_rate": public_repeat_rate,
        "combined_repeat_rate_is_simulation_artifact": combined_repeat_rate == 1.0,
        "identified_customers_combined": int(combined_frequency.size),
        "identified_customers_public_core": int(public_frequency.size),
        "champions_customer_share": float(champions["customer_share"]),
        "champions_monetary_share": float(champions["monetary_share"]),
        "at_risk_lost_customer_share": float(vulnerable["customer_share"]),
        "best_store": str(best_store["location_name"]),
        "best_store_variance_gbp": float(best_store["store_variance"]),
        "best_store_variance_pct": float(best_store["store_variance_pct"]),
        "worst_store": str(worst_store["location_name"]),
        "worst_store_variance_gbp": float(worst_store["store_variance"]),
        "worst_store_variance_pct": float(worst_store["store_variance_pct"]),
        "best_marketing_channel": str(best_channel["channel_name"]),
        "best_marketing_roi": float(best_channel["roi"]),
        "worst_marketing_channel": str(worst_channel["channel_name"]),
        "worst_marketing_roi": float(worst_channel["roi"]),
        "peak_complete_month": peak_month["month"].strftime("%Y-%m"),
        "peak_complete_month_revenue": float(peak_month["net_revenue"]),
        "trough_complete_month": trough_month["month"].strftime("%Y-%m"),
        "trough_complete_month_revenue": float(trough_month["net_revenue"]),
    }
    (LOGS / "depth-review-metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
