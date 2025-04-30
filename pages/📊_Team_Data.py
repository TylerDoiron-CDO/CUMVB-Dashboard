import streamlit as st
import pandas as pd
import os
from PIL import Image

# -------------------------------
# Page Setup
# -------------------------------

st.set_page_config(page_title="📊 Team Data", layout="wide")
st.title("📊 Team Data Explorer")
st.markdown("This page summarizes performance and roster-wide insights across all seasons.")

st.markdown("---")

# -------------------------------
# Load Combined Roster Data
# -------------------------------

ROSTER_BASE_DIR = "rosters"
CSV_FILENAME = "team_info.csv"

@st.cache_data
def load_all_rosters():
    all_data = []
    for season_folder in os.listdir(ROSTER_BASE_DIR):
        season_path = os.path.join(ROSTER_BASE_DIR, season_folder)
        csv_path = os.path.join(season_path, CSV_FILENAME)

        if not os.path.exists(csv_path):
            continue

        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except:
            df = pd.read_csv(csv_path, encoding="ISO-8859-1")

        df.columns = [col.strip().lower() for col in df.columns]
        rename_map = {
            "no.": "#",
            "name": "name",
            "pos.": "position",
            "yr.": "year",
            "ht.": "height",
            "hometown": "hometown"
        }
        df = df.rename(columns=rename_map)
        df["season"] = season_folder
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)

df = load_all_rosters()

# -------------------------------
# Quick Summary Stats
# -------------------------------

st.subheader("📈 Roster Composition Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Players", len(df))
col2.metric("Seasons Tracked", df["season"].nunique())
col3.metric("Unique Hometowns", df["hometown"].nunique())

st.markdown("---")

# -------------------------------
# Position Breakdown by Season
# -------------------------------

st.subheader("📌 Position Distribution by Season")

pos_counts = df.groupby(["season", "position"]).size().unstack(fill_value=0)
st.dataframe(pos_counts)

st.markdown("---")

# -------------------------------
# Footer
# -------------------------------

st.caption("Advanced analytics powered by Streamlit • Crandall Chargers Volleyball © 2025")
