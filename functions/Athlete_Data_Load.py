# functions/Athlete_Data_Load.py

import pandas as pd
import os
import re
from datetime import datetime

ATHLETE_DATA_DIR = "data/Athlete Data"
HISTORICAL_DATA_FILE = "data/Historical Athlete Data.csv"
CACHE_FILE = "data/athlete_data_cache.parquet"

def infer_season_from_date(date_str):
    try:
        match_date = datetime.strptime(date_str, "%Y-%m-%d")
        year = match_date.year
        return f"{year}-{year + 1}" if match_date.month >= 9 else f"{year - 1}-{year}"
    except:
        return "Unknown"

def extract_home_away_team(file_name):
    # Normalize dashes and whitespace
    cleaned = file_name.replace("—", "-").replace("–", "-")
    cleaned = re.sub(r"\s+", " ", cleaned)

    prefix = cleaned.split("Totals")[0].strip()
    vs_match = re.search(r"(.+?)\s+vs\s+([^-^(]+)", prefix, re.IGNORECASE)
    at_match = re.search(r"(.+?)\s+@\s+([^-^(]+)", prefix, re.IGNORECASE)

    if vs_match:
        home_team = vs_match.group(1).strip()
        away_team = vs_match.group(2).strip()
    elif at_match:
        away_team = at_match.group(1).strip()
        home_team = at_match.group(2).strip()
    else:
        home_team = away_team = "Unknown"

    return home_team, away_team

def process_athlete_data_file(file_path, file_name):
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
    except Exception:
        return None

    date_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", file_name)
    date_str = date_match.group(1) if date_match else "Unknown"
    season = infer_season_from_date(date_str)

    home_team, away_team = extract_home_away_team(file_name)

    team_match = re.search(r"Totals\s+(.*?)\s+\(", file_name)
    team = team_match.group(1).strip() if team_match else "Unknown"

    df.insert(0, "Season", season)
    df.insert(1, "Date", date_str)
    df.insert(2, "Home", home_team)
    df.insert(3, "Away", away_team)
    df.insert(4, "Team", team)
    df["source_file"] = file_name

    df = df[[col for col in df.columns if not str(col).startswith("0")]]
    metadata = ["Season", "Date", "Home", "Away", "Team"]
    other_cols = [col for col in df.columns if col not in metadata + ["source_file"]]
    df = df[metadata + other_cols + ["source_file"]]

    return df

def load_preprocessed_athlete_data(force_rebuild=False):
    historical_df = pd.DataFrame()
    if os.path.exists(HISTORICAL_DATA_FILE):
        try:
            historical_df = pd.read_csv(HISTORICAL_DATA_FILE)
            historical_df.insert(0, "Season", "Unknown")
            historical_df.insert(1, "Date", "Unknown")
            historical_df.insert(2, "Home", "Unknown")
            historical_df.insert(3, "Away", "Unknown")
            historical_df.insert(4, "Team", "Unknown")
            historical_df["source_file"] = "historical data"

            historical_df = historical_df[[col for col in historical_df.columns if not str(col).startswith("0")]]
            metadata = ["Season", "Date", "Home", "Away", "Team"]
            other_cols = [col for col in historical_df.columns if col not in metadata + ["source_file"]]
            historical_df = historical_df[metadata + other_cols + ["source_file"]]
        except Exception as e:
            print(f"⚠️ Failed to load Historical Athlete Data: {e}")

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
            try:
                combined[col] = combined[col].astype(str)
            except:
                combined[col] = combined[col].apply(lambda x: str(x) if not isinstance(x, str) else x)

    try:
        combined.to_parquet(CACHE_FILE, index=False)
    except Exception as e:
        print(f"❌ Failed to write cache: {e}")

    return combined

