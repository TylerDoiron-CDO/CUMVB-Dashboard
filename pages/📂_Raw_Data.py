import streamlit as st
import pandas as pd
import os
from functions import Athlete_Data_Load, Overall_Data_Load

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="📂 Raw Data Viewer", layout="wide")
st.title("📂 Raw Data Viewer — For Exploratory Analysis")
st.markdown("This page combines the full processed Athlete Data and Overall Data for deep-dive inspection and exploration.")
st.markdown("---")

# -------------------------------
# Section 1: Athlete Data
# -------------------------------
st.header("🏐 Athlete Data")

force_refresh = st.session_state.get("reset_cache_athlete", False)
with st.spinner("🔄 Loading Athlete Data..."):
    athlete_df = Athlete_Data_Load.load_preprocessed_athlete_data(force_rebuild=force_refresh)

if athlete_df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    with st.expander("🔎 Filter Athlete Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(athlete_df["Season"].dropna().unique())
        teams = sorted(athlete_df["TEAM"].dropna().unique())
        homes = sorted(athlete_df["Home"].dropna().unique())
        aways = sorted(athlete_df["Away"].dropna().unique())
        names = sorted(athlete_df["Athlete"].dropna().unique()) if "Athlete" in athlete_df.columns else []

        s_seasons = col1.multiselect("Season", options=seasons)
        s_teams = col2.multiselect("TEAM", options=teams)
        s_home = col3.multiselect("Home", options=homes)
        s_away = col4.multiselect("Away", options=aways)
        s_name = col5.text_input("Search Athlete")

    filtered_athlete = athlete_df.copy()
    if s_seasons:
        filtered_athlete = filtered_athlete[filtered_athlete["Season"].isin(s_seasons)]
    if s_teams:
        filtered_athlete = filtered_athlete[filtered_athlete["TEAM"].isin(s_teams)]
    if s_home:
        filtered_athlete = filtered_athlete[filtered_athlete["Home"].isin(s_home)]
    if s_away:
        filtered_athlete = filtered_athlete[filtered_athlete["Away"].isin(s_away)]
    if s_name and "Athlete" in filtered_athlete.columns:
        filtered_athlete = filtered_athlete[filtered_athlete["Athlete"].str.contains(s_name, case=False, na=False)]

    st.success(f"✅ {filtered_athlete.shape[0]} athlete records shown")
    latest_athlete_date = pd.to_datetime(filtered_athlete["Date"], errors="coerce").dropna().max()
    if pd.notnull(latest_athlete_date):
        st.markdown(f"**🗓️ Athlete data current as of:** {latest_athlete_date.date()}")

    st.dataframe(filtered_athlete)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.download_button("💾 Download Athlete CSV", filtered_athlete.to_csv(index=False).encode("utf-8"), "athlete_data.csv", "text/csv")
    with c2:
        if st.button("🔁 Reset Athlete Cache"):
            if os.path.exists(Athlete_Data_Load.CACHE_FILE):
                os.remove(Athlete_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_athlete"] = True
                st.rerun()
            else:
                st.info("ℹ️ No athlete cache found.")
        st.caption("⚠️ Only use if source athlete data changed.")

st.markdown("---")

# -------------------------------
# Section 2: Overall Data
# -------------------------------
st.header("📊 Overall Data")

force_refresh_overall = st.session_state.get("reset_cache_overall", False)
with st.spinner("🔄 Loading Overall Data..."):
    overall_df = Overall_Data_Load.load_preprocessed_overall_data(force_rebuild=force_refresh_overall)
    st.info(f"🔍 Total Overall Records: {overall_df.shape[0]}")
    st.info(f"📄 Historical Records Detected: {(overall_df['source_file'] == 'historical data').sum()}")
    st.info(f"🧾 Unique Seasons: {overall_df['Season'].unique()}")

if overall_df.empty:
    st.warning("⚠️ No overall data found or processed.")
else:
    with st.expander("🔎 Filter Overall Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(overall_df["Season"].dropna().unique())
        teams = sorted(overall_df["TEAM"].dropna().unique())
        homes = sorted(overall_df["Home"].dropna().unique())
        aways = sorted(overall_df["Away"].dropna().unique())
        teamnames = sorted(overall_df["Team"].dropna().unique()) if "Team" in overall_df.columns else []

        o_seasons = col1.multiselect("Season", options=seasons)
        o_teams = col2.multiselect("TEAM", options=teams)
        o_home = col3.multiselect("Home", options=homes)
        o_away = col4.multiselect("Away", options=aways)
        o_search = col5.text_input("Search Team Name")

    filtered_overall = overall_df.copy()
    if o_seasons:
        filtered_overall = filtered_overall[filtered_overall["Season"].isin(o_seasons)]
    if o_teams:
        filtered_overall = filtered_overall[filtered_overall["TEAM"].isin(o_teams)]
    if o_home:
        filtered_overall = filtered_overall[filtered_overall["Home"].isin(o_home)]
    if o_away:
        filtered_overall = filtered_overall[filtered_overall["Away"].isin(o_away)]
    if o_search and "Team" in filtered_overall.columns:
        filtered_overall = filtered_overall[filtered_overall["Team"].str.contains(o_search, case=False, na=False)]

    st.success(f"✅ {filtered_overall.shape[0]} overall records shown")
    latest_overall_date = pd.to_datetime(filtered_overall["Date"], errors="coerce").dropna().max()
    if pd.notnull(latest_overall_date):
        st.markdown(f"**🗓️ Overall data current as of:** {latest_overall_date.date()}")

    st.dataframe(filtered_overall)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.download_button("💾 Download Overall CSV", filtered_overall.to_csv(index=False).encode("utf-8"), "overall_data.csv", "text/csv")
    with c2:
        if st.button("🔁 Reset Overall Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()
            else:
                st.info("ℹ️ No overall cache found.")
        st.caption("⚠️ Only use if source overall data changed.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations — Advanced analytics powered by Streamlit • Crandall Chargers Volleyball © 2025")

