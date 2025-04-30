import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="🏐 Volleyball Team Analytics", layout="wide")

st.title("🏐 Volleyball Team Analytics Dashboard")
st.markdown("""
Welcome to the **Crandall Chargers 2024–25 Volleyball Analytics Platform**.

Use the sidebar to:
- View the full team roster and player bios
- Explore match statistics and setter analysis
- Track fitness progress and more
""")

# Load preview of the roster
csv_path = Path("roster 24-25/team info.csv")

@st.cache_data
def load_roster(path):
    # Try UTF-8 first, fallback to ISO-8859-1 if needed
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
