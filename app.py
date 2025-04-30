import streamlit as st
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

# Optionally preview roster
csv_path = Path("roster 24-25/team info.csv")
if csv_path.exists():
    st.subheader("📋 Team Preview")
    df = st.cache_data(pd.read_csv)(csv_path)
    st.dataframe(df)
