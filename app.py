import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="🏐 Volleyball Team Analytics", layout="wide")

st.title("🏐 Volleyball Team Analytics Dashboard")
st.markdown("""
Welcome to the **Crandall Chargers 2024–25 Volleyball Analytics Platform**.

Use the sidebar to:
- View the full team roster and player bios
- Explore match statistics and setter analysis
- Track fitness progress and more
""")

st.markdown("---")

st.subheader("🌐 Crandall Chargers – Men's Volleyball Web Portal")

st.markdown("Stay connected with the official [Crandall Chargers Men's Volleyball site](https://www.crandallchargers.ca/sports/mvball/index) for schedules, rosters, and news.")

# Embed webpage (iframe)
components.html(
    """
    <iframe src="https://www.crandallchargers.ca/sports/mvball/index"
            width="100%" height="800px" frameborder="0">
    </iframe>
    """,
    height=800,
)

