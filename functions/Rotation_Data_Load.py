# functions/Rotation_Data_Load.py

import pandas as pd
import os
import re
from datetime import datetime

ROTATION_DATA_DIR = "data/Rotation Data"
HISTORICAL_FILE = "data/Historical Rotation Data.csv"
CACHE_FILE = "data/rotation_data_cache.parquet"

TARGET_COLUMN_NAME = "Rotation"

def infer_season_from_date(date_str):
    try:
        match_date = datetime.strptime(date_str, "%Y-%m-%d")
        year = match_date.year
        return f"{year}-{year + 1}" if match_date.month >= 9 else f"{year - 1}-{year}"
    except:
        return "Unknown"

def process_rotation_data_file(file_path, file_name):
    try:
        df_raw = pd.read_csv(file_path, header=None, skiprows=1)
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

        # Rename "Matches" column to "Rotation"
        df.columns = [TARGET_COLUMN_NAME if col == "Matches" else col for col in df.columns]

        # Filter out rows where Rotation == "By Rotation"
        if TARGET_COLUMN_NAME in df.columns:
            df = df[df[TARGET_COLUMN_NAME].astype(str).str.strip().str.lower() != "by rotation"]

    except Exception:
        return None

    date_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", file_name)
    date_str = date_match.group(1) if date_match else "Unknown"
    season = infer_season_from_date(date_str)

    home_team = away_team = "Unknown"
    if "@" in file_name:
        parts = file_name.split("@")
        away_team = parts[0].strip()
        home_team = parts[1].split("\u2014")[0].strip()
    elif "vs." in file_name:
        parts = file_name.split("vs.")
        home_team = parts[0].strip()
        away_team = parts[1].split("\u2014")[0].strip()

    team_match = re.search(r"Totals\s+(.*?)\s+\(", file_name)
    team = team_match.group(1).strip() if team_match else "Unknown"

    df.insert(0, "Season", season)
    df.insert(1, "Date", date_str)
    df.insert(2, "Home", home_team)
    df.insert(3, "Away", away_team)
    df.insert(4, "Team", team)
    df["source_file"] = file_name

    df = df[[col for col in df.columns if not str(col).startswith("0")]]
    return df

def load_preprocessed_rotation_data(force_rebuild=False):
    if os.path.exists(CACHE_FILE) and not force_rebuild:
        return pd.read_parquet(CACHE_FILE)

    all_dfs = []

    for file in os.listdir(ROTATION_DATA_DIR):
        if file.endswith(".csv"):
            df = process_rotation_data_file(os.path.join(ROTATION_DATA_DIR, file), file)
            if df is not None:
                all_dfs.append(df)

    # Load historical
    if os.path.exists(HISTORICAL_FILE):
        try:
            hist_df = pd.read_csv(HISTORICAL_FILE)
            hist_df = hist_df.drop(columns=["Unnamed: 0"], errors="ignore")
            hist_df = hist_df.rename(columns={"Matches": TARGET_COLUMN_NAME})
            hist_df = hist_df[hist_df[TARGET_COLUMN_NAME].astype(str).str.strip().str.lower() != "by rotation"]
            hist_df["source_file"] = os.path.basename(HISTORICAL_FILE)

            if all_dfs:
                for col in all_dfs[0].columns:
                    if col not in hist_df.columns:
                        hist_df[col] = pd.NA
                for col in hist_df.columns:
                    if col not in all_dfs[0].columns:
                        for i in range(len(all_dfs)):
                            all_dfs[i][col] = pd.NA
                hist_df = hist_df[all_dfs[0].columns]

            all_dfs.append(hist_df)
        except Exception as e:
            print(f"⚠️ Failed to load historical rotation data: {e}")

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.columns = [str(col) for col in combined.columns]

    for col in combined.columns:
        try:
            combined[col] = pd.to_numeric(combined[col], errors="ignore")
        except:
            pass
        if not pd.api.types.is_numeric_dtype(combined[col]) and not pd.api.types.is_bool_dtype(combined[col]):
            combined[col] = combined[col].astype(str)

    try:
        combined.to_parquet(CACHE_FILE, index=False)
    except Exception as e:
        print(f"❌ Failed to write cache: {e}")

    return combined
