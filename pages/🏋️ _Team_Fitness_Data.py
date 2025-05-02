import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")

# Title and intro
st.title("💪 Team Fitness Data")
st.markdown("""
Explore physical performance metrics and longitudinal testing for all athletes.

Use the filters below to refine the dataset and navigate through interactive visualizations to monitor progress, spot trends, and evaluate individual and team-wide improvements.
""")

# Load data
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

# Main Filters
if not df.empty:
    st.markdown("### 🔍 Filter Options")
    col1, col2, col3 = st.columns(3)
    f_athlete = col1.multiselect("Athlete", sorted(df["Athlete"].dropna().unique()))
    f_position = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()))
    f_date = col3.multiselect("Testing Date", sorted(pd.to_datetime(df["Testing Date"].dropna()).dt.strftime("%Y-%m-%d")))

    filtered_df = df.copy()
    filtered_df["Testing Date"] = pd.to_datetime(filtered_df["Testing Date"])
    if f_athlete:
        filtered_df = filtered_df[filtered_df["Athlete"].isin(f_athlete)]
    if f_position:
        filtered_df = filtered_df[filtered_df["Primary Position"].isin(f_position)]
    if f_date:
        filtered_df = filtered_df[filtered_df["Testing Date"].dt.strftime("%Y-%m-%d").isin(f_date)]

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
    st.stop()

# Preprocess for visualizations
df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")
metric_cols = df.select_dtypes(include="number").columns.tolist()
athlete_list = sorted(df["Athlete"].dropna().unique())

# Metric mapping
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

# Tabs
tabs = st.tabs(["📈 Line Plot", "📦 Box/Violin", "🕸 Radar Chart", "🔁 Delta", "📉 Correlation", "⚖️ Z-Score"])

# Tab 1 - 📈 Line Plot
with tabs[0]:
    st.markdown("### 📈 Track Athlete Progress")
    col1, col2, col3 = st.columns(3)
    selected_metric = col1.selectbox("Metric", tracked_metrics, key="lineplot_metric")
    selected_athletes = col2.multiselect("Athletes", athlete_list, key="lineplot_athletes")
    selected_positions = col3.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="lineplot_positions")

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

# Tab 2 - 📦 Box/Violin Plot
with tabs[1]:
    st.markdown("### 📦 Distribution by Testing Date")
    col1, col2, col3 = st.columns([3, 3, 2])
    selected_box_metric = col1.selectbox("Metric", tracked_metrics, key="box_metric")
    selected_box_positions = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="box_positions")
    chart_mode = col3.radio("Chart Type", ["Box", "Violin"], horizontal=True, key="box_violin_mode")

    filtered_box_df = df.copy()
    if selected_box_positions:
        filtered_box_df = filtered_box_df[filtered_box_df["Primary Position"].isin(selected_box_positions)]

    raw_metric = inverse_map[selected_box_metric]
    filtered_box_df = filtered_box_df.dropna(subset=["Testing Date", raw_metric])
    filtered_box_df["Testing Date"] = filtered_box_df["Testing Date"].dt.strftime("%Y-%m-%d")

    if not filtered_box_df.empty:
        if chart_mode == "Box":
            fig = px.box(filtered_box_df, x="Testing Date", y=raw_metric, points="all")
        else:
            fig = px.violin(filtered_box_df, x="Testing Date", y=raw_metric, box=True, points="all")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Tab 3 - 🕸 Radar Chart
with tabs[2]:
    st.markdown("### 🕸 Radar Charts – Touch vs. Performance Profiles")
    radar_athlete = st.selectbox("Select Athlete", athlete_list, key="dual_radar_athlete")
    radar_df = df[df["Athlete"] == radar_athlete].copy()
    radar_df["Testing Date"] = pd.to_datetime(radar_df["Testing Date"], errors="coerce")

    group1_keys = ["Height (in.)", "Weight (lbs)", "Block Touch (in.)", "Approach Touch (in.)", "Broad Jump (in.)"]
    group1_labels = ["Height", "Weight", "Block Touch", "Approach Touch", "Broad Jump"]
    group2_keys = ["Block Vertical (in.)", "Approach Vertical (in.)", "Reps at E[X] Bench", "Agility Test (s)", "10 Down and Backs (s)", "Yo-Yo Cardio Test"]
    group2_labels = ["Block Vertical", "Approach Vertical", "Reps @ E[X] Bench", "Agility Test", "10 Down/Backs", "Yo-Yo Test"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 Touches & Physical Attributes")
        fig1 = go.Figure()
        for _, row in radar_df.iterrows():
            values = row[group1_keys]
            if values.isnull().all():
                continue
            values.index = group1_labels
            fig1.add_trace(go.Scatterpolar(r=values.values, theta=values.index, fill='toself', name=row["Testing Date"].strftime("%Y-%m-%d")))
        fig1.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=600)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### 🧪 Performance & Capacity Metrics")
        fig2 = go.Figure()
        for _, row in radar_df.iterrows():
            values = row[group2_keys]
            if values.isnull().all():
                continue
            values.index = group2_labels
            fig2.add_trace(go.Scatterpolar(r=values.values, theta=values.index, fill='toself', name=row["Testing Date"].strftime("%Y-%m-%d")))
        fig2.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=600)
        st.plotly_chart(fig2, use_container_width=True)

# 🔁 Tab 4: Progress Delta
with tabs[3]:
    st.markdown("### 🔁 Athlete-Specific Change Over Time")

    # Inline filters
    col1, col2, col3 = st.columns([4, 3, 3])
    delta_metric_clean = col1.selectbox("Metric", tracked_metrics, key="delta_metric")
    delta_position_filter = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="delta_positions")
    display_mode = col3.radio("Display As", ["% Change", "Raw Change"], horizontal=True)

    delta_metric = inverse_map[delta_metric_clean]

    delta_df = df[["Athlete", "Primary Position", "Testing Date", delta_metric]].dropna()
    delta_df["Testing Date"] = pd.to_datetime(delta_df["Testing Date"], errors="coerce")

    if delta_position_filter:
        delta_df = delta_df[delta_df["Primary Position"].isin(delta_position_filter)]

    delta_df.sort_values(by=["Athlete", "Testing Date"], inplace=True)

    results = []
    for athlete, group in delta_df.groupby("Athlete"):
        if group.shape[0] >= 2:
            group_sorted = group.sort_values("Testing Date")

            first_val = group_sorted.iloc[0][delta_metric]
            first_date = group_sorted.iloc[0]["Testing Date"]
            last_val = group_sorted.iloc[-1][delta_metric]
            last_date = group_sorted.iloc[-1]["Testing Date"]

            if group.shape[0] >= 3:
                second_last_val = group_sorted.iloc[-2][delta_metric]
                second_last_date = group_sorted.iloc[-2]["Testing Date"]
            else:
                second_last_val, second_last_date = None, None

            try:
                first_val = float(first_val)
                last_val = float(last_val)
                second_last_val = float(second_last_val) if second_last_val is not None else None

                diff_first = last_val - first_val
                diff_second = last_val - second_last_val if second_last_val is not None else None

                pct_first = 100 * diff_first / last_val if last_val != 0 else None
                pct_second = 100 * diff_second / last_val if last_val != 0 and diff_second is not None else None

                results.append({
                    "Athlete": athlete,
                    "Δ_val_1st": round(diff_first, 2),
                    "Δ_pct_1st": round(pct_first, 2) if pct_first is not None else None,
                    "Δ_val_2nd": round(diff_second, 2) if diff_second is not None else None,
                    "Δ_pct_2nd": round(pct_second, 2) if pct_second is not None else None,
                    "First Test Date": first_date.strftime("%Y-%m-%d"),
                    "Second Last Test Date": second_last_date.strftime("%Y-%m-%d") if second_last_date else None,
                    "Most Recent Test Date": last_date.strftime("%Y-%m-%d")
                })
            except Exception:
                continue

    delta_summary = pd.DataFrame(results)

    if not delta_summary.empty:
        # Select y-axis fields
        y1_col = "Δ_pct_1st" if display_mode == "% Change" else "Δ_val_1st"
        y2_col = "Δ_pct_2nd" if display_mode == "% Change" else "Δ_val_2nd"
        y_axis_title = "Δ (%)" if display_mode == "% Change" else "Δ (Raw Value)"

        delta_summary_sorted1 = delta_summary.sort_values(by=y1_col, ascending=False)
        delta_summary_sorted2 = delta_summary.sort_values(by=y2_col, ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Change Since 1st Testing Date")
            fig1 = px.bar(
                delta_summary_sorted1,
                x="Athlete", y=y1_col, color=y1_col,
                text=y1_col,
                hover_data=["First Test Date", "Most Recent Test Date"]
            )
            fig1.update_layout(
                title="Change Since 1st Testing Date",
                yaxis_title=y_axis_title,
                xaxis_title="Athlete"
            )
            fig1.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("#### 📈 Change Since Most Recent Testing Date")
            filtered = delta_summary_sorted2.dropna(subset=[y2_col])
            if not filtered.empty:
                fig2 = px.bar(
                    filtered,
                    x="Athlete", y=y2_col, color=y2_col,
                    text=y2_col,
                    hover_data=["Second Last Test Date", "Most Recent Test Date"]
                )
                fig2.update_layout(
                    title="Change Since Most Recent Testing Date",
                    yaxis_title=y_axis_title,
                    xaxis_title="Athlete"
                )
                fig2.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Not enough data for second-most-recent comparison.")
    else:
        st.info("Not enough valid data to generate progression charts.")

# Tab 5 - 📉 Correlation Heatmap
with tabs[4]:
    st.markdown("### 📉 Fitness Metric Correlations")
    corr = df[metric_cols].dropna().corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# Tab 6 -⚖️ Z-Score Tracker
with tabs[5]:
    st.markdown("### ⚖️ Z-Score Normalization")
    z_metric = st.selectbox("Metric", sorted(metric_cols), key="zscore_metric")
    z_athletes = st.multiselect("Athletes", sorted(athlete_list), default=sorted(athlete_list)[:3], key="zscore_ath")

    z_df = df[df["Athlete"].isin(z_athletes)][["Athlete", "Testing Date", z_metric]].dropna()
    z_df["Z-Score"] = z_df.groupby("Testing Date")[z_metric].transform(lambda x: (x - x.mean()) / x.std(ddof=0))

    fig = px.line(z_df, x="Testing Date", y="Z-Score", color="Athlete", markers=True,
                  title=f"Z-Score Progress of {z_metric}")
    st.plotly_chart(fig, use_container_width=True)
