import streamlit as st
import pandas as pd
import os
from functions import Athlete_Data_Load

st.set_page_config(page_title="📂 Raw Data", layout="wide")
st.title("📂 Raw Athlete Data Viewer")
st.markdown("Displays all processed athlete-level data from match files and historical records.")
st.markdown("---")

with st.spinner("🔄 Loading and processing Athlete Data..."):
    df = Athlete_Data_Load.load_preprocessed_athlete_data()

if df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    st.success(f"✅ {df.shape[0]} records loaded")

    latest_date = pd.to_datetime(df["Date"], errors="coerce").dropna().max()
    if pd.notnull(latest_date):
        st.markdown(f"**🗓️ Data current as of:** {latest_date.date()}")

    st.dataframe(df)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download CSV", df.to_csv(index=False).encode("utf-8"), "athlete_data_processed.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Cache"):
            if os.path.exists(Athlete_Data_Load.CACHE_FILE):
                os.remove(Athlete_Data_Load.CACHE_FILE)
                st.warning("⚠️ Cache cleared. Rebuilding now.")
                st.rerun()
            else:
                st.info("ℹ️ No cache file to delete.")
        st.caption("⚠️ Only use if underlying data has changed.")

st.markdown("---")
st.caption("Developed by Astute Innovations — Powered by Streamlit • Crandall Chargers Volleyball © 2025")
