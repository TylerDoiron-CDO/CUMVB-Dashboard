import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="🏐 Volleyball Team Analytics", layout="wide")

# Header
st.title("🏐 Crandall Chargers Volleyball Analytics Platform")
st.markdown("""
Welcome to the **official analytics platform for the Crandall Chargers Men's Volleyball program (2025–26 season)**.  
This tool is designed to empower coaches, athletes, and staff with actionable insights across all aspects of performance.

---

### 📌 What You Can Do:
- 🧑‍💼 **Player Profiles**: Browse bios, positions, eligibility, and individual data
- 📈 **Performance Analytics**: Track match stats, trends, and comparative insights
- 🏋️ **Fitness Testing**: Monitor physical benchmarks over time
- 🩺 **Wellness & Recovery**: Stay on top of health, readiness, and athlete input
- 📊 **Team + Individual Dashboards**: Dig into detailed metrics by player or unit
- 🧠 **Scouting & Strategy**: Prepare with tactical breakdowns and external reports
- 🍽️ **Meal & Recovery Planning**: Integrate nutrition and routine tracking
- 📂 **Raw Data Access**: Explore the underlying datasets that power every chart

---

Use the **sidebar** to navigate between modules. This dashboard is continuously evolving to support high-performance decision-making on and off the court.
""")
# Divider
st.markdown("---")

# Section 1 – Crandall Chargers Site
st.subheader("📍 Crandall Chargers – Men's Volleyball")
st.markdown("""
Stay connected with the official [Crandall Chargers Men's Volleyball site](https://www.crandallchargers.ca/sports/mvball/index) for up-to-date schedules, rosters, and news.
""")

components.html(
    """
    <div style="border: 1px solid #ccc; border-radius: 8px; overflow: hidden;">
        <iframe src="https://www.crandallchargers.ca/sports/mvball/index"
                width="100%" height="600px" frameborder="0"
                style="border: none;">
        </iframe>
    </div>
    """,
    height=600,
)

st.markdown("---")

# Section 2 – ACAA League Hub
st.subheader("🏆 ACAA Men's Volleyball Central Hub")
st.markdown("""
Explore standings, league leaders, and match results across the ACAA conference via the [ACAA Men's Volleyball site](https://acaa.ca/sports/mvball/index).
""")

components.html(
    """
    <div style="border: 1px solid #ccc; border-radius: 8px; overflow: hidden;">
        <iframe src="https://acaa.ca/sports/mvball/index"
                width="100%" height="600px" frameborder="0"
                style="border: none;">
        </iframe>
    </div>
    """,
    height=600,
)

st.markdown("---")

