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

# Display filters if data is loaded
if not df.empty:
    athlete_options = sorted(df["Athlete"].dropna().unique())
    position_options = sorted(df["Primary Position"].dropna().unique())
    date_options = sorted(df["Testing Date"].dropna().unique())

    # 🧭 Inline filters — always visible and clean layout
    st.markdown("### 🔍 Filter Options")
    filter_cols = st.columns([4, 3, 3])

    with filter_cols[0]:
        selected_athletes = st.multiselect(
            "Filter by Athlete",
            options=athlete_options,
            default=athlete_options,
            key="filter_athlete"
        )

    with filter_cols[1]:
        selected_positions = st.multiselect(
            "Filter by Position",
            options=position_options,
            default=position_options,
            key="filter_position"
        )

    with filter_cols[2]:
        selected_dates = st.multiselect(
            "Filter by Testing Date",
            options=date_options,
            default=date_options,
            key="filter_date"
        )

    # Filter the data
    filtered_df = df[
        df["Athlete"].isin(selected_athletes) &
        df["Primary Position"].isin(selected_positions) &
        df["Testing Date"].isin(selected_dates)
    ]

    # Display the table
    st.subheader("📋 Raw Fitness Testing Data")
    st.dataframe(filtered_df, use_container_width=True)

    # Utility buttons directly below the table
    col1, col2 = st.columns([1, 1])

    with col1:
        st.download_button(
            "💾 Download Fitness CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "team_fitness_data.csv",
            "text/csv"
        )

    with col2:
        if st.button("🔁 Reset Fitness Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Reloading data...")
            st.rerun()

    st.caption("⚠️ Only use 'Reset Fitness Cache' if the source data file has changed.")

else:
    st.warning("No data available.")

