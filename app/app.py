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

@st.cache()
def load_sample_data():
    # load the small sample CSV included in the repo
    sales = pd.read_csv(DATA_DIR / "sample_otc_collections.csv", parse_dates=["date"])

    # simple mock feed from the same CSV for the prototype
    feed = sales.copy()

    # mock counties_geo (use a real GeoJSON file if available in data/)
    counties_geo = {"type": "FeatureCollection", "features": []}

    return sales, feed, counties_geo

sales_df, feed_df, counties_geo = load_sample_data()

st.title("FiduciaSimplx — OK Tax Tracker (Prototype)")
st.write("Sample sales rows:")
st.dataframe(sales_df.head())
