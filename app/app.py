import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
st.set_page_config(page_title="FiduciaSimplx — OK Tax Tracker (Prototype)", layout="wide")

@st.cache_data(ttl=3600)
def
():
    # load the small sample CSV included in the repo
    sales = pd.read_csv(DATA_DIR / "sample_otc_collections.csv", parse_dates=["date"])
    # simple mock feed from the same file for demo purpose
    feed = sales.sort_values("date", ascending=False).head(10).rename(columns={"category":"title"})
    # tiny geojson fallback (not required for minimal deploy)
    counties_geo = {"type":"FeatureCollection","features":[]}
    return sales, feed, counties_geo

sales_df, feed_df, counties_geo = load_sample_data()

def():
    def
    (df, col_name):
        last = df[df["category"] == col_name].sort_values("date").tail(1)
        if last.empty:
            return {"value": 0, "pct_change": 0}
        val = float(last["amount"].values[0])
        prev = df[df["category"] == col_name].sort_values("date").tail(2)
        prev_val = float(prev["amount"].values[0]) if len(prev) > 1 else val
        pct = ((val - prev_val) / prev_val * 100) if prev_val != 0 else 0
        return {"value": val, "pct_change": pct}
    categories = ["Sales", "Individual Income", "Business/Franchise", "Property", "Trusts"]
    return {cat: agg_latest(sales_df, cat) for cat in categories}

def
(latest_values):
    cols = st.columns(len(latest_values))
    for c, (label, v) in zip(cols, latest_values.items()):
        delta = v["pct_change"]
        sign = "▲" if delta >= 0 else "▼"
        c.metric(label=label, value=f"${v['value']:,.0f}", delta=f"{sign} {abs(delta):.1f}%")

st.title("FiduciaSimplx — Oklahoma Tax Tracker (Prototype)")
st.markdown("Prototype: public demo — not tax advice. Data is sample/mock for testing purposes.")

latest = compute_latest_metrics()
render_ticker(latest)

left, right = st.columns([1,2])

with left:
    st.header("Live feed (sample)")
    for _, row in feed_df.iterrows():
        ts = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        st.write(f"{ts} — {row.get('title','Update')} — Source: {row.get('source','OTC')}")

with right:
    st.header("Charts (sample)")
    sales_ts = sales_df[sales_df["category"] == "Sales"].sort_values("date")
    if not sales_ts.empty:
        fig1 = px.line(sales_ts, x="date", y="amount", title="Sales Tax Collections (sample)")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No Sales sample data available.")

    st.subheader("Simple projection (sample)")
    now = pd.Timestamp.now()
    this_month = sales_df[sales_df["date"].dt.month == now.month]
    if not this_month.empty:
        partial = this_month.groupby("category")["amount"].sum().reset_index()
        days_so_far = now.day
        days_in_month = (now + pd.offsets.MonthEnd(0)).day
        partial["projected_month"] = partial["amount"] / max(days_so_far,1) * days_in_month
        fig3 = px.bar(partial, x="category", y="projected_month", title="Projected month-end (sample)")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.write("No partial-month sample data available.")

st.markdown("---")
st.header("Subscribe (prototype)")
email = st.text_input("Email for alerts")
if st.button("Subscribe (prototype)"):
    if email and "@" in email:
        sub_file = DATA_DIR / "subscribers.csv"
        row = {"email": email, "timestamp": datetime.datetime.utcnow().isoformat()}
        df = pd.DataFrame([row])
        if sub_file.exists():
            df.to_csv(sub_file, mode="a", header=False, index=False)
        else:
            df.to_csv(sub_file, index=False)
        st.success("Thanks — subscribed (prototype).")
    else:
        st.error("Enter a valid email.")
st.write("Disclaimer: Prototype for demonstration only — not personalized tax advice.")
