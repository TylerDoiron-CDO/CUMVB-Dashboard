import streamlit as st
import pandas as pd
import os
from functions import (
    Athlete_Data_Load,
    Overall_Data_Load,
    Rotation_Data_Load,
    Match_Data_Load
)

st.set_page_config(page_title="📂 Raw Data Viewer", layout="wide")

# Summary intro for the full page
st.markdown("""
## 📂 Raw Data Viewer
This page provides full access to the underlying match, rotation, overall, and athlete data used throughout the analytics dashboards.
It is intended for exploratory analysis, enabling filters, downloads, and quick reviews of data trends. Use the navigation below to jump to specific sections.
""")

# Horizontal navigation buttons
nav1, nav2, nav3, nav4, nav5 = st.columns(5)
with nav1:
    if st.button("📘 Match Data"):
        st.experimental_set_query_params(section="match")
with nav2:
    if st.button("📊 Overall Data"):
        st.experimental_set_query_params(section="overall")
with nav3:
    if st.button("🔄 Rotation Data"):
        st.experimental_set_query_params(section="rotation")
with nav4:
    if st.button("🏐 Athlete Data"):
        st.experimental_set_query_params(section="athlete")
with nav5:
    if st.button("📊 Setter Dist. Data"):
        st.experimental_set_query_params(section="setter")

st.markdown("---")

force_refresh_match = st.session_state.get("reset_cache_match", False)

with st.spinner("🔄 Loading Match Data..."):
    match_df = Match_Data_Load.load_preprocessed_match_data(force_rebuild=force_refresh_match)

if match_df.empty:
    st.title("📘 Match Data — No Records Found")
    st.warning("⚠️ No match data found or processed.")
else:
    # Normalize team names
    match_df["Home"] = match_df["Home"].replace({"CU": "Crandall", "Holland College": "Holland"})
    match_df["Away"] = match_df["Away"].replace({"CU": "Crandall", "Holland College": "Holland"})
    match_df["Team"] = match_df["Team"].replace({"CU": "Crandall", "Holland College": "Holland"})

    # Filter for Crandall team only for summary
    crandall_matches = match_df[match_df["Team"] == "Crandall"]
    season_summary = crandall_matches.groupby("Season").size().reset_index(name="Records")

    latest_date = pd.to_datetime(match_df["Date"], errors='coerce').dropna().max()
    latest_date_str = latest_date.date() if pd.notnull(latest_date) else "Unknown"

    # Title with latest date only
    st.title(f"📘 Match Data — Latest Match: {latest_date_str}")

    # Summary section (inline single line)
    summary_line = " | ".join([f"{row['Season']}: {row['Records']} records" for _, row in season_summary.iterrows()])
    st.markdown(f"### 📊 Summary by Season — {summary_line}")

    # Explanation
    st.caption("This dataset includes all point-by-point match data for every set played in the tracked seasons. Summary counts reflect only matches played by Crandall.")

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    seasons = sorted(match_df["Season"].dropna().unique())
    homes = sorted(match_df["Home"].dropna().unique())
    aways = sorted(match_df["Away"].dropna().unique())
    teams = sorted(match_df["Team"].dropna().unique())

    f_season = col1.multiselect("Season", options=seasons)
    f_home = col2.multiselect("Home", options=homes)
    f_away = col3.multiselect("Away", options=aways)
    f_team = col4.multiselect("Team", options=teams)

    filtered_match = match_df.copy()
    if f_season:
        filtered_match = filtered_match[filtered_match["Season"].isin(f_season)]
    if f_home:
        filtered_match = filtered_match[filtered_match["Home"].isin(f_home)]
    if f_away:
        filtered_match = filtered_match[filtered_match["Away"].isin(f_away)]
    if f_team:
        filtered_match = filtered_match[filtered_match["Team"].isin(f_team)]

    st.success(f"✅ {filtered_match.shape[0]} match records shown")
    st.dataframe(filtered_match)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Match CSV", filtered_match.to_csv(index=False).encode("utf-8"), "match_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Match Cache"):
            if os.path.exists(Match_Data_Load.CACHE_FILE):
                os.remove(Match_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_match"] = True
                st.rerun()
            else:
                st.info("ℹ️ No match cache found.")
        st.caption("⚠️ Only use if source match data changed.")

st.markdown("---")

# -------------------------------
# Section 2: Overall Data
# -------------------------------
st.header("📊 Overall Data")

force_refresh_overall = st.session_state.get("reset_cache_overall", False)

with st.spinner("🔄 Loading Overall Data..."):
    overall_df = Overall_Data_Load.load_preprocessed_overall_data(force_rebuild=force_refresh_overall)

if overall_df.empty:
    st.warning("⚠️ No overall data found or processed.")
else:
    # Normalize team names
    overall_df["Home"] = overall_df["Home"].replace({"CU": "Crandall", "Holland College": "Holland"})
    overall_df["Away"] = overall_df["Away"].replace({"CU": "Crandall", "Holland College": "Holland"})
    overall_df["Team"] = overall_df["Team"].replace({"CU": "Crandall", "Holland College": "Holland"})

    if "Matches" in overall_df.columns:
        overall_df = overall_df[overall_df["Matches"].astype(str).str.strip().str.isnumeric()]
        overall_df = overall_df[overall_df["Matches"].astype(int).between(0, 5)]

    col1, col2, col3, col4 = st.columns(4)
    seasons = sorted(overall_df["Season"].dropna().unique())
    homes = sorted(overall_df["Home"].dropna().unique())
    aways = sorted(overall_df["Away"].dropna().unique())
    teams = sorted(overall_df["Team"].dropna().unique())
    f_season = col1.multiselect("Overall Season", options=seasons, key="overall_season")
    f_home = col2.multiselect("Overall Home", options=homes, key="overall_home")
    f_away = col3.multiselect("Overall Away", options=aways, key="overall_away")
    f_team = col4.multiselect("Overall Team", options=teams, key="overall_team")

    filtered_overall = overall_df.copy()
    if f_season:
        filtered_overall = filtered_overall[filtered_overall["Season"].isin(f_season)]
    if f_home:
        filtered_overall = filtered_overall[filtered_overall["Home"].isin(f_home)]
    if f_away:
        filtered_overall = filtered_overall[filtered_overall["Away"].isin(f_away)]
    if f_team:
        filtered_overall = filtered_overall[filtered_overall["Team"].isin(f_team)]

    st.success(f"✅ {filtered_overall.shape[0]} overall records shown")
    st.dataframe(filtered_overall)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Overall CSV", filtered_overall.to_csv(index=False).encode("utf-8"), "overall_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Overall Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()
            else:
                st.info("ℹ️ No overall cache found.")
        st.caption("⚠️ Only use if source overall data changed.")

st.markdown("---")

# -------------------------------
# Section 3: Rotation Data
# -------------------------------
st.header("🔄 Rotation Data")

force_refresh_rotation = st.session_state.get("reset_cache_rotation", False)

with st.spinner("🔄 Loading Rotation Data..."):
    rotation_df = Rotation_Data_Load.load_preprocessed_rotation_data(force_rebuild=force_refresh_rotation)

if rotation_df.empty:
    st.warning("⚠️ No rotation data found or processed.")
else:
    # Normalize team names
    rotation_df["Home"] = rotation_df["Home"].replace({"CU": "Crandall", "Holland College": "Holland"})
    rotation_df["Away"] = rotation_df["Away"].replace({"CU": "Crandall", "Holland College": "Holland"})
    rotation_df["Team"] = rotation_df["Team"].replace({"CU": "Crandall", "Holland College": "Holland"})

    if "Rotation" in rotation_df.columns:
        rotation_df["Rotation_str"] = rotation_df["Rotation"].astype(str).str.strip()
        rotation_df = rotation_df[
            rotation_df["Rotation_str"].isin(["0", "1", "2", "3", "4", "5", "Unknown", "unknown", "nan"])
        ]
        rotation_df.drop(columns=["Rotation_str"], inplace=True, errors="ignore")

    s1, s2, s3, s4 = st.columns(4)
    seasons = sorted(rotation_df["Season"].dropna().unique())
    homes = sorted(rotation_df["Home"].dropna().unique())
    aways = sorted(rotation_df["Away"].dropna().unique())
    teams = sorted(rotation_df["Team"].dropna().unique())
    f_season = s1.multiselect("Rotation Season", options=seasons, key="rotation_season")
    f_home = s2.multiselect("Rotation Home", options=homes, key="rotation_home")
    f_away = s3.multiselect("Rotation Away", options=aways, key="rotation_away")
    f_team = s4.multiselect("Rotation Team", options=teams, key="rotation_team")

    filtered_rotation = rotation_df.copy()
    if f_season:
        filtered_rotation = filtered_rotation[filtered_rotation["Season"].isin(f_season)]
    if f_home:
        filtered_rotation = filtered_rotation[filtered_rotation["Home"].isin(f_home)]
    if f_away:
        filtered_rotation = filtered_rotation[filtered_rotation["Away"].isin(f_away)]
    if f_team:
        filtered_rotation = filtered_rotation[filtered_rotation["Team"].isin(f_team)]

    st.success(f"✅ {filtered_rotation.shape[0]} rotation records shown")
    st.dataframe(filtered_rotation)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.download_button("💾 Download Rotation CSV", filtered_rotation.to_csv(index=False).encode("utf-8"), "rotation_data.csv", "text/csv")
    with c2:
        if st.button("🔁 Reset Rotation Cache"):
            if os.path.exists(Rotation_Data_Load.CACHE_FILE):
                os.remove(Rotation_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_rotation"] = True
                st.rerun()
            else:
                st.info("ℹ️ No rotation cache found.")
        st.caption("⚠️ Only use if source rotation data changed.")

st.markdown("---")

# -------------------------------
# Section 4: Athlete Data
# -------------------------------
st.header("🏐 Athlete Data")

force_refresh_athlete = st.session_state.get("reset_cache_athlete", False)
with st.spinner("🔄 Loading Athlete Data..."):
    athlete_df = Athlete_Data_Load.load_preprocessed_athlete_data(force_rebuild=force_refresh_athlete)

if athlete_df.empty:
    st.warning("⚠️ No athlete data found or processed.")
else:
    # Normalize team names
    athlete_df["Home"] = athlete_df["Home"].replace({"CU": "Crandall", "Holland College": "Holland"})
    athlete_df["Away"] = athlete_df["Away"].replace({"CU": "Crandall", "Holland College": "Holland"})
    athlete_df["Team"] = athlete_df["Team"].replace({"CU": "Crandall", "Holland College": "Holland"})

    # Create combined index column
    if "#" in athlete_df.columns and "Athlete" in athlete_df.columns:
        athlete_df.insert(0, "# - Athlete", athlete_df["#"].astype(str).str.strip() + " - " + athlete_df["Athlete"].astype(str).str.strip())

    with st.expander("🔎 Filter Athlete Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(athlete_df["Season"].dropna().unique())
        teams = sorted(athlete_df["Team"].dropna().unique()) if "Team" in athlete_df.columns else []
        homes = sorted(athlete_df["Home"].dropna().unique())
        aways = sorted(athlete_df["Away"].dropna().unique())
        names = sorted(athlete_df["Athlete"].dropna().unique()) if "Athlete" in athlete_df.columns else []

        s_seasons = col1.multiselect("Athlete Season", options=seasons)
        s_teams = col2.multiselect("Athlete Team", options=teams)
        s_home = col3.multiselect("Athlete Home", options=homes)
        s_away = col4.multiselect("Athlete Away", options=aways)
        s_name = col5.text_input("Search Athlete")

    filtered_athlete = athlete_df.copy()
    if s_seasons:
        filtered_athlete = filtered_athlete[filtered_athlete["Season"].isin(s_seasons)]
    if s_teams:
        filtered_athlete = filtered_athlete[filtered_athlete["Team"].isin(s_teams)]
    if s_home:
        filtered_athlete = filtered_athlete[filtered_athlete["Home"].isin(s_home)]
    if s_away:
        filtered_athlete = filtered_athlete[filtered_athlete["Away"].isin(s_away)]
    if s_name and "Athlete" in filtered_athlete.columns:
        filtered_athlete = filtered_athlete[filtered_athlete["Athlete"].str.contains(s_name, case=False, na=False)]

    st.success(f"✅ {filtered_athlete.shape[0]} athlete records shown")
    latest_athlete_date = pd.to_datetime(filtered_athlete["Date"], errors='coerce').dropna().max()
    if pd.notnull(latest_athlete_date):
        st.markdown(f"**🗓️ Athlete data current as of:** {latest_athlete_date.date()}")

    st.dataframe(filtered_athlete)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button("💾 Download Athlete CSV", filtered_athlete.to_csv(index=False).encode("utf-8"), "athlete_data.csv", "text/csv")
    with col2:
        if st.button("🔁 Reset Athlete Cache"):
            if os.path.exists(Athlete_Data_Load.CACHE_FILE):
                os.remove(Athlete_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_athlete"] = True
                st.rerun()
            else:
                st.info("ℹ️ No athlete cache found.")
        st.caption("⚠️ Only use if source athlete data changed.")

st.markdown("---")

# -------------------------------
# Section 5: Setter Distribution Data
# -------------------------------
st.header("📊 Setter Distribution Data")

setter_file = "data/Setter Distribution Data.csv"

if os.path.exists(setter_file):
    try:
        setter_df = pd.read_csv(setter_file)
        st.success(f"✅ Loaded {setter_df.shape[0]} rows from Setter Distribution Data")
        st.dataframe(setter_df)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "💾 Download Setter Distribution CSV",
                data=setter_df.to_csv(index=False).encode("utf-8"),
                file_name="setter_distribution_data.csv",
                mime="text/csv"
            )
        with col2:
            st.caption("📌 Direct from scouting reports and analytics exports")
    except Exception as e:
        st.error(f"❌ Failed to load Setter Distribution Data: {e}")
else:
    st.warning("⚠️ Setter Distribution file not found at `data/Setter Distribution Data.csv`")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations — Streamlit analytics platform • Crandall Chargers Volleyball © 2025")
