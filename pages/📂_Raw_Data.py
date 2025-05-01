import streamlit as st
import pandas as pd
import os
from functions import Athlete_Data_Load

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="📂 Raw Data", layout="wide")
st.title("📂 Raw Athlete Data Viewer")
st.markdown("This page displays the full combined dataset from raw match files and historical records.")
st.markdown("---")

# -------------------------------
# Load Data
# -------------------------------
force_refresh = st.session_state.get("reset_cache", False)
with st.spinner("🔄 Loading and processing Athlete Data..."):
    df = Athlete_Data_Load.load_preprocessed_athlete_data(force_rebuild=force_refresh)

if df.empty:
    st.warning("⚠️ No athlete data found or processed.")
    st.stop()

# -------------------------------
# Filter UI
# -------------------------------
with st.expander("🔎 Filter Options"):
    col1, col2, col3, col4, col5 = st.columns(5)

    all_seasons = sorted(df["Season"].dropna().unique())
    all_teams = sorted(df["TEAM"].dropna().unique())
    all_home = sorted(df["Home"].dropna().unique())
    all_away = sorted(df["Away"].dropna().unique())
    all_names = sorted(df["Athlete"].dropna().unique()) if "Athlete" in df.columns else []

    selected_seasons = col1.multiselect("Season", options=all_seasons)
    selected_teams = col2.multiselect("TEAM", options=all_teams)
    selected_home = col3.multiselect("Home", options=all_home)
    selected_away = col4.multiselect("Away", options=all_away)
    name_search = col5.text_input("Search Athlete Name")

# -------------------------------
# Apply Filters
# -------------------------------
filtered_df = df.copy()

if selected_seasons:
    filtered_df = filtered_df[filtered_df["Season"].isin(selected_seasons)]

if selected_teams:
    filtered_df = filtered_df[filtered_df["TEAM"].isin(selected_teams)]

if selected_home:
    filtered_df = filtered_df[filtered_df["Home"].isin(selected_home)]

if selected_away:
    filtered_df = filtered_df[filtered_df["Away"].isin(selected_away)]

if name_search and "Athlete" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Athlete"].str.contains(name_search, case=False, na=False)]

# -------------------------------
# Display Table
# -------------------------------
st.success(f"✅ {filtered_df.shape[0]} records match your filters")

latest_date = pd.to_datetime(filtered_df["Date"], errors="coerce").dropna().max()
if pd.notnull(latest_date):
    st.markdown(f"**🗓️ Data current as of:** {latest_date.date()}")

st.subheader("📋 Filtered Athlete Data Table")
st.dataframe(filtered_df)

# -------------------------------
# Download + Cache Reset
# -------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.download_button(
        label="💾 Download CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="athlete_data_filtered.csv",
        mime="text/csv"
    )
with col2:
    if st.button("🔁 Reset Cache"):
        if os.path.exists(Athlete_Data_Load.CACHE_FILE):
            os.remove(Athlete_Data_Load.CACHE_FILE)
            st.session_state["reset_cache"] = True
            st.warning("⚠️ Cache has been cleared. Reloading now...")
            st.rerun()
        else:
            st.info("ℹ️ No cache file found to reset.")
    st.caption("⚠️ Only use if data has changed or updated.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations — Advanced analytics powered by Streamlit • Crandall Chargers Volleyball © 2025")

