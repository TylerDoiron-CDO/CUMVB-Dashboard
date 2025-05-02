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
# Roster Composition Overview
# -------------------------------

st.subheader("📈 Roster Composition Overview")

# Helper to convert height to inches
def convert_height_to_inches(ht):
    try:
        parts = ht.strip().replace('"', '').split("'")
        feet = int(parts[0])
        inches = int(parts[1]) if len(parts) > 1 else 0
        return feet * 12 + inches
    except:
        return None

# Ensure height_in exists
if "height_in" not in df.columns:
    df["height_in"] = df["height"].apply(convert_height_to_inches)

# Calculate stats
avg_height_in = df["height_in"].dropna().mean()
avg_feet = int(avg_height_in) // 12
avg_inches = int(round(avg_height_in % 12))

total_players = len(df)
unique_seasons = df["season"].nunique()
unique_hometowns = df["hometown"].nunique()
unique_positions = df["position"].nunique()
avg_players_per_season = round(total_players / unique_seasons, 1) if unique_seasons else 0

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Players", total_players)
col2.metric("Seasons Tracked", unique_seasons)
col3.metric("Unique Hometowns", unique_hometowns)

col4, col5, col6 = st.columns(3)
col4.metric("Avg Height", f"{avg_feet}'{avg_inches}\" ({round(avg_height_in, 1)} in)")
col5.metric("Avg Players / Season", avg_players_per_season)
col6.metric("Positions Used", unique_positions)

st.markdown("---")

# -------------------------------
# Position Breakdown by Season
# -------------------------------

st.subheader("📌 Position Distribution by Season")

pos_counts = df.groupby(["season", "position"]).size().unstack(fill_value=0)
st.dataframe(pos_counts)

st.markdown("---")

# -------------------------------
# Average Height by Average Height by Position (Grouped by Season)
# -------------------------------

import plotly.graph_objects as go

st.subheader("📏 Average Height by Position (Grouped by Season)")

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

# Drop missing data
valid_df = df.dropna(subset=["height_in", "position", "season"])

# Group by season + position
avg_height = (
    valid_df
    .groupby(["season", "position"])["height_in"]
    .mean()
    .reset_index()
    .sort_values("position")
)

# Unique axes values
positions = sorted(avg_height["position"].unique())
seasons = sorted(avg_height["season"].unique())

# One trace per season
traces = []
for season in seasons:
    season_data = avg_height[avg_height["season"] == season]
    heights = [season_data[season_data["position"] == pos]["height_in"].values[0] if pos in season_data["position"].values else None for pos in positions]

    traces.append(go.Bar(
        name=season,
        y=positions,
        x=heights,
        orientation='h'
    ))

# Plotly figure
fig = go.Figure(data=traces)
fig.update_layout(
    barmode='group',
    title="Average Player Height by Position (Grouped by Season)",
    xaxis_title="Average Height (inches)",
    yaxis_title="Position",
    height=500,
    plot_bgcolor="#fafafa",
    paper_bgcolor="#fafafa"
)

st.plotly_chart(fig, use_container_width=True)


st.markdown("---")

# -------------------------------
# Average Height by Average Height by Position (Grouped by Year)
# -------------------------------

st.subheader("📏 Average Height by Position (Grouped by Eligibility Year)")

# Ensure height_in exists
def convert_height_to_inches(ht):
    try:
        parts = ht.strip().replace('"', '').split("'")
        feet = int(parts[0])
        inches = int(parts[1]) if len(parts) > 1 else 0
        return feet * 12 + inches
    except:
        return None

if "height_in" not in df.columns:
    df["height_in"] = df["height"].apply(convert_height_to_inches)

# Filter and group
valid_df = df.dropna(subset=["height_in", "position", "year"])

avg_height = (
    valid_df
    .groupby(["year", "position"])["height_in"]
    .mean()
    .reset_index()
    .sort_values("position")
)

# Unique values
positions = sorted(avg_height["position"].unique())
years = sorted(avg_height["year"].unique())

# Build horizontal grouped bar chart
traces = []
for year in years:
    year_data = avg_height[avg_height["year"] == year]
    heights = [
        year_data[year_data["position"] == pos]["height_in"].values[0]
        if pos in year_data["position"].values else None
        for pos in positions
    ]

    traces.append(go.Bar(
        name=f"Year {year}",
        y=positions,
        x=heights,
        orientation='h'
    ))

fig = go.Figure(data=traces)
fig.update_layout(
    barmode='group',
    title="Average Height by Position (Grouped by Eligibility Year)",
    xaxis_title="Average Height (inches)",
    yaxis_title="Position",
    height=500,
    plot_bgcolor="#fafafa",
    paper_bgcolor="#fafafa"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations - Advanced analytics powered by Streamlit • Crandall Chargers Volleyball © 2025")
st.markdown("---")
