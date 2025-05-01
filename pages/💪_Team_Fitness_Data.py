import streamlit as st
import pandas as pd

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
        df.columns = df.columns.str.strip()  # Remove extra whitespace
        return df
    except Exception as e:
        st.error(f"Failed to load Testing Data: {e}")
        return pd.DataFrame()

df = load_testing_data()

# Apply filters
if not df.empty:
    # Get filter options
    athlete_options = sorted(df["Athlete"].dropna().unique())
    position_options = sorted(df["Primary Position"].dropna().unique())
    date_options = sorted(df["Testing Date"].dropna().unique())

    with st.expander("🔍 Filter Options"):
        selected_athletes = st.multiselect("Filter by Athlete", athlete_options)
        selected_positions = st.multiselect("Filter by Position", position_options)
        selected_dates = st.multiselect("Filter by Testing Date", date_options)

    # Apply filters
    filtered_df = df.copy()
    if selected_athletes:
        filtered_df = filtered_df[filtered_df["Athlete"].isin(selected_athletes)]
    if selected_positions:
        filtered_df = filtered_df[filtered_df["Primary Position"].isin(selected_positions)]
    if selected_dates:
        filtered_df = filtered_df[filtered_df["Testing Date"].isin(selected_dates)]

    # Display
    st.subheader("📋 Raw Fitness Testing Data")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.warning("No data available.")

