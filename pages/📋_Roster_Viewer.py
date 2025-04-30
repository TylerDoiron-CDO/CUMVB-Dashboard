import streamlit as st
import pandas as pd
import os
from PIL import Image

ROSTER_BASE_DIR = "rosters"
CSV_FILENAME = "team_info.csv"

st.title("📋 Historical Roster Viewer")

# Load all rosters
@st.cache_data
def load_all_rosters():
    all_data = []
    errors = []

    for season_folder in os.listdir(ROSTER_BASE_DIR):
        season_path = os.path.join(ROSTER_BASE_DIR, season_folder)
        csv_path = os.path.join(season_path, CSV_FILENAME)

        if not os.path.isdir(season_path):
            continue

        if not os.path.exists(csv_path):
            errors.append(f"Missing file: {csv_path}")
            continue

        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_path, encoding="ISO-8859-1")
            except Exception as e:
                errors.append(f"{csv_path} could not be read: {e}")
                continue

        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]
        df["season"] = season_folder
        all_data.append(df)

    if not all_data:
        st.error("❌ No valid roster CSVs were found.")
        if errors:
            st.error("Errors encountered:")
            for err in errors:
                st.text(err)
        raise ValueError("No roster data to load.")

    return pd.concat(all_data, ignore_index=True)

# Load and validate
df = load_all_rosters()

# Required columns
required_columns = {"name", "position", "year of eligibility", "height", "hometown", "season"}
missing = required_columns - set(df.columns)

if missing:
    st.error(f"❌ Missing columns: {', '.join(missing)}. Check your team_info.csv files.")
    st.stop()

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
st.subheader("📄 Filtered Roster Data")
st.dataframe(filtered_df.reset_index(drop=True))

# Show headshots (optional)
st.markdown("### 🖼️ Player Headshots")
for _, row in filtered_df.iterrows():
    season_dir = os.path.join(ROSTER_BASE_DIR, row["season"])
    image_files = [
        f for f in os.listdir(season_dir)
        if f.lower().endswith(".jpg") and row["name"].lower() in f.lower()
    ]

    if image_files:
        col1, col2 = st.columns([1, 4])
        img_path = os.path.join(season_dir, image_files[0])
        img = Image.open(img_path)
        col1.image(img, width=120)
        col2.markdown(f"**{row['name']}**")
        col2.markdown(f"- **Season:** {row['season']}")
        col2.markdown(f"- **Position:** {row['position']}")
        col2.markdown(f"- **Height:** {row['height']}")
        col2.markdown(f"- **Eligibility Year:** {row['year of eligibility']}")
        col2.markdown(f"- **Hometown:** {row['hometown']}")
        st.markdown("---")
