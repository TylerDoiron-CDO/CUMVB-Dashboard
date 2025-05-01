# functions/Match_Data_Load.py

import pandas as pd
import os
import re
from datetime import datetime

MATCH_DATA_DIR = "data/Match Data"
CACHE_FILE = "data/match_data_cache.parquet"


def infer_season_from_filename(file_name):
    try:
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name)
        if not date_match:
            return "Unknown"
        match_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
        year = match_date.year
        return f"{year}-{year + 1}" if match_date.month >= 9 else f"{year - 1}-{year}"
    except:
        return "Unknown"

def infer_home_away_team(row, file_name, team_label):
    opp = row.get("Opponent", "")
    home, away = "Unknown", "Unknown"
    if opp.startswith("@"):
        home = opp.replace("@", "").strip()
        away = team_label
    elif opp.startswith("vs") or opp.startswith("Vs"):
        home = team_label
        away = opp.replace("vs", "").replace("Vs", "").strip()
    return home, away

def process_match_data_file(file_path, file_name):
    try:
        df = pd.read_csv(file_path)
        df = df[[col for col in df.columns if not str(col).startswith("0")]]

        season = infer_season_from_filename(file_name)
        is_opponents_file = "Opponents" in file_name

        if is_opponents_file:
            df["Team"] = df["Opponent"].astype(str).str.extract(r"[@vsVS]+\s*(.*)")[0].fillna("Unknown").str.strip()
        else:
            df["Team"] = "Crandall"

        df["Season"] = season
        df["source_file"] = file_name

        # Apply Home and Away extraction
        homes, aways = [], []
        for _, row in df.iterrows():
            home, away = infer_home_away_team(row, file_name, df.at[_, "Team"])
            homes.append(home)
            aways.append(away)

        df["Home"] = homes
        df["Away"] = aways

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

