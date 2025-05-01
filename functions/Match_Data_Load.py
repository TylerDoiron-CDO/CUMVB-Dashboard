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

def parse_date_column(raw_date, season):
    try:
        raw_date = str(raw_date).strip()
        if re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
            return raw_date

        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }

        start_year, end_year = map(int, season.split("-"))

        # Handles formats like "Sep 29" or "29 Sep"
        match1 = re.match(r"([A-Za-z]{3})[\s\-]*(\d{1,2})", raw_date)
        if match1:
            month_str = match1.group(1).capitalize()
            day = int(match1.group(2))
            month = month_map.get(month_str)
            year = start_year if month >= 9 else end_year
            return datetime(year, month, day).strftime("%Y-%m-%d")

        # Handles formats like "02-Dec" or "2-Dec"
        match2 = re.match(r"(\d{1,2})[\s\-]*([A-Za-z]{3})", raw_date)
        if match2:
            day = int(match2.group(1))
            month_str = match2.group(2).capitalize()
            month = month_map.get(month_str)
            year = start_year if month >= 9 else end_year
            return datetime(year, month, day).strftime("%Y-%m-%d")

        # Catch Excel misinterpreted format (datetime object interpreted as string)
        try:
            dt = pd.to_datetime(raw_date, errors='coerce')
            if pd.notnull(dt):
                month = dt.month
                year = start_year if month >= 9 else end_year
                return datetime(year, month, dt.day).strftime("%Y-%m-%d")
        except:
            pass

    except Exception as e:
        print(f"⚠️ Failed to parse date '{raw_date}' with season '{season}': {e}")
        return raw_date

    return raw_date
    
def adjust_result_for_team(row):
    result = row.get("Result", "")
    team = row.get("Team", "")
    match = re.match(r"([WL])\s*(\d+)-(\d+)", result)
    if not match:
        return result
    outcome, team_score, opp_score = match.groups()
    if team == "Crandall":
        return result
    else:
        return f"{'L' if outcome == 'W' else 'W'} {opp_score}-{team_score}"

def normalize_set_score(value):
    try:
        value = str(value).strip()
        month_map = {
            'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5',
            'Jun': '6', 'Jul': '7', 'Aug': '8', 'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        for m, n in month_map.items():
            value = value.replace(m, n)
        parts = re.findall(r"\d+", value)
        if len(parts) == 2:
            return f"{parts[0]}-{parts[1]}"
    except:
        pass
    return value

def flip_set_score(row, col):
    if row.get("Team", "") == "Crandall":
        return row[col]
    parts = re.findall(r"(\d+)-(\d+)", str(row[col]))
    if parts:
        return f"{parts[0][1]}-{parts[0][0]}"
    return row[col]

def process_match_data_file(file_path, file_name):
    try:
        df = pd.read_csv(file_path)
        df = df[[col for col in df.columns if not str(col).startswith("0")]]

        season = infer_season_from_filename(file_name)
        is_opponents_file = "Opponents" in file_name

        df["Team"] = df.apply(lambda row: "Crandall" if not is_opponents_file else (
            row["Opponent"].strip()[1:].strip() if row["Opponent"].strip().startswith("@")
            else row["Opponent"].strip()[3:].strip() if row["Opponent"].strip().lower().startswith("vs")
            else "Unknown"), axis=1)

        df["Home"] = df["Opponent"].apply(
            lambda val: val.strip()[1:].strip() if val.strip().startswith("@")
            else "Crandall" if val.strip().lower().startswith("vs")
            else "Unknown"
        )
        df["Away"] = df["Opponent"].apply(
            lambda val: "Crandall" if val.strip().startswith("@")
            else val.strip()[3:].strip() if val.strip().lower().startswith("vs")
            else "Unknown"
        )

        df["Season"] = season
        df["source_file"] = file_name

        if "Date" in df.columns:
            df["Date"] = df["Date"].apply(lambda d: parse_date_column(d, season))

        if "Result" in df.columns:
            df["Result"] = df.apply(adjust_result_for_team, axis=1)

        set_columns = [col for col in df.columns if col.lower().startswith("score") or re.match(r"set\s*\d", col.lower())]
        for col in set_columns:
            df[col] = df[col].apply(normalize_set_score)
            df[col] = df.apply(lambda row: flip_set_score(row, col), axis=1)

        df.drop(columns=["Opponent"], inplace=True, errors="ignore")

        start_cols = ["Season", "Date", "Home", "Away", "Team"]
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
