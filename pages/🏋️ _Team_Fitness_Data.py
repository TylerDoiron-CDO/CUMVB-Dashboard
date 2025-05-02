
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

    # Inline filters with chart type toggle
    col1, col2, col3 = st.columns([3, 3, 2])
    selected_box_metric = col1.selectbox("Metric", tracked_metrics, key="box_metric")
    selected_box_positions = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="box_positions")
    chart_mode = col3.radio("Chart Type", ["Box", "Violin"], horizontal=True, key="box_violin_mode")

    # Apply filters
    filtered_box_df = df.copy()
    if selected_box_positions:
        filtered_box_df = filtered_box_df[filtered_box_df["Primary Position"].isin(selected_box_positions)]

    # Drop NA for metric
    raw_metric = inverse_map[selected_box_metric]
    filtered_box_df = filtered_box_df.dropna(subset=["Testing Date", raw_metric])
    filtered_box_df["Testing Date"] = pd.to_datetime(filtered_box_df["Testing Date"]).dt.strftime("%Y-%m-%d")

    # Plot
    if not filtered_box_df.empty:
        if chart_mode == "Box":
            fig = px.box(filtered_box_df, x="Testing Date", y=raw_metric, points="all", title=f"{selected_box_metric} Distribution")
        else:
            fig = px.violin(filtered_box_df, x="Testing Date", y=raw_metric, box=True, points="all", title=f"{selected_box_metric} Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Tab 3: Dual Radar Charts
with tabs[2]:
    st.markdown("### 🕸 Radar Charts – Touch vs. Performance Profiles")

    radar_athlete = st.selectbox("Select Athlete", athlete_list, key="dual_radar_athlete")
    radar_df = df[df["Athlete"] == radar_athlete].copy()
    radar_df["Testing Date"] = pd.to_datetime(radar_df["Testing Date"], errors="coerce")

    if radar_df.empty:
        st.warning("⚠️ No records available for this athlete.")
    else:
        # Group 1: Touches & Physical Attributes
        group1_keys = [
            "Height (in.)", "Weight (lbs)", "Block Touch (in.)",
            "Approach Touch (in.)", "Broad Jump (in.)"
        ]
        group1_labels = ["Height", "Weight", "Block Touch", "Approach Touch", "Broad Jump"]

        # Group 2: Performance & Capacity
        group2_keys = [
            "Block Vertical (in.)", "Approach Vertical (in.)", "Reps at E[X] Bench",
            "Agility Test (s)", "10 Down and Backs (s)", "Yo-Yo Cardio Test"
        ]
        group2_labels = [
            "Block Vertical", "Approach Vertical", "Reps at E[X] Bench",
            "Agility Test", "10 Down/Backs", "Yo-Yo Test"
        ]

        col1, col2 = st.columns(2)

        # --- Radar Chart 1 ---
        with col1:
            st.markdown("#### 📊 Touches & Physical Attributes")
            fig1 = go.Figure()

            for _, row in radar_df.iterrows():
                values = row[group1_keys]
                if values.isnull().all():
                    continue
                values.index = group1_labels
                plot_data = values.reindex(group1_labels)

                fig1.add_trace(go.Scatterpolar(
                    r=plot_data.values,
                    theta=plot_data.index,
                    fill='toself',
                    name=row["Testing Date"].strftime("%Y-%m-%d")
                ))

            if fig1.data:
                fig1.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    height=600
                )
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No data available for chart 1.")

        # --- Radar Chart 2 ---
        with col2:
            st.markdown("#### 🧪 Performance & Capacity Metrics")
            fig2 = go.Figure()

            for _, row in radar_df.iterrows():
                values = row[group2_keys]
                if values.isnull().all():
                    continue
                values.index = group2_labels
                plot_data = values.reindex(group2_labels)

                fig2.add_trace(go.Scatterpolar(
                    r=plot_data.values,
                    theta=plot_data.index,
                    fill='toself',
                    name=row["Testing Date"].strftime("%Y-%m-%d")
                ))

            if fig2.data:
                fig2.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    height=600
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No data available for chart 2.")

# Tab 4: Progress Delta
with tabs[3]:
    st.markdown("### 🔁 Change Over Time – Progress to Most Recent Test")

    # Use consistent tracked metrics
    delta_metric_clean = st.selectbox("Metric", tracked_metrics, key="delta_metric")
    delta_metric = inverse_map[delta_metric_clean]

    # Filter valid rows
    delta_df = df[["Athlete", "Testing Date", delta_metric]].dropna()
    delta_df["Testing Date"] = pd.to_datetime(delta_df["Testing Date"], errors="coerce")
    delta_df.sort_values(by=["Athlete", "Testing Date"], inplace=True)

    # Build athlete-specific progression tables
    results = []
    for athlete, group in delta_df.groupby("Athlete"):
        group_sorted = group.sort_values("Testing Date")
        if group_sorted.shape[0] >= 2:
            latest_val = pd.to_numeric(group_sorted.iloc[-1][delta_metric], errors="coerce")
            second_val = pd.to_numeric(group_sorted.iloc[-2][delta_metric], errors="coerce")
            first_val = pd.to_numeric(group_sorted.iloc[0][delta_metric], errors="coerce")
    
            if pd.notnull(latest_val) and latest_val != 0:
                from_first = 100 * (latest_val - first_val) / latest_val if pd.notnull(first_val) else None
                from_second = 100 * (latest_val - second_val) / latest_val if pd.notnull(second_val) else None
                results.append({
                    "Athlete": athlete,
                    "Change from First": from_first,
                    "Change from Second Last": from_second
                })
    

    # Create DataFrame
    delta_summary = pd.DataFrame(results).set_index("Athlete")

    if not delta_summary.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Progress from First Test")
            fig1 = px.bar(delta_summary, x=delta_summary.index, y="Change from First", color="Change from First",
                          title=f"Progress in {delta_metric_clean} (First ➜ Most Recent)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("#### 📈 Progress from Second Most Recent")
            fig2 = px.bar(delta_summary, x=delta_summary.index, y="Change from Second Last", color="Change from Second Last",
                          title=f"Progress in {delta_metric_clean} (2nd ➜ Most Recent)")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Not enough data to compute progression charts.")

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
