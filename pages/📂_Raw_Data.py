import streamlit as st
import pandas as pd
import os
from functions import (
    Athlete_Data_Load,
    Overall_Data_Load,
    Rotation_Data_Load,
    Match_Data_Load  # Future use
)

st.set_page_config(page_title="📂 Raw Data Viewer", layout="wide")
st.title("📂 Raw Data Viewer — For Exploratory Analysis")
st.markdown("This page combines the full processed Athlete Data, Overall Data, Rotation Data, and additional scouting files for deep-dive inspection.")
st.markdown("---")

# -------------------------------
# Section 1: Athlete Data
# -------------------------------
st.header("🏐 Athlete Data")

force_refresh_athlete = st.session_state.get("reset_cache_athlete", False)
with st.spinner("🔄 Loading Athlete Data..."):
    athlete_df = Athlete_Data_Load.load_preprocessed_athlete_data(force_rebuild=force_refresh_athlete)

if athlete_df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    with st.expander("🔎 Filter Athlete Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(athlete_df["Season"].dropna().unique())
        teams = sorted(athlete_df["Team"].dropna().unique()) if "Team" in athlete_df.columns else []
        homes = sorted(athlete_df["Home"].dropna().unique())
        aways = sorted(athlete_df["Away"].dropna().unique())
        names = sorted(athlete_df["Athlete"].dropna().unique()) if "Athlete" in athlete_df.columns else []

        s_seasons = col1.multiselect("Athlete Season", options=seasons)
        s_teams = col2.multiselect("Athlete Team", options=teams)
        s_home = col3.multiselect("Athlete Home", options=homes)
        s_away = col4.multiselect("Athlete Away", options=aways)
        s_name = col5.text_input("Search Athlete")

    filtered_athlete = athlete_df.copy()
    if s_seasons:
        filtered_athlete = filtered_athlete[filtered_athlete["Season"].isin(s_seasons)]
    if s_teams:
        filtered_athlete = filtered_athlete[filtered_athlete["Team"].isin(s_teams)]
    if s_home:
        filtered_athlete = filtered_athlete[filtered_athlete["Home"].isin(s_home)]
    if s_away:
        filtered_athlete = filtered_athlete[filtered_athlete["Away"].isin(s_away)]
    if s_name and "Athlete" in filtered_athlete.columns:
        filtered_athlete = filtered_athlete[filtered_athlete["Athlete"].str.contains(s_name, case=False, na=False)]

    st.success(f"✅ {filtered_athlete.shape[0]} athlete records shown")
    latest_athlete_date = pd.to_datetime(filtered_athlete["Date"], errors='coerce').dropna().max()
    if pd.notnull(latest_athlete_date):
        st.markdown(f"**🗓️ Athlete data current as of:** {latest_athlete_date.date()}")

    st.dataframe(filtered_athlete)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Athlete CSV", filtered_athlete.to_csv(index=False).encode("utf-8"), "athlete_data.csv", "text/csv")
    with col2:
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
    if "Matches" in overall_df.columns:
        overall_df = overall_df[overall_df["Matches"].astype(str).str.strip().str.lower() != "by set"]

if overall_df.empty:
    st.warning("⚠️ No overall data found or processed.")
else:
    st.success(f"✅ {overall_df.shape[0]} overall records shown")
    st.dataframe(overall_df)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Overall CSV", overall_df.to_csv(index=False).encode("utf-8"), "overall_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Overall Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()
            else:
                st.info("ℹ️ No overall cache found.")
        st.caption("⚠️ Only use if source overall data changed.")

st.markdown("---")

# -------------------------------
# Section 3: Rotation Data
# -------------------------------
st.header("🔄 Rotation Data")

force_refresh_rotation = st.session_state.get("reset_cache_rotation", False)

with st.spinner("🔄 Loading Rotation Data..."):
    rotation_df = Rotation_Data_Load.load_preprocessed_rotation_data(force_rebuild=force_refresh_rotation)

if rotation_df.empty:
    st.warning("⚠️ No rotation data found or processed.")
else:
    st.success(f"✅ {rotation_df.shape[0]} rotation records shown")
    st.dataframe(rotation_df)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Rotation CSV", rotation_df.to_csv(index=False).encode("utf-8"), "rotation_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Rotation Cache"):
            if os.path.exists(Rotation_Data_Load.CACHE_FILE):
                os.remove(Rotation_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_rotation"] = True
                st.rerun()
            else:
                st.info("ℹ️ No rotation cache found.")
        st.caption("⚠️ Only use if source rotation data changed.")

# -------------------------------
# Section 4: Match Data by Set (Placeholder)
# -------------------------------
st.header("📘 Match Data by Set")

st.info("📂 This section is reserved for loading and displaying Match Data by Set. Functionality coming soon.")

st.markdown("---")

# -------------------------------
# Section 5: Setter Distribution Data
# -------------------------------
st.header("📊 Setter Distribution Data")

setter_file = "data/Setter Distribution Data.csv"

if os.path.exists(setter_file):
    try:
        setter_df = pd.read_csv(setter_file)
        st.success(f"✅ Loaded {setter_df.shape[0]} rows from Setter Distribution Data")
        st.dataframe(setter_df)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "💾 Download Setter Distribution CSV",
                data=setter_df.to_csv(index=False).encode("utf-8"),
                file_name="setter_distribution_data.csv",
                mime="text/csv"
            )
        with col2:
            st.caption("📌 Direct from scouting reports and analytics exports")
    except Exception as e:
        st.error(f"❌ Failed to load Setter Distribution Data: {e}")
else:
    st.warning("⚠️ Setter Distribution file not found at `data/Setter Distribution Data.csv`")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations — Streamlit analytics platform • Crandall Chargers Volleyball © 2025")
