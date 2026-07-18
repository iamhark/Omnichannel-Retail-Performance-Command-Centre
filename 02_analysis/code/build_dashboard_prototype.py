from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PROJECT = Path(__file__).resolve().parents[2]
TABLES = PROJECT / "02_analysis" / "outputs" / "tables"
OUT = PROJECT / "04_deliverables" / "review" / "2026-07-18-omnichannel-retail-dashboard-prototype-v1.pdf"
PAGE = (13.333 * inch, 7.5 * inch)
NAVY = colors.HexColor("#16324F")
TEAL = colors.HexColor("#2A9D8F")
AMBER = colors.HexColor("#E9C46A")
RED = colors.HexColor("#C94C4C")
PALE = colors.HexColor("#EFF4F6")
TEXT = colors.HexColor("#24323A")


def money(value: float) -> str:
    return f"£{value / 1_000_000:.2f}m" if abs(value) >= 1_000_000 else f"£{value:,.0f}"


def header(c: canvas.Canvas, page_title: str, page_number: int) -> None:
    w, h = PAGE
    c.setFillColor(NAVY)
    c.rect(0, h - 0.62 * inch, w, 0.62 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.38 * inch, h - 0.39 * inch, page_title)
    c.setFont("Helvetica", 9)
    c.drawRightString(w - 0.38 * inch, h - 0.36 * inch, f"Review prototype | Page {page_number}/4")
    c.setFillColor(colors.HexColor("#52646F"))
    c.setFont("Helvetica", 7.5)
    c.drawString(0.38 * inch, 0.18 * inch, "Business-case data: UCI Online Retail public transactions plus deterministic simulated omnichannel extensions.")


def card(c: canvas.Canvas, x: float, y: float, width: float, title: str, value: str, accent=TEAL) -> None:
    c.setFillColor(PALE)
    c.roundRect(x, y, width, 0.72 * inch, 6, fill=1, stroke=0)
    c.setFillColor(accent)
    c.rect(x, y, 0.06 * inch, 0.72 * inch, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#52646F"))
    c.setFont("Helvetica", 8)
    c.drawString(x + 0.15 * inch, y + 0.49 * inch, title)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(x + 0.15 * inch, y + 0.18 * inch, value)


def bar_chart(c: canvas.Canvas, x: float, y: float, width: float, height: float, labels: list[str], values: list[float], title: str, palette=None, value_format: str = "number") -> None:
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y + height + 0.12 * inch, title)
    max_value = max(abs(v) for v in values) or 1
    baseline = y + (height / 2 if min(values) < 0 else 0)
    c.setStrokeColor(colors.HexColor("#CBD5DA"))
    c.line(x, baseline, x + width, baseline)
    gap = width / max(len(values), 1)
    bar_w = gap * 0.58
    for i, (label, value) in enumerate(zip(labels, values)):
        bx = x + i * gap + (gap - bar_w) / 2
        scale_height = (height / 2 if min(values) < 0 else height) * abs(value) / max_value
        by = baseline if value >= 0 else baseline - scale_height
        color = palette[i] if palette else (TEAL if value >= 0 else RED)
        c.setFillColor(color)
        c.rect(bx, by, bar_w, scale_height, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#52646F"))
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(bx + bar_w / 2, y - 0.11 * inch, label[:16])
        c.setFont("Helvetica-Bold", 7)
        label_value = f"{value:.1%}" if value_format == "percent" else f"{0 if abs(value) < 0.5 else value:,.0f}"
        c.drawCentredString(bx + bar_w / 2, by + scale_height + (0.04 * inch if value >= 0 else -0.10 * inch), label_value)


def build() -> None:
    monthly = pd.read_csv(TABLES / "monthly_performance.csv", parse_dates=["month"])
    rfm = pd.read_csv(TABLES / "customer_rfm.csv")
    store = pd.read_csv(TABLES / "product_store_performance.csv")
    campaign = pd.read_csv(TABLES / "campaign_efficiency.csv")
    retention = pd.read_csv(TABLES / "customer_retention.csv", parse_dates=["month"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    w, h = PAGE

    header(c, "Executive performance", 1)
    totals = {"revenue": monthly.net_revenue.sum(), "gm": monthly.gross_margin.sum(), "cm": monthly.contribution_margin.sum()}
    complete_retention = retention[(retention.month >= "2011-01-01") & (retention.month < "2011-12-01")].retention_rate.mean()
    for i, (title, value, color) in enumerate([
        ("Net revenue", money(totals["revenue"]), TEAL), ("Gross margin", money(totals["gm"]), TEAL),
        ("Contribution margin", money(totals["cm"]), AMBER), ("Complete-month retention", f"{complete_retention:.1%}", TEAL)
    ]):
        card(c, 0.4 * inch + i * 3.2 * inch, h - 1.55 * inch, 2.85 * inch, title, value, color)
    bar_chart(c, 0.55 * inch, 0.75 * inch, 7.3 * inch, 3.25 * inch,
              [d.strftime("%b-%y") + ("*" if d == monthly.month.max() else "") for d in monthly.month], (monthly.net_revenue / 1000).tolist(), "Monthly net revenue (£000; *partial month)")
    bar_chart(c, 8.35 * inch, 0.75 * inch, 4.35 * inch, 3.25 * inch,
              [d.strftime("%b-%y") + ("*" if d == monthly.month.max() else "") for d in monthly.month], (monthly.contribution_margin / 1000).tolist(), "Monthly contribution margin (£000; *partial month)", [AMBER] * len(monthly))
    c.showPage()

    header(c, "Customer and retention", 2)
    seg = rfm.groupby("rfm_segment", as_index=False).agg(customers=("customer_id", "count"), monetary=("monetary", "sum"), avg_clv=("observed_historical_clv", "mean")).sort_values("monetary", ascending=False)
    champions = seg.loc[seg.rfm_segment == "Champions"].iloc[0]
    risk_count = int(seg.loc[seg.rfm_segment.isin(["At Risk", "Lost"]), "customers"].sum())
    for i, (title, value, color) in enumerate([
        ("Identified customers", f"{len(rfm):,}", TEAL), ("Champions", f"{int(champions.customers):,}", TEAL),
        ("Champion value share", f"{champions.monetary / seg.monetary.sum():.1%}", AMBER), ("At Risk + Lost", f"{risk_count:,}", RED)
    ]):
        card(c, 0.4 * inch + i * 3.2 * inch, h - 1.55 * inch, 2.85 * inch, title, value, color)
    bar_chart(c, 0.6 * inch, 0.85 * inch, 6.0 * inch, 3.35 * inch, seg.rfm_segment.tolist(), seg.customers.tolist(), "Customers by RFM segment")
    bar_chart(c, 6.95 * inch, 0.85 * inch, 5.75 * inch, 3.35 * inch, seg.rfm_segment.tolist(), (seg.monetary / 1000).tolist(), "Monetary value by RFM segment (£000)", [TEAL, RED, AMBER, TEAL, colors.HexColor("#78909C"), RED])
    c.showPage()

    header(c, "Product and store operations", 3)
    store_total = store.groupby(["location_id", "store_format"], as_index=False).agg(revenue=("net_revenue", "sum"), margin=("gross_margin", "sum"), variance=("store_variance", "sum"))
    best = store_total.loc[store_total.variance.idxmax()]
    worst = store_total.loc[store_total.variance.idxmin()]
    for i, (title, value, color) in enumerate([
        ("Simulated stores", f"{len(store_total)}", AMBER), ("Top peer variance", money(best.variance), TEAL),
        ("Lowest peer variance", money(worst.variance), RED), ("Store revenue", money(store_total.revenue.sum()), TEAL)
    ]):
        card(c, 0.4 * inch + i * 3.2 * inch, h - 1.55 * inch, 2.85 * inch, title, value, color)
    labels = [s.replace("STORE-", "").replace("-CITY", "").title() for s in store_total.location_id]
    bar_chart(c, 0.65 * inch, 0.85 * inch, 7.4 * inch, 3.35 * inch, labels, store_total.variance.tolist(), "Store variance versus same-format peer (£)")
    category = store.groupby("category", as_index=False).agg(revenue=("net_revenue", "sum"), margin=("gross_margin", "sum")).sort_values("revenue", ascending=False)
    bar_chart(c, 8.35 * inch, 0.85 * inch, 4.3 * inch, 3.35 * inch, category.category.tolist(), (category.margin / 1000).tolist(), "Gross margin by category (£000)", [TEAL] * len(category))
    c.showPage()

    header(c, "Marketing and channel efficiency", 4)
    channel = campaign.groupby("channel_id", as_index=False).agg(spend=("spend", "sum"), revenue=("attributed_revenue", "sum"), gm=("attributed_gross_margin", "sum"), conversions=("conversions", "sum"))
    channel["roi"] = (channel.gm - channel.spend) / channel.spend
    channel["cac"] = channel.spend / channel.conversions
    channel["roas"] = channel.revenue / channel.spend
    for i, row in channel.iterrows():
        card(c, 0.55 * inch + i * 4.25 * inch, h - 1.55 * inch, 3.85 * inch, row.channel_id.replace("MKT_", "").replace("_", " ").title(), f"ROI {row.roi:.1%} | CAC £{row.cac:,.0f}", TEAL if row.roi >= 0 else RED)
    bar_chart(c, 0.7 * inch, 0.9 * inch, 5.6 * inch, 3.3 * inch, channel.channel_id.str.replace("MKT_", "").str.replace("_", " ").tolist(), channel.roi.tolist(), "Campaign ROI by channel", value_format="percent")
    bar_chart(c, 6.7 * inch, 0.9 * inch, 5.65 * inch, 3.3 * inch, channel.channel_id.str.replace("MKT_", "").str.replace("_", " ").tolist(), channel.cac.tolist(), "Customer acquisition cost (£)", [TEAL, TEAL, RED])
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
