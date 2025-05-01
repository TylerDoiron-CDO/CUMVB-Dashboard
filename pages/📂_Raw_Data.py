# pages/📂_Raw_Data.py

import streamlit as st
import pandas as pd
import os
from functions import Overall_Data_Load

st.set_page_config(page_title="📂 Raw Data Viewer", layout="wide")
st.title("📂 Raw Data Viewer — For Exploratory Analysis")

# -------------------------------
# Section: Overall Data
# -------------------------------
st.header("📊 Overall Data")

force_refresh = st.session_state.get("reset_cache_overall", False)
with st.spinner("🔄 Loading Overall Data..."):
    overall_df = Overall_Data_Load.load_preprocessed_overall_data(force_rebuild=force_refresh)

if overall_df.empty:
    st.warning("⚠️ No overall data found or processed.")
else:
    with st.expander("🔎 Filter Overall Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(overall_df["Season"].dropna().unique())
        teams = sorted(overall_df["Team"].dropna().unique())
        homes = sorted(overall_df["Home"].dropna().unique())
        aways = sorted(overall_df["Away"].dropna().unique())
        search_team = col5.text_input("Search Opponent")

        o_seasons = col1.multiselect("Season", options=seasons)
        o_teams = col2.multiselect("Team", options=teams)
        o_home = col3.multiselect("Home", options=homes)
        o_away = col4.multiselect("Away", options=aways)

    filtered_df = overall_df.copy()
    if o_seasons:
        filtered_df = filtered_df[filtered_df["Season"].isin(o_seasons)]
    if o_teams:
        filtered_df = filtered_df[filtered_df["Team"].isin(o_teams)]
    if o_home:
        filtered_df = filtered_df[filtered_df["Home"].isin(o_home)]
    if o_away:
        filtered_df = filtered_df[filtered_df["Away"].isin(o_away)]
    if search_team and "Opponent" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Opponent"].str.contains(search_team, case=False, na=False)]

    st.success(f"✅ {filtered_df.shape[0]} overall records shown")
    latest_date = pd.to_datetime(filtered_df["Date"], errors='coerce').dropna().max()
    if pd.notnull(latest_date):
        st.markdown(f"**🗓️ Data current as of:** {latest_date.date()}")

    st.dataframe(filtered_df)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download CSV", filtered_df.to_csv(index=False).encode("utf-8"), "overall_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()
            else:
                st.info("ℹ️ No overall cache found.")
        st.caption("⚠️ Only use if source data changed.")

st.markdown("---")
st.caption("Developed by Astute Innovations — Streamlit analytics platform • Crandall Chargers Volleyball © 2025")
