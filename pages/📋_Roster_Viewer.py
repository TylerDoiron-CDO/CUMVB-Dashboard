import streamlit as st
import pandas as pd
import os
from PIL import Image

ROSTER_BASE_DIR = "rosters"
CSV_FILENAME = "team_info.csv"

st.title("📋 Historical Roster Viewer")

# Load all rosters and combine them
@st.cache_data
def load_all_rosters():
    all_data = []
    
    for season_folder in os.listdir(ROSTER_BASE_DIR):
        season_path = os.path.join(ROSTER_BASE_DIR, season_folder)
        csv_path = os.path.join(season_path, CSV_FILENAME)
        
        if not os.path.isdir(season_path) or not os.path.exists(csv_path):
            continue
        
        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="ISO-8859-1")
        
        df["season"] = season_folder
        all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True)

df = load_all_rosters()

# Standardize column names
df.columns = [col.strip().lower() for col in df.columns]

# Display filters
with st.expander("🔎 Filter Options"):
    col1, col2, col3, col4 = st.columns(4)

    selected_seasons = col1.multiselect("Season", sorted(df["season"].unique()), default=df["season"].unique())
    selected_positions = col2.multiselect("Position", sorted(df["position"].dropna().unique()), default=df["position"].dropna().unique())
    selected_years = col3.multiselect("Eligibility Year", sorted(df["year of eligibility"].dropna().unique()), default=df["year of eligibility"].dropna().unique())
    name_search = col4.text_input("Search by name")

# Apply filters
filtered_df = df[
    (df["season"].isin(selected_seasons)) &
    (df["position"].isin(selected_positions)) &
    (df["year of eligibility"].isin(selected_years))
]

if name_search:
    filtered_df = filtered_df[filtered_df["name"].str.contains(name_search, case=False, na=False)]

# Show table
st.dataframe(filtered_df.reset_index(drop=True))

# Optionally display headshots for filtered players
st.markdown("### 🖼️ Headshots (Filtered)")
for _, row in filtered_df.iterrows():
    season_dir = os.path.join(ROSTER_BASE_DIR, row["season"])
    image_candidates = [
        f for f in os.listdir(season_dir)
        if f.lower().endswith(".jpg") and row["name"] in f
    ]

    if image_candidates:
        col1, col2 = st.columns([1, 4])
        img_path = os.path.join(season_dir, image_candidates[0])
        img = Image.open(img_path)
        col1.image(img, width=120)
        col2.markdown(f"**{row['name']}**")
        col2.markdown(f"- **Season:** {row['season']}")
        col2.markdown(f"- **Position:** {row['position']}")
        col2.markdown(f"- **Height:** {row['height']}")
        col2.markdown(f"- **Year of Eligibility:** {row['year of eligibility']}")
        col2.markdown(f"- **Hometown:** {row['hometown']}")
        st.markdown("-----")
