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

