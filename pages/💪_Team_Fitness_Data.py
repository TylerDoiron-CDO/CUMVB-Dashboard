import streamlit as st
import pandas as pd
import os

# Constants
TESTING_DATA_PATH = "data/Testing Data.csv"

# Page setup
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")
st.title("💪 Team Fitness Data")
st.markdown("Explore raw fitness testing results for all athletes. Use the filters below to focus your view.")

# Load data
@st.cache_data
def load_testing_data():
    try:
        df = pd.read_csv(TESTING_DATA_PATH)
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"Failed to load Testing Data: {e}")
        return pd.DataFrame()

df = load_testing_data()

if not df.empty:
    # Filter values
    athlete_options = sorted(df["Athlete"].dropna().unique())
    position_options = sorted(df["Primary Position"].dropna().unique())
    date_options = sorted(df["Testing Date"].dropna().unique())

    # Filters (clean style)
    col1, col2, col3 = st.columns(3)
    f_athlete = col1.multiselect("Athlete", options=athlete_options)
    f_position = col2.multiselect("Position", options=position_options)
    f_date = col3.multiselect("Testing Date", options=date_options)

    # Apply filters
    filtered_df = df.copy()
    if f_athlete:
        filtered_df = filtered_df[filtered_df["Athlete"].isin(f_athlete)]
    if f_position:
        filtered_df = filtered_df[filtered_df["Primary Position"].isin(f_position)]
    if f_date:
        filtered_df = filtered_df[filtered_df["Testing Date"].isin(f_date)]

    # Show data
    st.success(f"✅ {filtered_df.shape[0]} testing records shown")
    st.subheader("📋 Raw Fitness Testing Data")
    st.dataframe(filtered_df, use_container_width=True)

    # Utility buttons
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "💾 Download Fitness CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "team_fitness_data.csv",
            "text/csv"
        )
    with col_d2:
        if st.button("🔁 Reset Fitness Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Reloading data...")
            st.rerun()

    st.caption("⚠️ Only use 'Reset Fitness Cache' if the source data file has changed.")
else:
    st.warning("No data available.")

