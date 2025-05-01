import streamlit as st
import pandas as pd
import os
from functions import Athlete_Data_Load, Overall_Data_Load

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Raw Data Viewer", layout="wide")
st.title("📂 Raw Data Viewer - For Exploratory Analysis")
st.markdown("This page combines the full processed Athlete Data and Overall Data for deep-dive inspection and exploration.")
st.markdown("---")

# -------------------------------
# Section 1: Athlete Data
# -------------------------------
st.header("🏐 Athlete Data")

force_refresh = st.session_state.get("reset_cache_athlete", False)
with st.spinner("Loading Athlete Data..."):
    athlete_df = Athlete_Data_Load.load_preprocessed_athlete_data(force_rebuild=force_refresh)

if athlete_df.empty:
    st.warning("No athlete data found or processed.")
else:
    st.markdown("### Record Summary")
    st.write("Total athlete records:", athlete_df.shape[0])
    st.write("Historical rows:", (athlete_df["source_file"] == "historical data").sum())
    st.write("Seasons:", sorted(athlete_df["Season"].dropna().unique()))

    with st.expander("Filter Athlete Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        s1 = col1.multiselect("Season", sorted(athlete_df["Season"].dropna().unique()))
        s2 = col2.multiselect("TEAM", sorted(athlete_df["TEAM"].dropna().unique()))
        s3 = col3.multiselect("Home", sorted(athlete_df["Home"].dropna().unique()))
        s4 = col4.multiselect("Away", sorted(athlete_df["Away"].dropna().unique()))
        s5 = col5.text_input("Search Athlete")

    filtered = athlete_df.copy()
    if s1: filtered = filtered[filtered["Season"].isin(s1)]
    if s2: filtered = filtered[filtered["TEAM"].isin(s2)]
    if s3: filtered = filtered[filtered["Home"].isin(s3)]
    if s4: filtered = filtered[filtered["Away"].isin(s4)]
    if s5 and "Athlete" in filtered.columns:
        filtered = filtered[filtered["Athlete"].str.contains(s5, case=False, na=False)]

    st.success(f"Showing {filtered.shape[0]} athlete records")
    st.dataframe(filtered)

    col_dl1, col_reset1 = st.columns([3, 1])
    with col_dl1:
        st.download_button("Download Athlete CSV", filtered.to_csv(index=False), "athlete_data.csv")
    with col_reset1:
        if st.button("Reset Athlete Cache"):
            if os.path.exists(Athlete_Data_Load.CACHE_FILE):
                os.remove(Athlete_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_athlete"] = True
                st.rerun()

st.markdown("---")

# -------------------------------
# Section 2: Overall Data
# -------------------------------
st.header("📊 Overall Data")

force_refresh_overall = st.session_state.get("reset_cache_overall", False)
with st.spinner("Loading Overall Data..."):
    overall_df = Overall_Data_Load.load_preprocessed_overall_data(force_rebuild=force_refresh_overall)

if overall_df.empty:
    st.warning("No overall data found or processed.")
else:
    st.markdown("### Record Summary")
    st.write("Total overall records:", overall_df.shape[0])
    st.write("Historical rows:", (overall_df["source_file"] == "historical data").sum())
    st.write("Seasons:", sorted(overall_df["Season"].dropna().unique()))

    with st.expander("Filter Overall Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        s1 = col1.multiselect("Season", sorted(overall_df["Season"].dropna().unique()))
        s2 = col2.multiselect("TEAM", sorted(overall_df["TEAM"].dropna().unique()))
        s3 = col3.multiselect("Home", sorted(overall_df["Home"].dropna().unique()))
        s4 = col4.multiselect("Away", sorted(overall_df["Away"].dropna().unique()))
        s5 = col5.text_input("Search Team Name")

    filtered = overall_df.copy()
    if s1: filtered = filtered[filtered["Season"].isin(s1)]
    if s2: filtered = filtered[filtered["TEAM"].isin(s2)]
    if s3: filtered = filtered[filtered["Home"].isin(s3)]
    if s4: filtered = filtered[filtered["Away"].isin(s4)]
    if s5 and "Team" in filtered.columns:
        filtered = filtered[filtered["Team"].str.contains(s5, case=False, na=False)]

    st.success(f"Showing {filtered.shape[0]} overall records")
    st.dataframe(filtered)

    col_dl2, col_reset2 = st.columns([3, 1])
    with col_dl2:
        st.download_button("Download Overall CSV", filtered.to_csv(index=False), "overall_data.csv")
    with col_reset2:
        if st.button("Reset Overall Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()

st.markdown("---")
st.caption("Developed by Astute Innovations - Powered by Streamlit • Crandall Chargers Volleyball © 2025")
