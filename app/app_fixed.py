import streamlit as st 
import pandas as pd 
import numpy as np from pathlib 
import Path 
import plotly.express as px
BASE_DIR = Path(file).resolve().parent DATA_DIR = BASE_DIR / "data" DATA_FILE = DATA_DIR / "sample_otc_collections.csv"
st.set_page_config(page_title="FiduciaSimplx — OK Tax Tracker (Prototype)", layout="wide")
@st.cache() def load_sample_data(path: Path): df = pd.read_csv(path, parse_dates=["date"])
