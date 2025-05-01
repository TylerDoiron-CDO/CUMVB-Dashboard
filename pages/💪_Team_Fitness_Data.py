import streamlit as st
import pandas as pd

# Constants
TESTING_DATA_PATH = "data/Testing Data.csv"
NORMATIVE_DATA_PATH = "data/Volleyball Canada Normative.csv"

# Page config
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")
st.title("💪 Team Fitness Data")
st.markdown("This page displays the team's fitness testing results and compares them to Volleyball Canada's normative values.")

# Load team testing data
@st.cache_data
def load_testing_data():
    try:
        df = pd.read_csv(TESTING_DATA_PATH)
        return df
    except Exception as e:
        st.error(f"Failed to load Testing Data: {e}")
        return pd.DataFrame()

# Load Volleyball Canada normative values
@st.cache_data
def load_normative_data():
    try:
        df = pd.read_csv(NORMATIVE_DATA_PATH)
        return df
    except Exception as e:
        st.error(f"Failed to load Normative Data: {e}")
        return pd.DataFrame()

# Load data
testing_df = load_testing_data()
norms_df = load_normative_data()

# Filters
if not testing_df.empty:
    with st.expander("🔍 Filter Options"):
        names = st.multiselect("Filter by Player", sorted(testing_df["name"].unique()))
        positions = st.multiselect("Filter by Position", sorted(testing_df["position"].dropna().unique()))
        
        filtered_df = testing_df.copy()
        if names:
            filtered_df = filtered_df[filtered_df["name"].isin(names)]
        if positions:
            filtered_df = filtered_df[filtered_df["position"].isin(positions)]
else:
    filtered_df = pd.DataFrame()

# Show Testing Data
st.subheader("📋 Team Fitness Testing Results")
if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("No testing data to display.")

# Show Normative Reference Table (if applicable)
if not norms_df.empty:
    st.subheader("📊 Volleyball Canada Normative Reference Values")
    st.dataframe(norms_df, use_container_width=True)
else:
    st.info("Normative values not loaded or missing.")

# Summary Statistics
if not filtered_df.empty:
    st.subheader("📈 Summary Statistics")
    numeric_cols = filtered_df.select_dtypes(include="number").columns
    if not numeric_cols.empty:
        st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("No numeric columns available for summary statistics.")
