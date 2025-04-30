import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# Average Height by Position and Year (Grouped Bar Chart)
# -------------------------------

import plotly.express as px

st.subheader("📏 Average Height by Position (Grouped by Year)")

# Convert height to inches
def convert_height_to_inches(ht):
    try:
        parts = ht.strip().replace('"', '').split("'")
        feet = int(parts[0])
        inches = int(parts[1]) if len(parts) > 1 else 0
        return feet * 12 + inches
    except:
        return None

df["height_in"] = df["height"].apply(convert_height_to_inches)

# Drop missing values
valid_df = df.dropna(subset=["height_in", "position", "year"])

# Group average height by position and year
avg_height = (
    valid_df
    .groupby(["position", "year"])["height_in"]
    .mean()
    .reset_index()
)

# Plotly horizontal grouped bar chart
fig = px.bar(
    avg_height,
    y="position",
    x="height_in",
    color="year",
    orientation="h",  # Horizontal bars
    text=avg_height["height_in"].round(1),
    labels={
        "position": "Position",
        "height_in": "Average Height (inches)",
        "year": "Year"
    },
    title="Average Player Height by Position and Year"
)

fig.update_traces(textposition="outside")

# 🔥 This is what makes them appear side-by-side (NOT stacked)
fig.update_layout(
    barmode="group",
    height=500,
    xaxis_title="Average Height (inches)",
    yaxis_title="Position",
    plot_bgcolor="#fafafa",
    paper_bgcolor="#fafafa",
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------

st.caption("Advanced analytics powered by Streamlit • Crandall Chargers Volleyball © 2025")
