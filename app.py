import streamlit as st
import pandas as pd
from pathlib import Path

# Page setup
st.set_page_config(page_title="🏐 Volleyball Team Analytics", layout="wide")

# Sidebar navigation
st.sidebar.title("📂 Navigation")

section = st.sidebar.radio("Select a section:", [
    "🏠 Home",
    "👥 Team Overview",
    "📊 Team Statistics",
    "📈 Individual Statistics",
    "👤 Player Profiles",
    "🏋️ Team Fitness Data",
    "🩺 Wellness Reports",
    "🔍 Scouting Reports",
    "🍽️ Meal Planner",
    "📂 Raw Data"
])

# Page: Home
if section == "🏠 Home":
    st.title("🏐 Volleyball Team Analytics Dashboard")
    st.markdown("""
    Welcome to the **Crandall Chargers 2024–25 Volleyball Analytics Platform**.

    Use the sidebar to:
    - View the full team roster and player bios
    - Explore match statistics and setter analysis
    - Track fitness progress and more
    """)

    # Load team preview
    csv_path = Path("roster 24-25/team info.csv")

    @st.cache_data
    def load_roster(path):
        try:
            return pd.read_csv(path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding='ISO-8859-1')

    if csv_path.exists():
        st.subheader("📋 Team Preview")
        df = load_roster(csv_path)
        st.dataframe(df)
    else:
        st.warning("Roster CSV not found at: roster 24-25/team info.csv")

# Add placeholder messages for other sections — can replace with dynamic imports or page includes
elif section == "👥 Team Overview":
    st.title("👥 Team Overview")
    st.info("This section will summarize team-wide context like roster structure, positions, and eligibility.")

elif section == "📊 Team Statistics":
    st.title("📊 Team Statistics")
    st.info("This section will display team-based match, set, and seasonal stats.")

elif section == "📈 Individual Statistics":
    st.title("📈 Individual Statistics")
    st.info("Explore detailed breakdowns for individual athletes across matches or tests.")

elif section == "👤 Player Profiles":
    st.title("👤 Player Profiles")
    st.info("View player bios, headshots, and custom performance cards.")

elif section == "🏋️ Team Fitness Data":
    st.title("🏋️ Team Fitness Data")
    st.info("Analyze fitness and testing results for each athlete over time.")

elif section == "🩺 Wellness Reports":
    st.title("🩺 Wellness Reports")
    st.info("Monitor athlete recovery, readiness, and self-reported status.")

elif section == "🔍 Scouting Reports":
    st.title("🔍 Scouting Reports")
    st.info("Create or view match-level scouting notes and tactical breakdowns.")

elif section == "🍽️ Meal Planner":
    st.title("🍽️ Athlete Meal Planner")
    st.info("Manage customized nutrition plans for training and recovery.")

elif section == "📂 Raw Data":
    st.title("📂 Raw Data Viewer")
    st.info("Inspect all underlying datasets powering this dashboard.")

