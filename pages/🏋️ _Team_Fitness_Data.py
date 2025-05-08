# 💪 Team Fitness Data – Full Streamlit App with Utility Buttons

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import base64
import os
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.table import Table
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from io import BytesIO

# ✅ Must be first
st.set_page_config(page_title="💪 Team Fitness Data", layout="wide")

# --- Utility Function: Chart + CSV + Cache ---
def render_utilities(df, fig=None, filename="export", include_csv=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    if include_csv:
        with col1:
            st.download_button(
                "📂 Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name=f"{filename}.csv",
                mime="text/csv"
            )
    if fig is not None:
        with col2:
            try:
                png_bytes = fig.to_image(format="png", scale=3)
                st.download_button(
                    label="🖼️ Download Chart (PNG – Full Color)",
                    data=png_bytes,
                    file_name=f"{filename}.png",
                    mime="image/png"
                )
            except Exception as e:
                st.warning(f"⚠️ Chart PNG export failed. Ensure Kaleido is installed. ({e})")
    with col3:
        if st.button(f"🔁 Clear Cache for {filename}"):
            st.cache_data.clear()
            st.experimental_rerun()

# --- Get Most Recent Roster (Active Athletes) ---
def get_active_athletes(roster_base_dir="rosters", csv_name="team_info.csv"):
    if not os.path.exists(roster_base_dir):
        return set(), None
    seasons = sorted(
        [d for d in os.listdir(roster_base_dir) if os.path.isdir(os.path.join(roster_base_dir, d))],
        reverse=True
    )
    if not seasons:
        return set(), None
    latest_season = seasons[0]
    roster_path = os.path.join(roster_base_dir, latest_season, csv_name)
    if not os.path.exists(roster_path):
        return set(), latest_season
    try:
        roster_df = pd.read_csv(roster_path)
        roster_df.columns = roster_df.columns.str.strip().str.lower()
        if "name" in roster_df.columns:
            active_names = set(roster_df["name"].dropna().str.strip())
            return active_names, latest_season
    except Exception:
        pass
    return set(), latest_season

# Load active athlete list
active_athlete_names, latest_loaded_season = get_active_athletes()

# --- Header and Filter UI ---
col1, col2 = st.columns([6, 2])
with col1:
    st.title("💪 Team Fitness Data")
    st.markdown("""
    Explore physical performance metrics and longitudinal testing for all athletes.

    Navigate through interactive visualizations to monitor progress, spot trends, and evaluate individual and team-wide improvements.
    """)
with col2:
    athlete_filter_mode = st.radio("Includes:", ["Active Athletes Only", "All Athletes"], horizontal=True)

# --- Load & Filter Data ---
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

df["Testing Date"] = pd.to_datetime(df["Testing Date"], errors="coerce")
df["Athlete"] = df["Athlete"].astype(str).str.strip()

# Apply filter
if athlete_filter_mode == "Active Athletes Only":
    df = df[df["Athlete"].isin(active_athlete_names)]

# --- Preprocessing Metadata ---
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

# --- Tabs ---
st.markdown("---")
tabs = st.tabs([
    "📈 Line Plot",
    "📦 Box/Violin",
    "🕸 Radar Chart",
    "🔁 Delta",
    "📉 Correlation",
    "⚖️ Z-Score",
    "📊 Team vs. VBC Normative",
    "🎯 Target Analysis"
])

# Tab 1 - 📈 Line Plot
with tabs[0]:
    st.markdown("### 📈 Line Plot – Track Athlete Progress")

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 📏 What Is This Graph Showing?")
        st.code(
            "This line plot tracks the absolute (raw) scores for a chosen metric across testing dates."
        )
    
        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Understand trends in an athlete’s performance over time\n"
            "• Compare improvements or regressions across testing sessions\n"
            "• Spot consistency or volatility in results"
        )
    
        st.markdown("#### 🎯 What to Select")
        st.code(
            "• Choose a metric like 'Yo-Yo Test' or 'Block Vertical'\n"
            "• Filter by athlete or position to narrow your focus\n"
            "• Data table will show score changes across test dates with automatic deltas"
        )
    
        st.markdown("#### 📊 How to Interpret the Graph")
        st.code(
            "• Each line represents one athlete’s performance trend\n"
            "• Δ Last: change between most recent 2 tests\n"
            "• Δ Net: overall improvement from first to last test\n"
            "• Missing points may mean no test data for that athlete on that date"
        )

    st.info("ℹ️ Use this plot for visualizing raw performance growth over time.\nZ-Score standardization is available on the '⚖️ Z-Score' tab.")

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
    chart_df["Testing Date"] = pd.to_datetime(chart_df["Testing Date"], errors="coerce")
    chart_df[raw_metric] = pd.to_numeric(chart_df[raw_metric], errors="coerce")
    chart_df = chart_df.dropna(subset=["Testing Date", raw_metric])

    if not chart_df.empty:
        # --- Line Chart ---
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

        # --- Pivot Table ---
        pivot_ready = chart_df.dropna(subset=[raw_metric, "Testing Date"])
        pivot = pivot_ready.pivot_table(
            index=["Athlete", "Primary Position"],
            columns="Testing Date",
            values=raw_metric,
            aggfunc="mean"
        ).reset_index()

        # Format and sort date columns
        date_map = {col: col.strftime("%B %Y") for col in pivot.columns if isinstance(col, pd.Timestamp)}
        pivot.rename(columns=date_map, inplace=True)
        date_cols = sorted(date_map.values(), key=lambda d: pd.to_datetime(d))
        pivot = pivot.rename(columns={"Athlete": "Name", "Primary Position": "Position"})

        # Convert and calculate deltas
        pivot[date_cols] = pivot[date_cols].apply(pd.to_numeric, errors='coerce')
        if len(date_cols) >= 2:
            pivot["Δ Last"] = pivot[date_cols[-1]] - pivot[date_cols[-2]]
            pivot["Δ Net"] = pivot[date_cols[-1]] - pivot[date_cols[0]]
        else:
            pivot["Δ Last"] = np.nan
            pivot["Δ Net"] = np.nan

        pivot["Δ Last"] = pivot["Δ Last"].round(2)
        pivot["Δ Net"] = pivot["Δ Net"].round(2)

        final_cols = ["Name", "Position"] + date_cols + ["Δ Last", "Δ Net"]
        display_table = pivot[final_cols]

        st.dataframe(display_table, use_container_width=True, hide_index=True)
        render_utilities(display_table, fig, filename="line_plot")
    else:
        st.info("No data available for the selected filters.")

# Tab 2 - 📦 Box/Violin Plot
with tabs[1]:
    st.markdown("### 📦 Box/Violin Plot - Distribution of Perfomance")

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 📦 What Are Box & Violin Plots?")
        st.code(
            "These visualizations show the distribution of test scores for each date.\n"
            "Box plots highlight medians, quartiles, and outliers.\n"
            "Violin plots add density curves to show where values are concentrated."
        )
    
        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Understand variability within a testing session\n"
            "• Spot outliers or inconsistent results\n"
            "• Compare how tight or spread out athlete results are"
        )
    
        st.markdown("#### 🎯 What to Select")
        st.code(
            "• Choose a metric to analyze (e.g. 'Agility Test')\n"
            "• Filter by positions (optional)\n"
            "• Switch between Box or Violin views using the toggle"
        )
    
        st.markdown("#### 📊 How to Interpret the Graph")
        st.code(
            "• Each column = 1 test date\n"
            "• Taller = more variability in scores\n"
            "• Dots = individual athlete results\n"
            "• Narrow violin sections = few scores in that range"
        )
    
        st.warning("⚠️ If no data appears, check that selected metric and position group have values for that test date.")

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

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 🕸 What is a Radar Chart?")
        st.code(
            "Radar charts show how an athlete scores across multiple test dimensions at once.\n"
            "Each axis represents a different physical or performance attribute."
        )

        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Compare testing sessions over time\n"
            "• Quickly visualize strengths and weaknesses\n"
            "• Analyze balance across performance areas"
        )

        st.markdown("#### 🎯 What to Select")
        st.code(
            "• Choose an athlete from the dropdown\n"
            "• Two radar plots will be generated:\n"
            "   - Physical Attributes (height, jump, etc.)\n"
            "   - Performance & Capacity (agility, endurance, etc.)"
        )

        st.markdown("#### 📊 How to Interpret the Graph")
        st.code(
            "• Larger surface area = stronger performance\n"
            "• Each shape = 1 testing date (e.g. 'September 2024')\n"
            "• Smaller segments indicate weaker metrics on that date"
        )

        st.warning("⚠️ If nothing shows up, the athlete may have missing data for the selected tests.")

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
            formatted_date = row["Testing Date"].strftime("%B %Y")
            fig1.add_trace(go.Scatterpolar(r=values.values, theta=values.index, fill='toself', name=formatted_date))
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
            formatted_date = row["Testing Date"].strftime("%B %Y")
            fig2.add_trace(go.Scatterpolar(r=values.values, theta=values.index, fill='toself', name=formatted_date))
        fig2.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=600)
        st.plotly_chart(fig2, use_container_width=True)

# 🔁 Tab 4: Progress Delta
# 🔁 Tab 4: Progress Delta
with tabs[3]:
    st.markdown("### 🔁 Athlete-Specific Change Over Time")

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 📉 What is Delta Analysis?")
        st.code(
            "Delta (Δ) tracks how much an athlete has changed since:\n"
            "• Their first recorded test\n"
            "• Their most recent previous test"
        )

        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Easily monitor trends over time\n"
            "• Identify improvement or regression\n"
            "• Useful for progress tracking and goal evaluation"
        )

        st.markdown("#### 🎯 What to Select")
        st.code(
            "• Choose a performance metric\n"
            "• Filter by position if desired\n"
            "• Choose to display raw value change or percent change"
        )

        st.markdown("#### 📊 How to Interpret the Graphs")
        st.code(
            "Left Chart ➜ Change from first to most recent test\n"
            "Right Chart ➜ Change from second-last to most recent\n"
            "Positive = Improvement | Negative = Regression"
        )

        st.warning("⚠️ Athletes need at least two test results to be included. No chart = not enough data.")

    # Inline filters
    col1, col2, col3 = st.columns([4, 3, 3])
    delta_metric_clean = col1.selectbox("Metric", tracked_metrics, key="delta_metric")
    delta_position_filter = col2.multiselect("Position", sorted(df["Primary Position"].dropna().unique()), key="delta_positions")
    display_mode = col3.radio("Display As", ["Δ in value", "Δ (%)"], horizontal=True)

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
                    "First Test Date": first_date.strftime("%B %Y"),
                    "Second Last Test Date": second_last_date.strftime("%B %Y") if second_last_date else None,
                    "Most Recent Test Date": last_date.strftime("%B %Y")
                })
            except Exception:
                continue

    delta_summary = pd.DataFrame(results)

    if not delta_summary.empty:
        # Display mode mapping
        y1_col = "Δ_val_1st" if display_mode == "Δ in value" else "Δ_pct_1st"
        y2_col = "Δ_val_2nd" if display_mode == "Δ in value" else "Δ_pct_2nd"
        y_axis_title = display_mode

        delta_summary_sorted1 = delta_summary.sort_values(by=y1_col, ascending=False)
        delta_summary_sorted2 = delta_summary.sort_values(by=y2_col, ascending=False)

        col1, col2 = st.columns(2)

        # --- Chart 1: Change from First Test ---
        with col1:
            st.markdown("#### 📈 Change Since 1st Testing Date")
            fig1 = px.bar(
                delta_summary_sorted1,
                x="Athlete", y=y1_col, color=y1_col,
                text=y1_col,
                hover_data=["First Test Date", "Most Recent Test Date"],
                labels={y1_col: y_axis_title}
            )
            fig1.update_layout(
                title="Change Since 1st Testing Date",
                yaxis_title=y_axis_title,
                xaxis_title="Athlete",
                legend_title_text=y_axis_title
            )
            fig1.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        # --- Chart 2: Change from 2nd Most Recent Test ---
        with col2:
            st.markdown("#### 📈 Change Since Most Recent Testing Date")
            filtered = delta_summary_sorted2.dropna(subset=[y2_col])
            if not filtered.empty:
                fig2 = px.bar(
                    filtered,
                    x="Athlete", y=y2_col, color=y2_col,
                    text=y2_col,
                    hover_data=["Second Last Test Date", "Most Recent Test Date"],
                    labels={y2_col: y_axis_title}
                )
                fig2.update_layout(
                    title="Change Since Most Recent Testing Date",
                    yaxis_title=y_axis_title,
                    xaxis_title="Athlete",
                    legend_title_text=y_axis_title
                )
                fig2.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Not enough data for second-most-recent comparison.")
    else:
        st.info("Not enough valid data to generate progression charts.")

# 📉 Tab 5 – Correlation Heatmap by Position Group (based on most recent test date)
with tabs[4]:
    st.markdown("### 📉 Position-Specific Fitness Metric Correlations")

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 🔗 What is a Correlation Heatmap?")
        st.code(
            "A heatmap shows how strongly different physical tests are related to each other.\n"
            "Values range from -1 (strong inverse) to +1 (strong positive).\n"
            "Only data from the most recent testing date is used."
        )

        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Identify which tests move together (e.g. vertical + touch height)\n"
            "• Spot redundant or overlapping metrics\n"
            "• Tailor training emphasis for each position group"
        )

        st.markdown("#### 📊 What Does Correlation Actually Mean?")
        st.code(
            "• +1.00 ➜ Perfect positive relationship (metrics rise/fall together)\n"
            "•  0.00 ➜ No relationship\n"
            "• –1.00 ➜ Perfect negative relationship (one rises while the other falls)\n\n"
            "For example:\n"
            "   - A 0.85 correlation between Approach Touch & Block Touch = Strong positive\n"
            "   - A –0.6 correlation between Yo-Yo Test & Agility Time = Strong inverse"
        )

        st.markdown("#### 📈 Reading the Heatmaps")
        st.code(
            "• Each heatmap is specific to a positional group\n"
            "• Only metrics with ≥75% valid data on the most recent test date are shown\n"
            "• Dark red = strong positive correlation\n"
            "• Dark blue = strong negative correlation"
        )

        st.warning("⚠️ If a heatmap is missing, it means there isn't enough valid data for that group.")

    # Define position groupings
    position_groups = {
        "Outside Hitters": ["LS", "RS"],
        "Middle Hitters": ["MB", "M", "MH"],
        "Setters & Liberos": ["S", "LIB"]
    }

    selected_cols = list(metric_map.keys())
    most_recent_date = df["Testing Date"].dropna().max()
    recent_df = df[df["Testing Date"] == most_recent_date]
    recent_total = len(recent_df)

    eligible_cols = [
        col for col in selected_cols
        if recent_df[col].notna().sum() / recent_total >= 0.75
    ]

    if len(eligible_cols) < 2:
        st.warning("⚠️ Not enough metrics meet the 75% completeness threshold on the most recent test date.")
    else:
        st.caption(f"✅ Using data from {most_recent_date.strftime('%B %d, %Y')} — metrics with ≥75% completeness included.")

        fig, axes = plt.subplots(1, 3, figsize=(24, 8), constrained_layout=True)
        plotted = False

        for idx, (label, roles) in enumerate(position_groups.items()):
            group_df = df[df["Primary Position"].isin(roles)]
            group_df = group_df[group_df["Testing Date"] == most_recent_date]
            group_df = group_df[eligible_cols].replace(0, np.nan).dropna()

            if group_df.shape[0] < 2:
                axes[idx].axis("off")
                axes[idx].set_title(f"{label}\n(Not enough valid data)")
                continue

            corr = group_df.corr()

            sns.heatmap(
                corr,
                annot=True,
                fmt=".2f",
                cmap="coolwarm",
                ax=axes[idx],
                cbar=(idx == 2),
                xticklabels=[metric_map.get(c, c) for c in corr.columns],
                yticklabels=[metric_map.get(c, c) for c in corr.index] if idx == 0 else False
            )
            axes[idx].set_title(label)
            plotted = True

        if plotted:
            st.pyplot(fig)
        else:
            st.warning("⚠️ No valid data to generate grouped correlation matrices.")

# ⚖️ Tab 6 – Z-Score Tracker with Athlete 1–3 Filters
with tabs[5]:
    st.markdown("### ⚖️ Z-Score Normalization")

    with st.expander("ℹ️ How This Works & How to Use It", expanded=False):
        st.markdown("#### 📏 What is a Z-Score?")
        st.code(
            "A Z-score represents how far an athlete's score for a given test is from the group average "
            "on that specific testing date — in units of standard deviation."
        )

        st.markdown("#### 🧠 Why Use It?")
        st.code(
            "• Standardizes all metrics regardless of unit (e.g. inches, kg, seconds)\n"
            "• Makes performance comparison fair across different testing dates or groups\n"
            "• Helps identify standout or underperforming test scores"
        )

        st.markdown("#### 🎯 What to Select")
        st.code(
            "• Choose a metric (e.g. 'Block Touch')\n"
            "• Select 2–3 athletes to compare\n"
            "• Graph will only include testing dates where at least 2 valid athlete scores exist"
        )

        st.markdown("#### 📊 How to Interpret the Graph")
        st.code(
            "Z =  0     ➜ Exactly average that day\n"
            "Z >  0     ➜ Above average (e.g., +2 is top performer)\n"
            "Z <  0     ➜ Below average\n"
            "Dotted line marks Z = 0 as the team average baseline"
        )

        st.warning("⚠️ If no line appears, it likely means:\n- Too few athletes tested on the same date\n- Or selected metric has no variation (e.g. all values are the same)")

    # Metric selection
    z_metric = st.selectbox("Select Metric", sorted([metric_map.get(col, col) for col in metric_map.values()]), key="zscore_metric")
    z_metric_raw = inverse_map[z_metric]

    # 3-athlete comparison
    col1, col2, col3 = st.columns(3)
    athlete_1 = col1.selectbox("Athlete 1", sorted(athlete_list), key="zscore_a1")
    athlete_2 = col2.selectbox("Athlete 2", sorted(athlete_list), key="zscore_a2")
    athlete_3 = col3.selectbox("Athlete 3", sorted(athlete_list), key="zscore_a3")

    # Remove empty or duplicate selections
    selected_athletes = list({a for a in [athlete_1, athlete_2, athlete_3] if a})

    # Filter dataset
    z_df = df[df["Athlete"].isin(selected_athletes)][["Athlete", "Testing Date", z_metric_raw]].dropna()
    z_df["Testing Date"] = pd.to_datetime(z_df["Testing Date"], errors="coerce")
    z_df[z_metric_raw] = pd.to_numeric(z_df[z_metric_raw], errors="coerce")

    # Only allow testing dates with ≥2 athletes
    valid_dates = z_df.groupby("Testing Date")[z_metric_raw].count()
    valid_dates = valid_dates[valid_dates >= 2].index
    z_df = z_df[z_df["Testing Date"].isin(valid_dates)]

    if len(selected_athletes) < 2:
        st.warning("⚠️ Please select at least two different athletes.")
    elif z_df.empty:
        st.warning("⚠️ No valid testing dates found with enough scores to calculate Z-scores.")
    else:
        # Compute Z-scores per testing date
        z_df["Z-Score"] = z_df.groupby("Testing Date")[z_metric_raw].transform(
            lambda x: (x - x.mean()) / x.std(ddof=0)
        )

        # Plot Z-score trend
        fig = px.line(
            z_df,
            x="Testing Date",
            y="Z-Score",
            color="Athlete",
            markers=True,
            title=f"Z-Score Trend – {z_metric}",
            labels={"Z-Score": "Standard Score", "Testing Date": "Date"}
        )
        fig.update_layout(
            yaxis_title="Z-Score (standardized)",
            xaxis_title="Testing Date",
            shapes=[
                dict(type="line", xref="paper", x0=0, x1=1, y0=0, y1=0,
                     line=dict(color="gray", dash="dash"))
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 7 - 📊 Team vs. VBC Benchmark (All Ratings)
with tabs[6]:
    st.markdown("### 📊 Athlete Performance vs VBC Norms (Best, Average, Minimum)")
    st.info("Each athlete is grouped on the X-axis. Bars represent test dates. Horizontal lines represent VBC benchmarks for Excellent, Average, and Poor.")

    @st.cache_data
    def load_team_data():
        df = pd.read_csv("data/Testing Data.csv")
        df.columns = df.columns.str.strip()
        return df

    @st.cache_data
    def load_vbc_data():
        df = pd.read_csv("data/Volleyball Canada Normative.csv")
        df.columns = df.columns.str.strip()
        return df

    # Load data
    team_df = load_team_data()
    vbc_df = load_vbc_data()

    # Mappings
    metric_mapping = {
        "Approach Touch (in.)": "Spike Touch (in)",
        "Block Touch (in.)": "Block Touch (in)",
        "Attack Velocity (km/h)": "Attack Velocity (kmph)",
        "Serve Velocity (km/h)": "Spin Velocity (kmph)"
    }

    position_map = {
        "S": "Setter",
        "LS": "Left Side",
        "RS": "Opposite",
        "M": "Middle",
        "LIB": "Libero"
    }

    # --- Filters
    col1, col2, col3 = st.columns(3)
    selected_metric = col1.selectbox("📏 Metric", list(metric_mapping.keys()), key="vbc_full_metric")
    selected_position_team = col2.selectbox("🧍 Position", list(position_map.keys()), key="vbc_full_pos")
    age_groups = sorted(vbc_df["Age-Group"].dropna().unique())
    selected_age_group = col3.selectbox("📅 Age Group", age_groups, key="vbc_full_age")

    selected_metric_vbc = metric_mapping[selected_metric]
    selected_position_vbc = position_map[selected_position_team]

    # --- Filter and clean team data
    team_filtered = team_df[team_df["Primary Position"] == selected_position_team].copy()
    team_filtered["Testing Date"] = pd.to_datetime(team_filtered["Testing Date"], errors="coerce")
    team_filtered = team_filtered.dropna(subset=["Testing Date", selected_metric, "Athlete"])
    team_filtered["Date Label"] = team_filtered["Testing Date"].dt.strftime("%b %Y")

    if team_filtered.empty:
        st.warning("⚠️ No athlete data available for this metric/position.")
        st.stop()

    # --- Filter VBC data
    vbc_debug = vbc_df[
        (vbc_df["Position"] == selected_position_vbc) &
        (vbc_df["Age-Group"] == selected_age_group) &
        (vbc_df[selected_metric_vbc].notna())
    ]
    available_ratings = sorted(vbc_debug["Rating"].dropna().unique())
    st.caption(f"✅ Available VBC ratings for {selected_position_vbc} @ {selected_age_group}: {available_ratings}")

    # --- Extract Benchmark Lines
    rating_map = {
        "Minimum": ("Poor", "red"),
        "Average": ("Average", "yellow"),
        "Best": ("Excellent", "green")
    }

    benchmark_lines = {}
    for label, (rating_name, color) in rating_map.items():
        val = vbc_debug[vbc_debug["Rating"].str.lower() == rating_name.lower()][selected_metric_vbc].mean()
        if not pd.isna(val):
            benchmark_lines[label] = (val, color)
        else:
            st.warning(f"⚠️ Missing benchmark for: {label} (Rating='{rating_name}')")

    if not benchmark_lines:
        st.error("❌ No usable VBC benchmark values found.")
        st.stop()

    # --- Plotting
    fig = px.bar(
        team_filtered,
        x="Athlete",
        y=selected_metric,
        color="Date Label",
        barmode="group",
        title=f"{selected_metric} – {selected_position_vbc} – Age Group: {selected_age_group}",
        labels={"Date Label": "Testing Date", selected_metric: selected_metric},
        height=600
    )

    for label, (y_val, color) in benchmark_lines.items():
        fig.add_hline(
            y=y_val,
            line=dict(color=color, width=3),
            annotation_text=f"{label}: {y_val:.1f}",
            annotation_position="top left"
        )

    fig.update_layout(
        xaxis_title="Athlete",
        yaxis_title=selected_metric,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

# Tab 8 - 🎯 Target Analysis
with tabs[7]:
    st.markdown("### 🎯 Target Flow & Allocation Analysis")
    st.info("This dashboard will visualize fund flow or allocation targets based on ideal profiles, using a Sankey-style layout.")
    st.markdown("📌 *Placeholder content: Example target chart like company fund flow will be implemented here.*")
    st.image("data/5993889d-b26f-4737-970e-01cd2a69a3d5.png", caption="Example: Company Funds Flow Analysis")
