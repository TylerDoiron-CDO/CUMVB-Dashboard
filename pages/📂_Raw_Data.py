import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# -------------------------------
# Page Setup
# -------------------------------

st.set_page_config(page_title="📂 Raw Data", layout="wide")
st.title("📂 Raw Athlete Data Viewer")
st.markdown("This page loads and processes raw CSV files from the `data/Athlete Data` folder and displays the full athlete-level dataset.")

st.markdown("---")

# -------------------------------
# File & Folder Configuration
# -------------------------------

ATHLETE_DATA_DIR = "data/Athlete Data"
CACHE_FILE = "data/athlete_data_cache.parquet"

# -------------------------------
# Helper Functions
# -------------------------------

def infer_season_from_date(date_str):
    try:
        match_date = datetime.strptime(date_str, "%Y-%m-%d")
        year = match_date.year
        if match_date.month >= 9:
            return f"{year}-{year + 1}"
        else:
            return f"{year - 1}-{year}"
    except:
        return "Unknown"

def process_athlete_data_file(file_path, file_name):
    try:
        df_raw = pd.read_csv(file_path, header=None, skiprows=1)
        df_raw.columns = df_raw.iloc[0]
        df = df_raw.drop(index=0).reset_index(drop=True)
    except Exception as e:
        st.warning(f"⚠️ Failed to read file {file_name}: {e}")
        return None

    # Extract metadata
    date_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", file_name)
    date_str = date_match.group(1) if date_match else "Unknown"
    season = infer_season_from_date(date_str)

    home_team = away_team = "Unknown"
    if "@" in file_name:
        parts = file_name.split("@")
        away_team = parts[0].strip()
        home_team = parts[1].split("—")[0].strip()
    elif "vs." in file_name:
        parts = file_name.split("vs.")
        home_team = parts[0].strip()
        away_team = parts[1].split("—")[0].strip()

    team_match = re.search(r"Totals\s+(.*?)\s+\(", file_name)
    team = team_match.group(1).strip() if team_match else "Unknown"

    # Add metadata columns
    df["Season"] = season
    df["Date"] = date_str
    df["Home"] = home_team
    df["Away"] = away_team
    df["TEAM"] = team
    df["source_file"] = file_name

    return df

def load_preprocessed_athlete_data():
    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)

    all_dfs = []
    for file in os.listdir(ATHLETE_DATA_DIR):
        if file.endswith(".csv"):
            file_path = os.path.join(ATHLETE_DATA_DIR, file)
            df = process_athlete_data_file(file_path, file)
            if df is not None:
                all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)

    # 🔐 Clean all column names
    combined.columns = [str(col) for col in combined.columns]

    # 🔐 Clean each column
    for col in combined.columns:
        try:
            # Try convert to numeric if it makes sense
            combined[col] = pd.to_numeric(combined[col], errors='ignore')
        except:
            pass

        # If still object type, convert to string to avoid Arrow issues
        if combined[col].dtype == 'object':
            try:
                combined[col] = combined[col].astype(str)
            except:
                combined[col] = combined[col].apply(lambda x: str(x) if not isinstance(x, str) else x)

    # ✅ Save to Parquet safely
    try:
        combined.to_parquet(CACHE_FILE, index=False)
    except Exception as e:
        st.warning(f"Failed to save cache: {e}")

    return combined

# -------------------------------
# Main Display Logic
# -------------------------------

with st.spinner("🔄 Loading and processing athlete data..."):
    athlete_df = load_preprocessed_athlete_data()

if athlete_df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    st.success(f"✅ Loaded {athlete_df.shape[0]} records from {ATHLETE_DATA_DIR}")
    st.subheader("📋 Processed Athlete Data Table")
    st.dataframe(athlete_df)

    st.download_button(
        label="💾 Download Full Athlete Data as CSV",
        data=athlete_df.to_csv(index=False).encode('utf-8'),
        file_name="athlete_data_processed.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Raw athlete performance data from Balltime files • Crandall Chargers Volleyball © 2025")
