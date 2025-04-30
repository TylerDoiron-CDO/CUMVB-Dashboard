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
# Constants
# -------------------------------
ATHLETE_DATA_DIR = "data/Athlete Data"
CACHE_FILE = "data/athlete_data_cache.parquet"

# -------------------------------
# Helper: Infer Season from Date
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

# -------------------------------
# Helper: Process a Single File
# -------------------------------
def process_athlete_data_file(file_path, file_name):
    try:
        # Read and skip first row
        df_raw = pd.read_csv(file_path, header=None, skiprows=1)

        # Manually deduplicate columns
        raw_cols = list(df_raw.iloc[0])
        seen = {}
        deduped_cols = []
        for col in raw_cols:
            if col not in seen:
                seen[col] = 0
                deduped_cols.append(col)
            else:
                seen[col] += 1
                deduped_cols.append(f"{col}.{seen[col]}")

        df_raw.columns = deduped_cols
        df = df_raw.drop(index=0).reset_index(drop=True)

    except Exception as e:
        st.warning(f"⚠️ Failed to read file {file_name}: {e}")
        return None

    # Extract metadata from filename
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

    # Add metadata
    df.insert(0, "Season", season)
    df.insert(1, "Date", date_str)
    df.insert(2, "Home", home_team)
    df.insert(3, "Away", away_team)
    df.insert(4, "TEAM", team)
    df["source_file"] = file_name

    # Drop columns starting with '0'
    df = df[[col for col in df.columns if not str(col).startswith("0")]]

    # Reorder to place metadata first, source_file last
    metadata = ["Season", "Date", "Home", "Away", "TEAM"]
    other_cols = [col for col in df.columns if col not in metadata + ["source_file"]]
    df = df[metadata + other_cols + ["source_file"]]

    return df

# -------------------------------
# Main Loader Function
# -------------------------------
def load_preprocessed_athlete_data():
    historical_path = "data/Historical Athlete Data.csv"
    historical_df = pd.DataFrame()
    if os.path.exists(historical_path):
        try:
            historical_df = pd.read_csv(historical_path)
            historical_df.insert(0, "Season", "Unknown")
            historical_df.insert(1, "Date", "Unknown")
            historical_df.insert(2, "Home", "Unknown")
            historical_df.insert(3, "Away", "Unknown")
            historical_df.insert(4, "TEAM", "Unknown")
            historical_df["source_file"] = "historical data"

            # Drop columns starting with '0'
            historical_df = historical_df[[col for col in historical_df.columns if not str(col).startswith("0")]]

            # Reorder columns
            metadata = ["Season", "Date", "Home", "Away", "TEAM"]
            other_cols = [col for col in historical_df.columns if col not in metadata + ["source_file"]]
            historical_df = historical_df[metadata + other_cols + ["source_file"]]
        except Exception as e:
            st.warning(f"⚠️ Failed to load Historical Athlete Data: {e}")

    all_dfs = []
    for file in os.listdir(ATHLETE_DATA_DIR):
        if file.endswith(".csv"):
            file_path = os.path.join(ATHLETE_DATA_DIR, file)
            df = process_athlete_data_file(file_path, file)
            if df is not None:
                all_dfs.append(df)

    if historical_df is not None and not historical_df.empty:
        all_dfs.append(historical_df)

    if os.path.exists(CACHE_FILE) and not all_dfs:
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

    if historical_df is not None and not historical_df.empty:
        all_dfs.append(historical_df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.columns = [str(col) for col in combined.columns]

    for col in combined.columns:
        try:
            combined[col] = pd.to_numeric(combined[col], errors="ignore")
        except Exception:
            pass
        if not pd.api.types.is_numeric_dtype(combined[col]) and not pd.api.types.is_bool_dtype(combined[col]):
            try:
                combined[col] = combined[col].astype(str)
            except Exception:
                combined[col] = combined[col].apply(lambda x: str(x) if not isinstance(x, str) else x)

    try:
        combined.to_parquet(CACHE_FILE, index=False)
    except Exception as e:
        st.warning(f"❌ Failed to write cache: {e}")

    return combined

# -------------------------------
# Load and Display
# -------------------------------
with st.spinner("🔄 Loading and processing Athlete Data..."):
    athlete_df = load_preprocessed_athlete_data()

if athlete_df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    st.success(f"✅ Loaded {athlete_df.shape[0]} records from {ATHLETE_DATA_DIR}")
    st.subheader("📋 Processed Athlete Data Table")
    st.dataframe(athlete_df)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button(
            label="💾 Download CSV",
            data=athlete_df.to_csv(index=False).encode('utf-8'),
            file_name="athlete_data_processed.csv",
            mime="text/csv"
        )
    with col2:
        if st.button("🔁 Reset Cache"):
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
                st.warning("⚠️ Cache has been cleared. The app will now reload and rebuild from source files.")
                st.experimental_rerun()
            else:
                st.info("ℹ️ No cache file found to reset.")
        st.caption("⚠️ Only use if data has changed or is outdated.")

st.markdown("---")
st.caption("Raw athlete performance data from Balltime files • Crandall Chargers Volleyball © 2025")
