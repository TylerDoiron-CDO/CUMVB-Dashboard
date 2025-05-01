import streamlit as st
import pandas as pd
import os

# Constants
TESTING_DATA_PATH = "data/Testing Data.csv"

# Page setup
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")
st.title("💪 Team Fitness Data")
st.markdown("Explore raw fitness testing results for all athletes. Use the filters below to focus your view.")

# Load data
@st.cache_data
def load_testing_data():
    try:
        df = pd.read_csv(TESTING_DATA_PATH)
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"Failed to load Testing Data: {e}")
        return pd.DataFrame()

df = load_testing_data()

if not df.empty:
    # Filter values
    athlete_options = sorted(df["Athlete"].dropna().unique())
    position_options = sorted(df["Primary Position"].dropna().unique())
    date_options = sorted(df["Testing Date"].dropna().unique())

    # Filters (clean style)
    col1, col2, col3 = st.columns(3)
    f_athlete = col1.multiselect("Athlete", options=athlete_options)
    f_position = col2.multiselect("Position", options=position_options)
    f_date = col3.multiselect("Testing Date", options=date_options)

    # Apply filters
    filtered_df = df.copy()
    if f_athlete:
        filtered_df = filtered_df[filtered_df["Athlete"].isin(f_athlete)]
    if f_position:
        filtered_df = filtered_df[filtered_df["Primary Position"].isin(f_position)]
    if f_date:
        filtered_df = filtered_df[filtered_df["Testing Date"].isin(f_date)]

    # Show data
    st.success(f"✅ {filtered_df.shape[0]} testing records shown")
    st.subheader("📋 Raw Fitness Testing Data")
    st.dataframe(filtered_df, use_container_width=True)

    # Utility buttons
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "💾 Download Fitness CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "team_fitness_data.csv",
            "text/csv"
        )
    with col_d2:
        if st.button("🔁 Reset Fitness Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Reloading data...")
            st.rerun()

    st.caption("⚠️ Only use 'Reset Fitness Cache' if the source data file has changed.")
else:
    st.warning("No data available.")

import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Convert dates
df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")

# Filter for numeric columns
metric_cols = df.select_dtypes(include="number").columns.tolist()
athlete_list = sorted(df["Athlete"].dropna().unique())
dates = sorted(df["Testing Date"].dropna().unique())

# Section
st.markdown("## 📊 Athlete Testing Visualizations")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Line Plot", "📦 Box + Violin", "🕸 Radar Chart", 
    "🔁 Progress Delta", "📉 Correlation Heatmap", "⚖️ Z-Score Tracker"
])

# --- 📈 LINE PLOT ---
with tab1:
    col1, col2 = st.columns([3, 2])
    metric = col1.selectbox("Metric", metric_cols, key="line_metric")
    selected = col2.multiselect("Athletes", athlete_list, default=athlete_list[:3], key="line_ath")

    if selected:
        plot_df = df[df["Athlete"].isin(selected)].dropna(subset=["Testing Date", metric])
        fig = px.line(plot_df, x="Testing Date", y=metric, color="Athlete", markers=True,
                      title=f"{metric} Progress Over Time", line_shape="spline")
        st.plotly_chart(fig, use_container_width=True)

# --- 📦 BOXPLOT / VIOLIN ---
with tab2:
    col1, col2 = st.columns(2)
    metric = col1.selectbox("Metric", metric_cols, key="violin_metric")
    chart_type = col2.radio("Chart Type", ["Box Plot", "Violin Plot"], horizontal=True)

    plot_df = df.dropna(subset=["Testing Date", metric])
    plot_df["Testing Date"] = plot_df["Testing Date"].dt.strftime("%Y-%m-%d")

    if chart_type == "Box Plot":
        fig = px.box(plot_df, x="Testing Date", y=metric, points="all", title=f"{metric} Distribution")
    else:
        fig = px.violin(plot_df, x="Testing Date", y=metric, box=True, points="all", title=f"{metric} Distribution")
    st.plotly_chart(fig, use_container_width=True)

# --- 🕸 RADAR CHART ---
with tab3:
    selected_athlete = st.selectbox("Athlete", athlete_list, key="radar_ath")
    radar_date = st.selectbox("Testing Date", dates, key="radar_date")
    
    radar_df = df[(df["Athlete"] == selected_athlete) & (df["Testing Date"] == radar_date)].dropna()
    radar_metrics = radar_df[metric_cols].T
    radar_metrics.columns = ["Value"]
    radar_metrics = radar_metrics.reset_index().rename(columns={"index": "Metric"})

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_metrics["Value"],
        theta=radar_metrics["Metric"],
        fill='toself',
        name=f"{selected_athlete} on {radar_date.date()}"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# --- 🔁 PROGRESS DELTA ---
with tab4:
    delta_metric = st.selectbox("Metric", metric_cols, key="delta_metric")
    delta_df = df[["Athlete", "Testing Date", delta_metric]].dropna()
    delta_df.sort_values(by=["Athlete", "Testing Date"], inplace=True)

    delta_summary = (
        delta_df.groupby("Athlete")
        .agg(first=("Testing Date", "first"), last=("Testing Date", "last"))
        .join(delta_df.groupby("Athlete")[delta_metric].agg(first_val="first", last_val="last"))
    )
    delta_summary["% Change"] = 100 * (delta_summary["last_val"] - delta_summary["first_val"]) / delta_summary["first_val"]
    delta_summary = delta_summary.sort_values(by="% Change", ascending=False).dropna()

    fig = px.bar(delta_summary, x=delta_summary.index, y="% Change", color="% Change",
                 title=f"Improvement in {delta_metric} Over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- 📉 CORRELATION HEATMAP ---
with tab5:
    st.markdown("### Fitness Metric Correlations")
    corr_df = df[metric_cols].dropna().corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# --- ⚖️ Z-SCORE TRACKING ---
with tab6:
    z_metric = st.selectbox("Metric", metric_cols, key="zscore_metric")
    z_athletes = st.multiselect("Athletes", athlete_list, default=athlete_list[:3], key="zscore_ath")

    z_df = df[df["Athlete"].isin(z_athletes)][["Athlete", "Testing Date", z_metric]].dropna()
    z_df["Z-Score"] = z_df.groupby("Testing Date")[z_metric].transform(
        lambda x: (x - x.mean()) / x.std(ddof=0)
    )

    fig = px.line(z_df, x="Testing Date", y="Z-Score", color="Athlete", markers=True,
                  title=f"Z-Score Progress of {z_metric}")
    st.plotly_chart(fig, use_container_width=True)


