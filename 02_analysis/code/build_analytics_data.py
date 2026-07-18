from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260718
SIM_VERSION = "omnichannel-sim-v1"
STORE_LINES = 150_000
WEB_SESSIONS = 300_000

PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "01_inputs" / "data" / "raw" / "public" / "uci-online-retail" / "Online Retail.xlsx"
PROCESSED = PROJECT / "02_analysis" / "data" / "processed"
TABLES = PROJECT / "02_analysis" / "outputs" / "tables"
LOGS = PROJECT / "02_analysis" / "outputs" / "logs"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def customer_id(series: pd.Series) -> pd.Series:
    return series.map(lambda x: None if pd.isna(x) else f"C{int(x):05d}")


def classify_products(description: pd.Series) -> pd.Series:
    text = description.fillna("").str.upper()
    conditions = [
        text.str.contains(r"MUG|CUP|PLATE|BOWL|SPOON|FORK|TEA|KITCHEN", regex=True),
        text.str.contains(r"CHRISTMAS|EASTER|VALENTINE|BIRTHDAY|GIFT|WRAP", regex=True),
        text.str.contains(r"BAG|PURSE|NECKLACE|BRACELET|SCARF|UMBRELLA", regex=True),
        text.str.contains(r"CARD|NOTEBOOK|PENCIL|PEN |STICKER|PAPER", regex=True),
        text.str.contains(r"CANDLE|LANTERN|FRAME|CLOCK|CUSHION|HEART|DECOR", regex=True),
    ]
    choices = ["Kitchen & Dining", "Gifts & Seasonal", "Accessories", "Stationery", "Home Decor"]
    return pd.Series(np.select(conditions, choices, default="Other"), index=description.index)


def rfm_segments(rfm: pd.DataFrame) -> pd.Series:
    r, f, m = rfm["r_score"], rfm["f_score"], rfm["m_score"]
    conditions = [
        (r >= 4) & (f >= 4) & (m >= 4),
        (r >= 3) & (f >= 4),
        (r >= 4) & (f.between(2, 3)),
        (r <= 2) & (f >= 3),
        (r == 1) & (f <= 2),
    ]
    choices = ["Champions", "Loyal", "Potential Loyalists", "At Risk", "Lost"]
    return pd.Series(np.select(conditions, choices, default="Other"), index=rfm.index)


def score_quintiles(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    ranked = series.rank(method="first", ascending=True)
    score = pd.qcut(ranked, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return score if higher_is_better else 6 - score


def build() -> dict:
    rng = np.random.default_rng(SEED)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    raw_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    raw = pd.read_excel(RAW)
    raw_rows = len(raw)
    duplicate_rows = int(raw.duplicated().sum())
    clean = raw.drop_duplicates().copy()
    clean["Description"] = clean["Description"].fillna("Unknown product").astype(str).str.strip()
    clean["InvoiceNo"] = clean["InvoiceNo"].astype(str).str.strip()
    clean["StockCode"] = clean["StockCode"].astype(str).str.strip()
    clean["CustomerID_clean"] = customer_id(clean["CustomerID"])
    clean["InvoiceDate"] = pd.to_datetime(clean["InvoiceDate"])
    invalid = (clean["UnitPrice"] <= 0) | (clean["Quantity"] == 0)
    quarantine = clean.loc[invalid].copy()
    clean = clean.loc[~invalid].copy()

    product_base = (
        clean.groupby("StockCode", as_index=False)
        .agg(product_name=("Description", lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0]),
             median_unit_price=("UnitPrice", "median"))
        .sort_values("StockCode")
        .reset_index(drop=True)
    )
    product_base["category"] = classify_products(product_base["product_name"])
    product_base["cost_ratio"] = rng.uniform(0.38, 0.68, len(product_base)).round(4)
    product_base["standard_cost"] = (product_base["median_unit_price"] * product_base["cost_ratio"]).round(4)
    dim_product = product_base.rename(columns={"StockCode": "product_id"})
    dim_product["source_system"] = "UCI Online Retail + simulated attributes"
    dim_product["is_simulated_category"] = True
    dim_product["is_simulated_cost"] = True
    dim_product["simulation_version"] = SIM_VERSION

    product_lookup = dim_product.set_index("product_id")
    clean["product_id"] = clean["StockCode"]
    clean["standard_cost"] = clean["product_id"].map(product_lookup["standard_cost"])
    clean["date_key"] = clean["InvoiceDate"].dt.strftime("%Y%m%d").astype(int)
    clean["location_id"] = "COUNTRY-" + clean["Country"].map(slug)
    clean["is_return"] = clean["InvoiceNo"].str.startswith("C") | (clean["Quantity"] < 0)
    clean["discount_rate"] = 0.0
    clean["net_revenue"] = (clean["Quantity"] * clean["UnitPrice"]).round(4)
    clean["cogs"] = (clean["Quantity"] * clean["standard_cost"]).round(4)
    clean["fulfilment_cost"] = np.where(clean["is_return"], clean["Quantity"].abs() * 0.25, clean["Quantity"].abs() * 0.35).round(4)
    clean["source_record_id"] = "UCI-ROW-" + (clean.index + 2).astype(str)

    public_sales = pd.DataFrame({
        "sales_line_id": "UCI-LINE-" + (clean.index + 2).astype(str),
        "order_id": clean["InvoiceNo"],
        "transaction_timestamp": clean["InvoiceDate"],
        "date_key": clean["date_key"],
        "customer_id": clean["CustomerID_clean"],
        "product_id": clean["product_id"],
        "location_id": clean["location_id"],
        "channel_id": "SALES_ONLINE",
        "campaign_id": None,
        "quantity": clean["Quantity"].astype(int),
        "unit_price": clean["UnitPrice"].round(4),
        "discount_rate": clean["discount_rate"],
        "net_revenue": clean["net_revenue"],
        "cogs": clean["cogs"],
        "fulfilment_cost": clean["fulfilment_cost"],
        "is_return": clean["is_return"],
        "source_system": "UCI Online Retail",
        "source_record_id": clean["source_record_id"],
        "is_simulated": False,
        "simulation_version": None,
    })

    known = clean.loc[clean["CustomerID_clean"].notna()].copy()
    dim_customer = (
        known.groupby("CustomerID_clean", as_index=False)
        .agg(country=("Country", lambda s: s.mode().iat[0]),
             signup_date=("InvoiceDate", "min"),
             last_observed_date=("InvoiceDate", "max"))
        .rename(columns={"CustomerID_clean": "customer_id"})
    )
    dim_customer["source_system"] = "UCI Online Retail"
    dim_customer["is_simulated"] = False
    dim_customer["simulation_version"] = None

    stores = pd.DataFrame([
        ("STORE-LONDON-CITY", "London City", "London", "England", "Flagship", 1.25),
        ("STORE-MANCHESTER-CITY", "Manchester City", "Manchester", "England", "Large", 1.10),
        ("STORE-BIRMINGHAM-CITY", "Birmingham City", "Birmingham", "England", "Large", 1.05),
        ("STORE-LEEDS-CITY", "Leeds City", "Leeds", "England", "Standard", 0.95),
        ("STORE-GLASGOW-CITY", "Glasgow City", "Glasgow", "Scotland", "Standard", 0.90),
        ("STORE-BRISTOL-CITY", "Bristol City", "Bristol", "England", "Standard", 0.92),
        ("STORE-LIVERPOOL-CITY", "Liverpool City", "Liverpool", "England", "Standard", 0.88),
        ("STORE-EDINBURGH-CITY", "Edinburgh City", "Edinburgh", "Scotland", "Standard", 0.86),
    ], columns=["location_id", "location_name", "city", "region", "store_format", "demand_weight"])
    country_locations = pd.DataFrame({"country": sorted(clean["Country"].unique())})
    country_locations["location_id"] = "COUNTRY-" + country_locations["country"].map(slug)
    country_locations["location_name"] = country_locations["country"]
    country_locations["city"] = None
    country_locations["region"] = country_locations["country"]
    country_locations["store_format"] = "Online market"
    country_locations["location_type"] = "Country"
    country_locations["is_simulated"] = False
    store_locations = stores.copy()
    store_locations["country"] = "United Kingdom"
    store_locations["location_type"] = "Physical store"
    store_locations["is_simulated"] = True
    dim_location = pd.concat([
        country_locations[["location_id", "location_name", "city", "region", "country", "store_format", "location_type", "is_simulated"]],
        store_locations[["location_id", "location_name", "city", "region", "country", "store_format", "location_type", "is_simulated"]],
    ], ignore_index=True)
    dim_location["source_system"] = np.where(dim_location["is_simulated"], "Simulated extension", "UCI Online Retail")
    dim_location["simulation_version"] = np.where(dim_location["is_simulated"], SIM_VERSION, None)

    dim_channel = pd.DataFrame([
        ("SALES_ONLINE", "Online", "Sales", False),
        ("SALES_STORE", "Physical Store", "Sales", True),
        ("MKT_PAID_SEARCH", "Paid Search", "Marketing", True),
        ("MKT_ORGANIC_SEARCH", "Organic Search", "Marketing", True),
        ("MKT_EMAIL", "Email", "Marketing", True),
        ("MKT_SOCIAL", "Social", "Marketing", True),
        ("MKT_DIRECT", "Direct", "Marketing", True),
    ], columns=["channel_id", "channel_name", "channel_type", "is_simulated"])
    dim_channel["source_system"] = np.where(dim_channel["is_simulated"], "Simulated extension", "Derived from public source")
    dim_channel["simulation_version"] = np.where(dim_channel["is_simulated"], SIM_VERSION, None)

    min_date = clean["InvoiceDate"].dt.normalize().min()
    max_date = clean["InvoiceDate"].dt.normalize().max()
    campaign_rows = []
    marketing_campaign_channels = ["MKT_PAID_SEARCH", "MKT_EMAIL", "MKT_SOCIAL"]
    boundaries = pd.date_range(min_date, max_date + pd.Timedelta(days=1), periods=5)
    for channel in marketing_campaign_channels:
        code = channel.replace("MKT_", "")
        for quarter in range(4):
            campaign_rows.append((f"CMP-{code}-{quarter + 1:02d}", f"{code.title().replace('_', ' ')} Campaign {quarter + 1}", channel,
                                  boundaries[quarter].normalize(), (boundaries[quarter + 1] - pd.Timedelta(days=1)).normalize()))
    dim_campaign = pd.DataFrame(campaign_rows, columns=["campaign_id", "campaign_name", "channel_id", "start_date", "end_date"])
    dim_campaign["objective"] = "Acquire or reactivate customers"
    dim_campaign["source_system"] = "Simulated extension"
    dim_campaign["is_simulated"] = True
    dim_campaign["simulation_version"] = SIM_VERSION

    positive_orders = (
        public_sales.loc[~public_sales["is_return"] & (public_sales["net_revenue"] > 0)]
        .groupby("order_id", as_index=False)
        .agg(order_timestamp=("transaction_timestamp", "min"), customer_id=("customer_id", "first"),
             location_id=("location_id", "first"), order_revenue=("net_revenue", "sum"), order_gross_margin=("cogs", lambda s: 0.0))
    )
    margin_by_order = public_sales.groupby("order_id").apply(lambda g: (g["net_revenue"] - g["cogs"]).sum(), include_groups=False)
    positive_orders["order_gross_margin"] = positive_orders["order_id"].map(margin_by_order)

    session_count = WEB_SESSIONS
    channels = np.array(["MKT_PAID_SEARCH", "MKT_ORGANIC_SEARCH", "MKT_EMAIL", "MKT_SOCIAL", "MKT_DIRECT"])
    channel_probs = np.array([0.24, 0.25, 0.18, 0.14, 0.19])
    session_channel = rng.choice(channels, session_count, p=channel_probs)
    date_days = (max_date - min_date).days
    session_dates = min_date + pd.to_timedelta(rng.integers(0, date_days + 1, session_count), unit="D")
    session_customers = rng.choice(dim_customer["customer_id"].to_numpy(), session_count)
    session_customers = session_customers.astype(object)
    session_customers[rng.random(session_count) < 0.30] = None
    devices = rng.choice(["Desktop", "Mobile", "Tablet"], session_count, p=[0.48, 0.44, 0.08])
    page_views = np.maximum(1, rng.poisson(4.2, session_count)).astype(int)
    product_views = np.minimum(page_views, rng.binomial(page_views, 0.62)).astype(int)
    atc_prob = pd.Series(session_channel).map({"MKT_PAID_SEARCH": 0.13, "MKT_ORGANIC_SEARCH": 0.11, "MKT_EMAIL": 0.17, "MKT_SOCIAL": 0.08, "MKT_DIRECT": 0.12}).to_numpy()
    add_to_cart = rng.random(session_count) < atc_prob
    checkout = add_to_cart & (rng.random(session_count) < 0.58)
    converted = checkout & (rng.random(session_count) < 0.46)
    converted_idx = np.flatnonzero(converted)
    if len(converted_idx) > len(positive_orders):
        converted_idx = rng.choice(converted_idx, len(positive_orders), replace=False)
        converted[:] = False
        converted[converted_idx] = True
    attributed_orders = positive_orders.sample(len(converted_idx), random_state=SEED).reset_index(drop=True)
    attributed_order_id = np.full(session_count, None, dtype=object)
    attributed_order_id[converted_idx] = attributed_orders["order_id"].to_numpy()
    session_dates = pd.Series(session_dates)
    session_dates.iloc[converted_idx] = attributed_orders["order_timestamp"].dt.normalize().to_numpy() - pd.to_timedelta(rng.integers(0, 7, len(converted_idx)), unit="D")
    session_dates = session_dates.clip(lower=min_date, upper=max_date)
    session_customers[converted_idx] = attributed_orders["customer_id"].to_numpy()

    campaign_map = {}
    for row in dim_campaign.itertuples(index=False):
        campaign_map.setdefault(row.channel_id, []).append(row)

    def campaign_for(channel: str, date: pd.Timestamp) -> str | None:
        for campaign in campaign_map.get(channel, []):
            if campaign.start_date <= date <= campaign.end_date:
                return campaign.campaign_id
        return None

    campaign_ids = [campaign_for(ch, pd.Timestamp(dt)) for ch, dt in zip(session_channel, session_dates)]
    customer_country = dim_customer.set_index("customer_id")["country"].to_dict()
    session_country = [customer_country.get(c, "United Kingdom") if c is not None else "United Kingdom" for c in session_customers]
    fact_web_sessions = pd.DataFrame({
        "session_id": [f"SIM-SESSION-{i + 1:07d}" for i in range(session_count)],
        "session_timestamp": session_dates + pd.to_timedelta(rng.integers(0, 86_400, session_count), unit="s"),
        "date_key": session_dates.dt.strftime("%Y%m%d").astype(int),
        "customer_id": session_customers,
        "location_id": ["COUNTRY-" + slug(c) for c in session_country],
        "channel_id": session_channel,
        "campaign_id": campaign_ids,
        "device_type": devices,
        "page_views": page_views,
        "product_views": product_views,
        "add_to_cart": add_to_cart,
        "checkout_started": checkout,
        "converted": converted,
        "attributed_order_id": attributed_order_id,
        "source_system": "Simulated extension",
        "source_record_id": [f"SIM-SESSION-{i + 1:07d}" for i in range(session_count)],
        "is_simulated": True,
        "simulation_version": SIM_VERSION,
    })

    order_campaign = fact_web_sessions.loc[fact_web_sessions["converted"] & fact_web_sessions["campaign_id"].notna()].set_index("attributed_order_id")["campaign_id"]
    public_sales["campaign_id"] = public_sales["order_id"].map(order_campaign)

    order_count = STORE_LINES // 3
    store_order_ids = np.repeat([f"SIM-STORE-ORDER-{i + 1:06d}" for i in range(order_count)], 3)
    store_weights = stores["demand_weight"].to_numpy()
    store_weights = store_weights / store_weights.sum()
    order_store = rng.choice(stores["location_id"].to_numpy(), order_count, p=store_weights)
    order_customer = rng.choice(dim_customer["customer_id"].to_numpy(), order_count).astype(object)
    order_customer[rng.random(order_count) < 0.15] = None
    order_date = min_date + pd.to_timedelta(rng.integers(0, date_days + 1, order_count), unit="D")
    order_return = rng.random(order_count) < 0.025
    product_weights = clean["product_id"].value_counts(normalize=True).reindex(dim_product["product_id"], fill_value=0).to_numpy()
    product_weights = product_weights / product_weights.sum()
    store_products = rng.choice(dim_product["product_id"].to_numpy(), STORE_LINES, p=product_weights)
    base_prices = pd.Series(store_products).map(product_lookup["median_unit_price"]).to_numpy()
    store_price = np.maximum(0.10, base_prices * rng.lognormal(mean=0.02, sigma=0.08, size=STORE_LINES)).round(2)
    store_qty = rng.integers(1, 13, STORE_LINES)
    store_qty[np.repeat(order_return, 3)] *= -1
    store_discount = rng.choice([0.0, 0.05, 0.10, 0.15], STORE_LINES, p=[0.70, 0.14, 0.11, 0.05])
    store_cost = pd.Series(store_products).map(product_lookup["standard_cost"]).to_numpy()
    store_net = (store_qty * store_price * (1 - store_discount)).round(4)
    store_cogs = (store_qty * store_cost).round(4)
    store_fulfil = (np.abs(store_qty) * np.where(store_qty < 0, 0.20, 0.15)).round(4)
    store_dates = np.repeat(order_date, 3)
    store_fact = pd.DataFrame({
        "sales_line_id": [f"SIM-STORE-LINE-{i + 1:07d}" for i in range(STORE_LINES)],
        "order_id": store_order_ids,
        "transaction_timestamp": store_dates + pd.to_timedelta(rng.integers(36_000, 75_600, STORE_LINES), unit="s"),
        "date_key": pd.Series(store_dates).dt.strftime("%Y%m%d").astype(int),
        "customer_id": np.repeat(order_customer, 3),
        "product_id": store_products,
        "location_id": np.repeat(order_store, 3),
        "channel_id": "SALES_STORE",
        "campaign_id": None,
        "quantity": store_qty,
        "unit_price": store_price,
        "discount_rate": store_discount,
        "net_revenue": store_net,
        "cogs": store_cogs,
        "fulfilment_cost": store_fulfil,
        "is_return": store_qty < 0,
        "source_system": "Simulated extension",
        "source_record_id": [f"SIM-STORE-LINE-{i + 1:07d}" for i in range(STORE_LINES)],
        "is_simulated": True,
        "simulation_version": SIM_VERSION,
    })
    fact_sales = pd.concat([public_sales, store_fact], ignore_index=True)

    spend_rows = []
    for campaign in dim_campaign.itertuples(index=False):
        for dt in pd.date_range(campaign.start_date, campaign.end_date, freq="D"):
            impressions = int(rng.integers(8_000, 55_000))
            ctr = rng.uniform(0.012, 0.055)
            clicks = max(1, int(impressions * ctr))
            cpc = rng.uniform(0.35, 1.75)
            spend = round(clicks * cpc, 2)
            spend_rows.append((f"SPEND-{campaign.campaign_id}-{dt:%Y%m%d}", int(dt.strftime("%Y%m%d")), campaign.campaign_id,
                               campaign.channel_id, "COUNTRY-united-kingdom", impressions, clicks, spend))
    fact_campaign_spend = pd.DataFrame(spend_rows, columns=["spend_id", "date_key", "campaign_id", "channel_id", "location_id", "impressions", "clicks", "spend"])
    fact_campaign_spend["source_system"] = "Simulated extension"
    fact_campaign_spend["source_record_id"] = fact_campaign_spend["spend_id"]
    fact_campaign_spend["is_simulated"] = True
    fact_campaign_spend["simulation_version"] = SIM_VERSION

    dates = pd.DataFrame({"full_date": pd.date_range(min_date, max_date, freq="D")})
    dates["date_key"] = dates["full_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["full_date"].dt.year
    dates["quarter"] = "Q" + dates["full_date"].dt.quarter.astype(str)
    dates["month_number"] = dates["full_date"].dt.month
    dates["month_name"] = dates["full_date"].dt.month_name()
    dates["month_start"] = dates["full_date"].dt.to_period("M").dt.to_timestamp()
    dates["week_number"] = dates["full_date"].dt.isocalendar().week.astype(int)
    dates["day_of_week_number"] = dates["full_date"].dt.dayofweek + 1
    dates["day_name"] = dates["full_date"].dt.day_name()
    dates["is_weekend"] = dates["day_of_week_number"] >= 6
    dim_date = dates[["date_key", "full_date", "year", "quarter", "month_number", "month_name", "month_start", "week_number", "day_of_week_number", "day_name", "is_weekend"]]

    outputs = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_date": dim_date,
        "dim_location": dim_location,
        "dim_channel": dim_channel,
        "dim_campaign": dim_campaign,
        "fact_sales": fact_sales,
        "fact_web_sessions": fact_web_sessions,
        "fact_campaign_spend": fact_campaign_spend,
        "quarantine_source_rows": quarantine,
    }
    for name, frame in outputs.items():
        frame.to_csv(PROCESSED / f"{name}.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")

    sales = fact_sales.copy()
    sales["month"] = pd.to_datetime(sales["transaction_timestamp"]).dt.to_period("M").dt.to_timestamp()
    sales["gross_margin"] = sales["net_revenue"] - sales["cogs"]
    monthly = sales.groupby("month", as_index=False).agg(
        net_revenue=("net_revenue", "sum"),
        cogs=("cogs", "sum"),
        gross_margin=("gross_margin", "sum"),
        fulfilment_cost=("fulfilment_cost", "sum"),
    )
    completed = sales.loc[(~sales["is_return"]) & (sales["net_revenue"] > 0)]
    monthly_orders = completed.groupby("month")["order_id"].nunique()
    monthly_customers = completed.loc[completed["customer_id"].notna()].groupby("month")["customer_id"].nunique()
    monthly["orders"] = monthly["month"].map(monthly_orders).fillna(0).astype(int)
    monthly["active_customers"] = monthly["month"].map(monthly_customers).fillna(0).astype(int)
    spend_month = fact_campaign_spend.assign(month=pd.to_datetime(fact_campaign_spend["date_key"].astype(str)).dt.to_period("M").dt.to_timestamp()).groupby("month")["spend"].sum()
    monthly["campaign_spend"] = monthly["month"].map(spend_month).fillna(0)
    monthly["contribution_margin"] = monthly["gross_margin"] - monthly["fulfilment_cost"] - monthly["campaign_spend"]
    monthly["aov"] = monthly["net_revenue"] / monthly["orders"]
    monthly["revenue_mom_pct"] = monthly["net_revenue"].pct_change()

    positive_identified = sales.loc[(~sales["is_return"]) & sales["customer_id"].notna() & (sales["net_revenue"] > 0)].copy()
    positive_identified["month"] = positive_identified["month"].dt.to_period("M").dt.to_timestamp()
    active_by_month = positive_identified.groupby("month")["customer_id"].agg(lambda s: set(s))
    retention_rows = []
    months = sorted(active_by_month.index)
    for idx, month in enumerate(months):
        current = active_by_month[month]
        previous = active_by_month[months[idx - 1]] if idx else set()
        retained = len(current & previous)
        retention_rows.append((month, len(current), len(previous), retained, retained / len(previous) if previous else np.nan))
    retention = pd.DataFrame(retention_rows, columns=["month", "active_customers", "prior_month_customers", "retained_customers", "retention_rate"])

    rfm = positive_identified.groupby("customer_id", as_index=False).agg(last_purchase=("transaction_timestamp", "max"), frequency=("order_id", "nunique"),
        monetary=("net_revenue", "sum"), gross_margin=("gross_margin", "sum"), fulfilment_cost=("fulfilment_cost", "sum"))
    rfm["recency_days"] = (pd.Timestamp(max_date) + pd.Timedelta(days=1) - pd.to_datetime(rfm["last_purchase"]).dt.normalize()).dt.days
    rfm["observed_historical_clv"] = rfm["gross_margin"] - rfm["fulfilment_cost"]
    rfm["r_score"] = score_quintiles(rfm["recency_days"], higher_is_better=False)
    rfm["f_score"] = score_quintiles(rfm["frequency"], higher_is_better=True)
    rfm["m_score"] = score_quintiles(rfm["monetary"], higher_is_better=True)
    rfm["rfm_segment"] = rfm_segments(rfm)

    store_sales = sales.loc[sales["channel_id"] == "SALES_STORE"].merge(
        stores[["location_id", "store_format"]], on="location_id", how="left"
    )
    # Store peer variance is defined at one store-month grain. The previous
    # category-grain calculation averaged category rows and understated the
    # peer baseline. Category performance remains available from fact_sales
    # joined to dim_product; this table is reserved for store comparison.
    product_store = store_sales.groupby(
        ["month", "location_id", "store_format"], as_index=False
    ).agg(
        net_revenue=("net_revenue", "sum"),
        gross_margin=("gross_margin", "sum"),
        orders=("order_id", "nunique"),
        return_lines=("is_return", "sum"),
    )
    peer = product_store.groupby(["month", "store_format"])["net_revenue"].transform("mean")
    product_store["peer_average_revenue"] = peer
    product_store["store_variance"] = product_store["net_revenue"] - peer
    product_store["store_variance_pct"] = np.where(
        peer != 0, product_store["store_variance"] / peer, np.nan
    )

    session_campaign = fact_web_sessions.loc[fact_web_sessions["campaign_id"].notna()].groupby("campaign_id", as_index=False).agg(sessions=("session_id", "nunique"), conversions=("converted", "sum"))
    campaign_spend = fact_campaign_spend.groupby("campaign_id", as_index=False).agg(impressions=("impressions", "sum"), clicks=("clicks", "sum"), spend=("spend", "sum"))
    attributed = public_sales.loc[public_sales["campaign_id"].notna()].groupby("campaign_id", as_index=False).agg(attributed_revenue=("net_revenue", "sum"), attributed_cogs=("cogs", "sum"), attributed_orders=("order_id", "nunique"))
    campaign = dim_campaign[["campaign_id", "campaign_name", "channel_id"]].merge(campaign_spend, on="campaign_id", how="left").merge(session_campaign, on="campaign_id", how="left").merge(attributed, on="campaign_id", how="left").fillna(0)
    campaign["attributed_gross_margin"] = campaign["attributed_revenue"] - campaign["attributed_cogs"]
    campaign["ctr"] = campaign["clicks"] / campaign["impressions"]
    campaign["conversion_rate"] = campaign["conversions"] / campaign["sessions"]
    campaign["roas"] = campaign["attributed_revenue"] / campaign["spend"]
    campaign["roi"] = (campaign["attributed_gross_margin"] - campaign["spend"]) / campaign["spend"]
    campaign["cac"] = campaign["spend"] / campaign["conversions"].replace(0, np.nan)

    metric_outputs = {
        "monthly_performance": monthly,
        "customer_retention": retention,
        "customer_rfm": rfm,
        "product_store_performance": product_store,
        "campaign_efficiency": campaign,
    }
    for name, frame in metric_outputs.items():
        frame.to_csv(TABLES / f"{name}.csv", index=False, date_format="%Y-%m-%d")

    validation = {
        "status": "pass",
        "raw_sha256": raw_hash,
        "raw_rows": raw_rows,
        "raw_columns": len(raw.columns),
        "exact_duplicate_rows_removed": duplicate_rows,
        "quarantined_rows": len(quarantine),
        "public_fact_rows": len(public_sales),
        "simulated_store_rows": len(store_fact),
        "fact_sales_rows": len(fact_sales),
        "web_session_rows": len(fact_web_sessions),
        "campaign_spend_rows": len(fact_campaign_spend),
        "unique_sales_line_ids": bool(fact_sales["sales_line_id"].is_unique),
        "unique_session_ids": bool(fact_web_sessions["session_id"].is_unique),
        "unique_spend_ids": bool(fact_campaign_spend["spend_id"].is_unique),
        "provenance_nulls": int(fact_sales[["source_system", "source_record_id", "is_simulated"]].isna().sum().sum()),
        "simulation_labels_missing": int(fact_sales.loc[fact_sales["is_simulated"], "simulation_version"].isna().sum()),
        "revenue_arithmetic_max_abs_error": float((fact_sales["net_revenue"] - fact_sales["quantity"] * fact_sales["unit_price"] * (1 - fact_sales["discount_rate"])).abs().max()),
        "sales_product_orphans": int((~fact_sales["product_id"].isin(dim_product["product_id"])).sum()),
        "sales_location_orphans": int((~fact_sales["location_id"].isin(dim_location["location_id"])).sum()),
        "sales_channel_orphans": int((~fact_sales["channel_id"].isin(dim_channel["channel_id"])).sum()),
        "anonymous_customer_rows": int(fact_sales["customer_id"].isna().sum()),
        "rfm_anonymous_rows": int(rfm["customer_id"].isna().sum()),
    }
    hard_fail = [
        not validation["unique_sales_line_ids"], not validation["unique_session_ids"], not validation["unique_spend_ids"],
        validation["provenance_nulls"] != 0, validation["simulation_labels_missing"] != 0,
        validation["revenue_arithmetic_max_abs_error"] > 0.01, validation["sales_product_orphans"] != 0,
        validation["sales_location_orphans"] != 0, validation["sales_channel_orphans"] != 0,
        validation["rfm_anonymous_rows"] != 0,
    ]
    if any(hard_fail):
        validation["status"] = "fail"
    (LOGS / "validation-results.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    return validation


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "pass" else 1)
