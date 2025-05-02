import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="🏐 Volleyball Team Analytics", layout="wide")

st.title("🏐 Volleyball Team Analytics Dashboard")
st.markdown("""
Welcome to the **Crandall Chargers 2024–25 Volleyball Analytics Platform**.

Use the sidebar to:
- View the full team roster and player bios
- Explore match statistics and setter analysis
- Track fitness progress and more
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

# Optional: Team preview if roster file exists
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


