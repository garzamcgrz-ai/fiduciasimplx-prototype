import streamlit as st import pandas as pd import numpy as np from pathlib import Path import plotly.express as px
import streamlit as st 
import pandas as pd 
import numpy as np from pathlib 
import Path 
import streamlit as st

import pandas as pd

import numpy as np

from pathlib import Path

import plotly.express as px

BASE_DIR = Path(file).resolve().parent DATA_DIR = BASE_DIR / "data" DATA_FILE = DATA_DIR / "sample_otc_collections.csv"
st.set_page_config(page_title="FiduciaSimplx — OK Tax Tracker (Prototype)", layout="wide")
@st.cache() def load_sample_data(path: Path): df = pd.read_csv(path, parse_dates=["date"]) # normalize column names df.columns = [c.strip() for c in df.columns] # ensure expected columns exist if "amount" in df.columns: df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0) else: df["amount"] = 0.0 if "date" not in df.columns: df["date"] = pd.NaT df = df.sort_values("date") return df
Load data (if missing file, show error)
try: df = load_sample_data(DATA_FILE) except FileNotFoundError: st.error(f"Data file not found: {DATA_FILE}. Make sure data/sample_otc_collections.csv exists.") st.stop()
Sidebar controls
st.sidebar.header("Filters") min_date = df["date"].min() max_date = df["date"].max() if pd.isna(min_date) or pd.isna(max_date): min_date = pd.to_datetime("2020-01-01") max_date = pd.to_datetime("2025-12-31")
date_range = st.sidebar.date_input("Date range", [min_date.date(), max_date.date()]) start_date = pd.to_datetime(date_range[0]) end_date = pd.to_datetime(date_range[1])
Category filter
if "category" in df.columns: categories = sorted(df["category"].dropna().unique().tolist()) selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories) else: selected_categories = []
Aggregation and Top-N controls
agg_option = st.sidebar.selectbox("Aggregate by", ["Daily", "Weekly", "Monthly"]) top_n = st.sidebar.number_input("Top N for tables/charts", min_value=3, max_value=50, value=10, step=1)
st.sidebar.markdown("---") if st.sidebar.button("Reset filters"): st.experimental_rerun()
Apply filters
df_filtered = df.copy() df_filtered = df_filtered[(df_filtered["date"] >= start_date) & (df_filtered["date"] <= end_date)] if "category" in df.columns and selected_categories: df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]
Derived aggregation column
if agg_option == "Daily": df_filtered["period"] = df_filtered["date"].dt.to_period("D").dt.to_timestamp() elif agg_option == "Weekly": df_filtered["period"] = df_filtered["date"].dt.to_period("W").dt.start_time else: df_filtered["period"] = df_filtered["date"].dt.to_period("M").dt.to_timestamp()
KPIs
total_sales = df_filtered["amount"].sum() tx_count = len(df_filtered) avg_sale = total_sales / tx_count if tx_count > 0 else 0.0
percent change vs previous period (same span length)
span_days = (end_date - start_date).days + 1 prev_start = start_date - pd.Timedelta(days=span_days) prev_end = start_date - pd.Timedelta(days=1) prev_df = df[(df["date"] >= prev_start) & (df["date"] <= prev_end)] prev_sales = prev_df["amount"].sum() if prev_sales == 0: sales_change_pct = None else: sales_change_pct = (total_sales - prev_sales) / prev_sales * 100.0
Layout: KPI row
st.title("FiduciaSimplx — OK Tax Tracker (Prototype)") kpi1, kpi2, kpi3, kpi4 = st.columns([2,2,2,2]) kpi1.metric("Total sales", f"${total_sales:,.2f}") kpi2.metric("Transactions", f"{tx_count:,}") kpi3.metric("Average sale", f"${avg_sale:,.2f}") if sales_change_pct is None: kpi4.metric("Change vs prev period", "N/A") else: kpi4.metric("Change vs prev period", f"{sales_change_pct:+.1f}%")
st.markdown("---")
Time series: sum by period
ts = df_filtered.groupby("period", as_index=False)["amount"].sum() if ts.empty: st.warning("No data for selected filters.") else: fig_ts = px.line(ts, x="period", y="amount", title="Sales over time", markers=True) fig_ts.update_layout(yaxis_title="Sales ($)", xaxis_title="Period") st.plotly_chart(fig_ts, use_container_width=True)
Two columns: bar chart by category and top-N table
col1, col2 = st.columns([2,1])
with col1: if "category" in df.columns: cat_agg = df_filtered.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False) top_cats = cat_agg.head(top_n) fig_cat = px.bar(top_cats, x="category", y="amount", title=f"Sales by category (top {min(len(top_cats), top_n)})") fig_cat.update_layout(xaxis_title="Category", yaxis_title="Sales ($)", xaxis={'categoryorder':'total descending'}) st.plotly_chart(fig_cat, use_container_width=True) else: st.info("No 'category' column available to build category chart.")
with col2: st.subheader(f"Top {top_n} items/counties") if "item" in df_filtered.columns: top_items = df_filtered.groupby("item", as_index=False)["amount"].sum().sort_values("amount", ascending=False).head(top_n) st.table(top_items.reset_index(drop=True)) elif "county" in df_filtered.columns: top_counties = df_filtered.groupby("county", as_index=False)["amount"].sum().sort_values("amount", ascending=False).head(top_n) st.table(top_counties.reset_index(drop=True)) else: st.write("No 'item' or 'county' columns available for Top-N table.")
st.markdown("---")
Latest feed
st.subheader("Latest feed") if "date" in df.columns: feed = df.sort_values("date", ascending=False).head(10) st.table(feed.head(10)) else: st.write("No date column — cannot show feed.")
Download filtered CSV
def convert_df_to_csv(df_input): return df_input.to_csv(index=False).encode("utf-8")
csv_bytes = convert_df_to_csv(df_filtered) st.download_button(label="Download filtered CSV", data=csv_bytes, file_name="filtered_otc_collections.csv", mime="text/csv")