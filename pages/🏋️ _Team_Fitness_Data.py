
# Cleaned and structured version of the Team Fitness Data Streamlit page

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")
st.title("💪 Team Fitness Data")
st.markdown("""
Explore physical performance metrics and longitudinal testing for all athletes.

Use the filters below to refine the dataset and navigate through interactive visualizations to monitor progress, spot trends, and evaluate individual and team-wide improvements.
""")

# Load and prepare data
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

# Filtering UI
if not df.empty:
    st.markdown("### 🔍 Filter Options")
    col1, col2, col3 = st.columns(3)
    f_athlete = col1.multiselect("Athlete", sorted(df["Athlete"].dropna().unique()))
    f_position = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()))
    f_date = col3.multiselect("Testing Date", sorted(df["Testing Date"].dropna().unique()))

    filtered_df = df.copy()
    if f_athlete:
        filtered_df = filtered_df[filtered_df["Athlete"].isin(f_athlete)]
    if f_position:
        filtered_df = filtered_df[filtered_df["Primary Position"].isin(f_position)]
    if f_date:
        filtered_df = filtered_df[filtered_df["Testing Date"].isin(f_date)]

    st.success(f"✅ {filtered_df.shape[0]} testing records shown")
    st.subheader("📋 Raw Fitness Testing Data")
    st.dataframe(filtered_df, use_container_width=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("💾 Download Fitness CSV", filtered_df.to_csv(index=False).encode("utf-8"), "team_fitness_data.csv", "text/csv")
    with col_d2:
        if st.button("🔁 Reset Fitness Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Reloading data...")
            st.rerun()
else:
    st.warning("No data available.")

# Visualization Tabs
st.markdown("## 📊 Athlete Testing Visualizations")

df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")
metric_cols = df.select_dtypes(include="number").columns.tolist()
athlete_list = sorted(df["Athlete"].dropna().unique())

tabs = st.tabs(["📈 Line Plot", "📦 Box/Violin", "🕸 Radar Chart", "🔁 Delta", "📉 Correlation", "⚖️ Z-Score"])

# Tab 1: Line Plot
with tabs[0]:
    st.markdown("### 📈 Track Athlete Progress")

    # Metric label mapping
    metric_map = {
        'Height (in.)': 'Height', 'Weight (lbs)': 'Weight',
        'Block Touch (in.)': 'Block Touch', 'Approach Touch (in.)': 'Approach Touch',
        'Broad Jump (in.)': 'Broad Jump', 'Block Vertical (in.)': 'Block Vertical',
        'Approach Vertical (in.)': 'Approach Vertical', 'Reps at E[X] Bench': 'Reps @ E[X] Bench',
        'Agility Test (s)': 'Agility Test', '10 Down and Backs (s)': '10 Down and Backs',
        'Yo-Yo Cardio Test': 'Yo-Yo Test'
    }
    inverse_map = {v: k for k, v in metric_map.items()}
    tracked_metrics = list(inverse_map.keys())

    # Filters with unique keys
    col1, col2, col3 = st.columns(3)
    selected_metric = col1.selectbox("Metric", tracked_metrics, key="lineplot_metric_unique")
    selected_athletes = col2.multiselect("Athletes", athlete_list, key="lineplot_athletes_unique")
    selected_positions = col3.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="lineplot_position_unique")

    chart_df = df.copy()
    if selected_athletes:
        chart_df = chart_df[chart_df["Athlete"].isin(selected_athletes)]
    if selected_positions:
        chart_df = chart_df[chart_df["Primary Position"].isin(selected_positions)]

    if not chart_df.empty:
        raw_metric = inverse_map[selected_metric]
        fig = px.line(chart_df, x="Testing Date", y=raw_metric, color="Athlete", markers=True, line_shape="spline")
        fig.update_layout(height=500, title=f"{selected_metric} Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for this combination.")

# Tab 2: Box + Violin Plot
with tabs[1]:
    st.markdown("### 📦 Distribution by Testing Date")
    col1, col2 = st.columns(2)
    selected = col1.selectbox("Metric", metric_cols)
    mode = col2.radio("Chart Type", ["Box", "Violin"], horizontal=True)
    ddf = df.dropna(subset=["Testing Date", selected])
    ddf["Testing Date"] = ddf["Testing Date"].dt.strftime("%Y-%m-%d")

    fig = px.box(ddf, x="Testing Date", y=selected, points="all") if mode == "Box" else px.violin(ddf, x="Testing Date", y=selected, box=True, points="all")
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Radar Chart
with tabs[2]:
    st.markdown("### 🕸 Radar Chart – Athlete Profile Over Time")
    radar_athlete = st.selectbox("Athlete", athlete_list, key="radar_ath")
    radar_data = df[df["Athlete"] == radar_athlete].copy().dropna(subset=list(metric_map.keys()), how="any")

    if radar_data.empty:
        st.warning("⚠️ No complete test sets available for this athlete.")
    else:
        fig = go.Figure()
        for _, row in radar_data.iterrows():
            values = row[list(metric_map.keys())]
            values.index = list(metric_map.values())
            fig.add_trace(go.Scatterpolar(
                r=values.values, theta=values.index, fill='toself',
                name=row["Testing Date"].strftime("%Y-%m-%d")
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# Tab 4: Progress Delta
with tabs[3]:
    st.markdown("### 🔁 Change Over Time – First vs Last Test")
    delta_metric = st.selectbox("Metric", metric_cols, key="delta_metric")
    delta_df = df[["Athlete", "Testing Date", delta_metric]].dropna()
    delta_df.sort_values(by=["Athlete", "Testing Date"], inplace=True)

    summary = (
        delta_df.groupby("Athlete")
        .agg(first=("Testing Date", "first"), last=("Testing Date", "last"))
        .join(delta_df.groupby("Athlete")[delta_metric].agg(first_val="first", last_val="last"))
    )
    summary["% Change"] = 100 * (summary["last_val"] - summary["first_val"]) / summary["first_val"]
    summary = summary.sort_values(by="% Change", ascending=False).dropna()

    fig = px.bar(summary, x=summary.index, y="% Change", color="% Change",
                 title=f"Improvement in {delta_metric}")
    st.plotly_chart(fig, use_container_width=True)

# Tab 5: Correlation Heatmap
with tabs[4]:
    st.markdown("### 📉 Fitness Metric Correlations")
    corr = df[metric_cols].dropna().corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# Tab 6: Z-Score Tracker
with tabs[5]:
    st.markdown("### ⚖️ Z-Score Normalization")
    z_metric = st.selectbox("Metric", metric_cols, key="zscore_metric")
    z_athletes = st.multiselect("Athletes", athlete_list, default=athlete_list[:3], key="zscore_ath")

    z_df = df[df["Athlete"].isin(z_athletes)][["Athlete", "Testing Date", z_metric]].dropna()
    z_df["Z-Score"] = z_df.groupby("Testing Date")[z_metric].transform(lambda x: (x - x.mean()) / x.std(ddof=0))

    fig = px.line(z_df, x="Testing Date", y="Z-Score", color="Athlete", markers=True,
                  title=f"Z-Score Progress of {z_metric}")
    st.plotly_chart(fig, use_container_width=True)
