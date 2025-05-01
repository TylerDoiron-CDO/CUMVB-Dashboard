# functions/Match_Data_Load.py

import pandas as pd
import os
import re
from datetime import datetime

MATCH_DATA_DIR = "data/Match Data"
CACHE_FILE = "data/match_data_cache.parquet"

def infer_season_from_filename(file_name):
    try:
        season_match = re.search(r"(\d{4}-\d{4})", file_name)
        if season_match:
            return season_match.group(1)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name)
        if date_match:
            match_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            year = match_date.year
            return f"{year}-{year + 1}" if match_date.month >= 9 else f"{year - 1}-{year}"
        return "Unknown"
    except:
        return "Unknown"

def process_match_data_file(file_path, file_name):
    try:
        df = pd.read_csv(file_path)
        df = df[[col for col in df.columns if not str(col).startswith("0")]]

        season = infer_season_from_filename(file_name)
        is_opponents_file = "Opponents" in file_name
        df["Is_Opponent_File"] = 1 if is_opponents_file else 0

        # Team based solely on file name
        df["Team"] = df["Opponent"]  # placeholder
        df.loc[~is_opponents_file, "Team"] = "Crandall"
        df.loc[is_opponents_file, "Team"] = df.loc[is_opponents_file, "Opponent"]
            .astype(str)
            .str.extract(r"[@|vs|VS]\s*(.*)")[0]
            .fillna("Unknown")
            .str.strip()

        # Home and Away based on Opponent prefix only
        df["Home"] = df["Opponent"].apply(
            lambda val: val.strip()[1:].strip() if val.strip().startswith("@") else (
                "Crandall" if val.strip().lower().startswith("vs") else "Unknown"
            )
        )
        df["Away"] = df["Opponent"].apply(
            lambda val: "Crandall" if val.strip().startswith("@") else (
                val.strip()[3:].strip() if val.strip().lower().startswith("vs") else "Unknown"
            )
        )

        df["Season"] = season
        df["source_file"] = file_name

        start_cols = ["Season", "Date", "Home", "Away", "Team", "Is_Opponent_File"]
        other_cols = [col for col in df.columns if col not in start_cols + ["source_file"]]
        df = df[start_cols + other_cols + ["source_file"]]

        return df
    except Exception as e:
        print(f"⚠️ Failed to process {file_name}: {e}")
        return None

def load_preprocessed_match_data(force_rebuild=False):
    if os.path.exists(CACHE_FILE) and not force_rebuild:
        return pd.read_parquet(CACHE_FILE)

    all_dfs = []

    for file in os.listdir(MATCH_DATA_DIR):
        if file.endswith(".csv"):
            df = process_match_data_file(os.path.join(MATCH_DATA_DIR, file), file)
            if df is not None:
                all_dfs.append(df)

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
        print(f"❌ Failed to write match data cache: {e}")

    return combined
