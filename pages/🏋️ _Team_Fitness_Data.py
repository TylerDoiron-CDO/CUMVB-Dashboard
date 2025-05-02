# 💪 Team Fitness Data – Full Streamlit App with Utility Buttons

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# ✅ Must be first
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")

# --- Utility Function: Chart + CSV + Cache ---
def render_utilities(df, fig=None, filename="export", include_csv=True):
    col1, col2, col3 = st.columns([1, 1, 1])

    if include_csv:
        with col1:
            st.download_button(
                "💾 Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name=f"{filename}.csv",
                mime="text/csv"
            )

    if fig:
        with col2:
            buffer = BytesIO()
            fig.write_image(buffer, format="pdf")
            b64 = base64.b64encode(buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">📄 Download Chart PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

    with col3:
        if st.button(f"🔁 Clear Cache for {filename}"):
            st.cache_data.clear()
            st.experimental_rerun()

# --- Load Data ---
@st.cache_data
def load_testing_data():
    try:
        df = pd.read_csv("data/Testing Data.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Failed to load Testing Data: {e}")
        return pd.DataFrame()

df = load_testing_data()
if df.empty:
    st.warning("⚠️ No data available.")
    st.stop()

# --- Preprocess ---
df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")
metric_cols = df.select_dtypes(include="number").columns.tolist()
athlete_list = sorted(df["Athlete"].dropna().unique())

metric_map = {
    'Height (in.)': 'Height', 'Weight (lbs)': 'Weight',
    'Block Touch (in.)': 'Block Touch', 'Approach Touch (in.)': 'Approach Touch',
    'Broad Jump (in.)': 'Broad Jump', 'Block Vertical (in.)': 'Block Vertical',
    'Approach Vertical (in.)': 'Approach Vertical', 'Reps at E[X] Bench': 'Reps @ E[X] Bench',
    'Agility Test (s)': 'Agility Test', '10 Down and Backs (s)': '10 Down and Backs',
    'Yo-Yo Cardio Test': 'Yo-Yo Test'
}
inverse_map = {v: k for k, v in metric_map.items()}
tracked_metrics = sorted(list(inverse_map.keys()))

# --- Header ---
st.title("💪 Team Fitness Data")
st.markdown("""
Explore physical performance metrics and longitudinal testing for all athletes.

Navigate through interactive visualizations to monitor progress, spot trends, and evaluate individual and team-wide improvements.
""")

# --- Tabs ---
st.markdown("---")
tabs = st.tabs(["\ud83d\udcc8 Line Plot", "\ud83d\udce6 Box/Violin", "\ud83d\udd38 Radar Chart", "\ud83d\udd01 Delta", "\ud83d\udcc9 Correlation", "\u2696\ufe0f Z-Score"])

# --- Tab 1: Line Plot ---
with tabs[0]:
    st.markdown("### \ud83d\udcc8 Track Athlete Progress")
    col1, col2, col3 = st.columns(3)
    selected_metric = col1.selectbox("Metric", tracked_metrics, key="lineplot_metric")
    selected_athletes = col2.multiselect("Athletes", athlete_list, key="lineplot_athletes")
    selected_positions = col3.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="lineplot_positions")

    chart_df = df.copy()
    if selected_athletes:
        chart_df = chart_df[chart_df["Athlete"].isin(selected_athletes)]
    if selected_positions:
        chart_df = chart_df[chart_df["Primary Position"].isin(selected_positions)]

    raw_metric = inverse_map[selected_metric]
    chart_df = chart_df.dropna(subset=["Testing Date", raw_metric])
    chart_df["Testing Date"] = pd.to_datetime(chart_df["Testing Date"], errors="coerce")

    if not chart_df.empty:
        fig = px.line(
            chart_df,
            x="Testing Date",
            y=raw_metric,
            color="Athlete",
            markers=True,
            line_shape="spline",
            title=f"{selected_metric} Over Time"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### \ud83d\udccb Detailed Athlete Records")
        display_table = chart_df[["Athlete", "Primary Position", "Testing Date", raw_metric]].copy()
        display_table = display_table.rename(columns={
            "Athlete": "Name",
            "Primary Position": "Position",
            "Testing Date": "Date",
            raw_metric: selected_metric
        }).sort_values(by="Date", ascending=False)
        st.dataframe(display_table, use_container_width=True, hide_index=True)

        render_utilities(display_table, fig, filename="line_plot")
    else:
        st.info("No data available for the selected filters.")



