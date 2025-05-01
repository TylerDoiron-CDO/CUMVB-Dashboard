import streamlit as st
import pandas as pd
import os
from functions import (
    Athlete_Data_Load,
    Overall_Data_Load,
    Rotation_Data_Load,
    Match_Data_Load
)

st.set_page_config(page_title="📂 Raw Data Viewer – For Exploratory Analysis", layout="wide")

# 🔎 Page Introduction
st.markdown("""
## 📂 Raw Data Viewer – For Exploratory Analysis
This page provides access to the full underlying match, rotation, overall, athlete, and setter distribution datasets. 
Use this space for filtering, exploration, and validating raw data powering all dashboards.
""")

st.markdown("---")

# --- Navigation anchor logic ---
section = st.query_params.get("section", None)
if isinstance(section, list):
    section = section[0]

# --- Navigation buttons ---
match_total, match_latest = 0, "N/A"
overall_total, overall_latest = 0, "N/A"
rotation_total, rotation_latest = 0, "N/A"
athlete_total, athlete_latest = 0, "N/A"

# Preload summaries
from functions import (
    Match_Data_Load,
    Overall_Data_Load,
    Rotation_Data_Load,
    Athlete_Data_Load,
)

def get_summary(load_func):
    try:
        df = load_func(force_rebuild=False)
        total = df.shape[0]
        latest = pd.to_datetime(df["Date"], errors='coerce').dropna().max()
        return total, latest.strftime("%Y-%m-%d") if pd.notnull(latest) else "N/A"
    except:
        return 0, "N/A"

match_total, match_latest = get_summary(Match_Data_Load.load_preprocessed_match_data)
overall_total, overall_latest = get_summary(Overall_Data_Load.load_preprocessed_overall_data)
rotation_total, rotation_latest = get_summary(Rotation_Data_Load.load_preprocessed_rotation_data)
athlete_total, athlete_latest = get_summary(Athlete_Data_Load.load_preprocessed_athlete_data)

# CSS & JavaScript for scroll behavior and tight spacing
st.markdown("""
<style>
.scroll-target {
    position: relative;
    top: -60px;
    margin: 0;
    padding: 0;
}
.nav-container {
    display: flex;
    justify-content: space-around;
    margin-top: -4em;
    margin-bottom: -6.5em;
}
.nav-box {
    text-align: center;
}
button.nav-button {
    padding: 0.5em 1em;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
}
</style>
<script>
    function scrollToSection(id) {
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
</script>
""", unsafe_allow_html=True)

st.markdown("""
<div class="nav-container">
  <div class="nav-box">
    <button class="nav-button" onclick="scrollToSection('match-data-section')">📘 Match Data</button><br>
    <strong>{} records</strong><br>
    <small>Latest: {}</small>
  </div>
  <div class="nav-box">
    <button class="nav-button" onclick="scrollToSection('overall-data-section')">📊 Overall Data</button><br>
    <strong>{} records</strong><br>
    <small>Latest: {}</small>
  </div>
  <div class="nav-box">
    <button class="nav-button" onclick="scrollToSection('rotation-data-section')">🔄 Rotation Data</button><br>
    <strong>{} records</strong><br>
    <small>Latest: {}</small>
  </div>
  <div class="nav-box">
    <button class="nav-button" onclick="scrollToSection('athlete-data-section')">🏐 Athlete Data</button><br>
    <strong>{} records</strong><br>
    <small>Latest: {}</small>
  </div>
  <div class="nav-box">
    <button class="nav-button" onclick="scrollToSection('setter-dist-data-section')">📊 Setter Dist. Data</button><br>
    <strong>Dynamic load</strong><br>
    <small>Via CSV</small>
  </div>
</div>
""".format(
    match_total, match_latest,
    overall_total, overall_latest,
    rotation_total, rotation_latest,
    athlete_total, athlete_latest
), unsafe_allow_html=True)

# Anchors for scrolling target
st.markdown("""<div class='scroll-target' id='match-data-section'></div>""", unsafe_allow_html=True)
st.markdown("""<div class='scroll-target' id='overall-data-section'></div>""", unsafe_allow_html=True)
st.markdown("""<div class='scroll-target' id='rotation-data-section'></div>""", unsafe_allow_html=True)
st.markdown("""<div class='scroll-target' id='athlete-data-section'></div>""", unsafe_allow_html=True)
st.markdown("""<div class='scroll-target' id='setter-dist-data-section'></div>""", unsafe_allow_html=True)

# Remove spacing before the line
st.markdown("""<div style='margin-top: -100px;'></div>""", unsafe_allow_html=True)

# Separator line
st.markdown("---")

# -------------------------------
# Section 1: Match Data
# -------------------------------
st.header("📘 Match Data")

force_refresh_match = st.session_state.get("reset_cache_match", False)

with st.spinner("🔄 Loading Match Data..."):
    match_df = Match_Data_Load.load_preprocessed_match_data(force_rebuild=force_refresh_match)

if match_df.empty:
    st.warning("⚠️ No match data found or processed.")
else:
    # Normalize team names
    match_df["Home"] = match_df["Home"].replace({"CU": "Crandall", "Holland College": "Holland"})
    match_df["Away"] = match_df["Away"].replace({"CU": "Crandall", "Holland College": "Holland"})
    match_df["Team"] = match_df["Team"].replace({"CU": "Crandall", "Holland College": "Holland"})

    # Caption summary
    st.caption("This dataset includes all point-by-point match data for every set played in the tracked seasons.")

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

    # Create combined index column without decimal padding
    if "#" in athlete_df.columns and "Athlete" in athlete_df.columns:
        athlete_df.insert(0, "# - Athlete", athlete_df["#"].apply(lambda x: str(int(float(x))) if pd.notnull(x) and str(x).replace('.', '', 1).isdigit() else str(x)) + " - " + athlete_df["Athlete"].astype(str).str.strip())

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

        # Filters
        f1, f2, f3, f4, f5 = st.columns(5)
        teams = sorted(setter_df["Team"].dropna().unique())
        homes = sorted(setter_df["Home"].dropna().unique()) if "Home" in setter_df.columns else []
        aways = sorted(setter_df["Away"].dropna().unique()) if "Away" in setter_df.columns else []
        tendencies = sorted(setter_df["Setter Tendency"].dropna().unique()) if "Setter Tendency" in setter_df.columns else []
        positions = sorted(setter_df["Position"].dropna().unique()) if "Position" in setter_df.columns else []

        f_team = f1.multiselect("Team", options=teams)
        f_home = f2.multiselect("Home", options=homes)
        f_away = f3.multiselect("Away", options=aways)
        f_tend = f4.multiselect("Setter Tendency", options=tendencies)
        f_pos  = f5.multiselect("Position", options=positions)

        filtered_setter_df = setter_df.copy()
        if f_team:
            filtered_setter_df = filtered_setter_df[filtered_setter_df["Team"].isin(f_team)]
        if f_home and "Home" in filtered_setter_df.columns:
            filtered_setter_df = filtered_setter_df[filtered_setter_df["Home"].isin(f_home)]
        if f_away and "Away" in filtered_setter_df.columns:
            filtered_setter_df = filtered_setter_df[filtered_setter_df["Away"].isin(f_away)]
        if f_tend and "Setter Tendency" in filtered_setter_df.columns:
            filtered_setter_df = filtered_setter_df[filtered_setter_df["Setter Tendency"].isin(f_tend)]
        if f_pos and "Position" in filtered_setter_df.columns:
            filtered_setter_df = filtered_setter_df[filtered_setter_df["Position"].isin(f_pos)]

        st.success(f"✅ Showing {filtered_setter_df.shape[0]} filtered rows from Setter Distribution Data")
        st.dataframe(filtered_setter_df)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "💾 Download Setter Distribution CSV",
                data=filtered_setter_df.to_csv(index=False).encode("utf-8"),
                file_name="setter_distribution_data.csv",
                mime="text/csv"
            )
        with col2:
            st.caption("📌 Direct from scouting reports and analytics exports")
    except Exception as e:
        st.error(f"❌ Failed to load Setter Distribution Data: {e}")
else:
    st.warning("⚠️ Setter Distribution file not found at data/Setter Distribution Data.csv")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Developed by Astute Innovations — Streamlit analytics platform • Crandall Chargers Volleyball © 2025")
