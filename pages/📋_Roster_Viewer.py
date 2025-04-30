import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageOps

ROSTER_BASE_DIR = "rosters"
CSV_FILENAME = "team_info.csv"

# -------------------------------
# Filtered Data Table
# -------------------------------

st.title("📋 Historical Roster Viewer")

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

        # Normalize and rename columns
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

    if not all_data:
        st.error("❌ No valid roster CSVs were found.")
        if errors:
            st.error("Errors encountered:")
            for err in errors:
                st.text(err)
        raise ValueError("No roster data to load.")

    return pd.concat(all_data, ignore_index=True)

# Load and validate data
df = load_all_rosters()

required_columns = {"name", "position", "year", "height", "hometown", "#", "season"}
missing = required_columns - set(df.columns)

if missing:
    st.error(f"❌ Missing columns: {', '.join(missing)}. Check your team_info.csv files.")
    st.stop()

# 🔎 Filter UI — starts with nothing selected
with st.expander("🔎 Filter Options"):
    col1, col2, col3, col4 = st.columns(4)

    all_seasons = sorted(df["season"].dropna().unique())
    all_positions = sorted(df["position"].dropna().unique())
    all_years = sorted(df["year"].dropna().unique())

    selected_seasons = col1.multiselect("Season", options=all_seasons)
    selected_positions = col2.multiselect("Position", options=all_positions)
    selected_years = col3.multiselect("Year", options=all_years)
    name_search = col4.text_input("Search by name")

# 🧠 Smart Filtering Logic (empty = all)
filtered_df = df.copy()

if selected_seasons:
    filtered_df = filtered_df[filtered_df["season"].isin(selected_seasons)]

if selected_positions:
    filtered_df = filtered_df[filtered_df["position"].isin(selected_positions)]

if selected_years:
    filtered_df = filtered_df[filtered_df["year"].isin(selected_years)]

if name_search:
    filtered_df = filtered_df[filtered_df["name"].str.contains(name_search, case=False, na=False)]

# 📄 Filtered Roster Table
st.subheader("📄 Filtered Roster Data")
st.dataframe(filtered_df.reset_index(drop=True))

st.markdown("---")

# -------------------------------
# Player Headshots
# -------------------------------

# 🖼️ Grouped Headshots by Player Across Seasons
st.markdown("### 🖼️ Player Headshots by Season")

# Ensure season is a string for sorting
df["season"] = df["season"].astype(str)
filtered_df["season"] = filtered_df["season"].astype(str)

# Group by player name
grouped = filtered_df.groupby("name")

for name, group in grouped:
    st.markdown(f"## {name}")
    group = group.dropna(subset=["season"])
    group = group.sort_values("season").head(5)
    cols = st.columns(len(group))

    for idx, (_, row) in enumerate(group.iterrows()):
        season_dir = os.path.join(ROSTER_BASE_DIR, row["season"])
        jersey = str(row["#"]).strip()
        name_clean = str(row["name"]).strip()
        expected_filename = f"{jersey} - {name_clean}".lower()

        # Match case-insensitive .jpg or .jpeg
        matched_image = None
        for f in os.listdir(season_dir):
            fname, ext = os.path.splitext(f.lower())
            if fname.strip() == expected_filename and ext in [".jpg", ".jpeg"]:
                matched_image = os.path.join(season_dir, f)
                break

        with cols[idx]:
            if matched_image and os.path.exists(matched_image):
                img = Image.open(matched_image)
                # Resize and crop to 150x200
                img = ImageOps.fit(img, (150, 200), method=Image.Resampling.LANCZOS)
                st.image(img, caption=row["season"])
            else:
                st.warning("No image")
                st.caption(row["season"])

            st.markdown(f"**#{jersey}**")
            st.markdown(f"{row['position']}, {row['height']}")
            st.markdown(f"Year: {row['year']}")
            st.markdown(f"{row['hometown']}")

st.markdown("---")

# -------------------------------
# Footer
# -------------------------------

st.caption("Advanced analytics powered by by Astute Innovations & Streamlit • Crandall Chargers Men's Volleyball © 2025")
