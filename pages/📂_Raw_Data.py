import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

ATHLETE_DATA_DIR = "data/Athlete Data"

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

@st.cache_data
def load_preprocessed_athlete_data():
    combined = []

    for file in os.listdir(ATHLETE_DATA_DIR):
        if not file.endswith(".csv"):
            continue

        file_path = os.path.join(ATHLETE_DATA_DIR, file)

        # Step 1: Read file and skip first row
        df_raw = pd.read_csv(file_path, header=None, skiprows=1)

        # Step 2: Extract header from row 0
        df_raw.columns = df_raw.iloc[0]
        df = df_raw.drop(index=0).reset_index(drop=True)

        # Step 3: Extract metadata from filename
        filename = file
        date_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", filename)
        date_str = date_match.group(1) if date_match else "Unknown"

        season = infer_season_from_date(date_str)

        home_team = away_team = "Unknown"
        if "@" in filename:
            parts = filename.split("@")
            away_team = parts[0].strip()
            home_team = parts[1].split("—")[0].strip()
        elif "vs." in filename:
            parts = filename.split("vs.")
            home_team = parts[0].strip()
            away_team = parts[1].split("—")[0].strip()

        team_match = re.search(r"Totals\s+(.*?)\s+\(", filename)
        team = team_match.group(1).strip() if team_match else "Unknown"

        # Step 4: Add columns
        df["Season"] = season
        df["Date"] = date_str
        df["Home"] = home_team
        df["Away"] = away_team
        df["TEAM"] = team
        df["source_file"] = filename

        combined.append(df)

    if combined:
        return pd.concat(combined, ignore_index=True)
    else:
        return pd.DataFrame()
