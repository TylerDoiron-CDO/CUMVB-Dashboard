import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📄 Test Historical Data", layout="wide")
st.title("📄 Test: Historical Overall Data Viewer")
st.markdown("This page tests reading the `Historical Overall Data.csv` file from `/mnt/data` and displaying it.")

# -------------------------------
# Load Historical File
# -------------------------------
file_path = "/mnt/data/Historical Overall Data.csv"

if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)
        st.success(f"✅ Loaded {df.shape[0]} rows from historical data.")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
else:
    st.warning("⚠️ File not found at /mnt/data/Historical Overall Data.csv")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Test utility for verifying historical data ingestion.")
