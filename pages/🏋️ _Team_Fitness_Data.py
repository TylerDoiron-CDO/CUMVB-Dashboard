import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")
st.title("💪 Team Fitness Data")
st.markdown(\"""
Explore physical performance metrics and longitudinal fitness testing for all athletes.

Use filters below to narrow your view. This page includes raw data, interactive charts, and high-level insights across all test dates.
\""")

# --- Load Fitness Testing Data ---
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

# --- Filtering Panel ---
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
        st.download_button("💾 Download Fitness CSV",
                           filtered_df.to_csv(index=False).encode("utf-8"),
                           "team_fitness_data.csv",
                           "text/csv")
    with col_d2:
        if st.button("🔁 Reset Fitness Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Reloading data...")
            st.rerun()
else:
    st.warning("No data available.")

# --- Prepare for Visuals ---
df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")
metric_cols = df.select_dtypes(include="number").columns.tolist()
athlete_list = sorted(df["Athlete"].dropna().unique())
dates = sorted(df["Testing Date"].dropna().unique())

# --- Tabs for Visualizations ---
st.markdown("## 📊 Athlete Testing Visualizations")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Line Plot", "📦 Box + Violin", "🕸 Radar Chart",
    "🔁 Progress Delta", "📉 Correlation Heatmap", "⚖️ Z-Score Tracker"
])

# Metric Display Map
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

# --- 📈 Line Plot ---
with tab1:
    st.markdown("### 📈 Track Athlete Progress Over Time")
    col1, col2, col3 = st.columns(3)
    selected_metric = col1.selectbox("Metric", tracked_metrics, key="lineplot_metric")
    selected_athletes = col2.multiselect("Athlete", athlete_list, key="lineplot_athletes")
    selected_positions = col3.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="lineplot_positions")

    line_df = df.copy()
    if selected_athletes:
        line_df = line_df[line_df["Athlete"].isin(selected_athletes)]
    if selected_positions:
        line_df = line_df[line_df["Primary Position"].isin(selected_positions)]

    raw_metric = inverse_map[selected_metric]
    line_df = line_df.dropna(subset=["Testing Date", raw_metric])

    if not line_df.empty:
        fig = px.line(line_df, x="Testing Date", y=raw_metric, color="Athlete",
                      markers=True, line_shape="spline", title=f"{selected_metric} Over Time")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for selected inputs.")

# --- 📦 Box + Violin Plot ---
with tab2:
    st.markdown("### 📦 Distribution of Test Results")
    col1, col2 = st.columns(2)
    metric = col1.selectbox("Metric", metric_cols, key="violin_metric")
    chart_type = col2.radio("Chart Type", ["Box Plot", "Violin Plot"], horizontal=True)

    dist_df = df.dropna(subset=["Testing Date", metric])
    dist_df["Testing Date"] = dist_df["Testing Date"].dt.strftime("%Y-%m-%d")

    if chart_type == "Box Plot":
        fig = px.box(dist_df, x="Testing Date", y=metric, points="all", title=f"{metric} Distribution")
    else:
        fig = px.violin(dist_df, x="Testing Date", y=metric, box=True, points="all", title=f"{metric} Distribution")
    st.plotly_chart(fig, use_container_width=True)

# --- 🕸 Radar Chart ---
with tab3:
    st.markdown("### 🕸 Radar Chart – Athlete Profile Over Time")
    selected_athlete = st.selectbox("Athlete", athlete_list, key="radar_athlete")
    radar_df = df[df["Athlete"] == selected_athlete].copy().dropna(subset=list(metric_map.keys()), how="any")

    if radar_df.empty:
        st.warning("⚠️ No complete test sets available for this athlete.")
    else:
        fig = go.Figure()
        for _, row in radar_df.iterrows():
            values = row[list(metric_map.keys())]
            values.index = list(metric_map.values())
            fig.add_trace(go.Scatterpolar(
                r=values.values, theta=values.index, fill='toself',
                name=row["Testing Date"].strftime("%Y-%m-%d")
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# --- 🔁 Progress Delta ---
with tab4:
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

# --- 📉 Correlation Heatmap ---
with tab5:
    st.markdown("### 📉 Fitness Metric Correlations")
    corr = df[metric_cols].dropna().corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# --- ⚖️ Z-Score Tracker ---
with tab6:
    st.markdown("### ⚖️ Z-Score Normalization")
    z_metric = st.selectbox("Metric", metric_cols, key="zscore_metric")
    z_athletes = st.multiselect("Athletes", athlete_list, default=athlete_list[:3], key="zscore_athletes")

    z_df = df[df["Athlete"].isin(z_athletes)][["Athlete", "Testing Date", z_metric]].dropna()
    z_df["Z-Score"] = z_df.groupby("Testing Date")[z_metric].transform(lambda x: (x - x.mean()) / x.std(ddof=0))

    fig = px.line(z_df, x="Testing Date", y="Z-Score", color="Athlete", markers=True,
                  title=f"Z-Score Progress of {z_metric}")
    st.plotly_chart(fig, use_container_width=True)
