# -------------------------------
# Section 2: Overall Data
# -------------------------------
st.header("📊 Overall Data")

force_refresh_overall = st.session_state.get("reset_cache_overall", False)
with st.spinner("🔄 Loading Overall Data..."):
    overall_df = Overall_Data_Load.load_preprocessed_overall_data(force_rebuild=force_refresh_overall)

if overall_df.empty:
    st.warning("⚠️ No overall data found or processed.")
else:
    st.markdown("### 🔍 Debug Summary")
    st.write("Total records loaded:", overall_df.shape[0])
    st.write("Historical records:", (overall_df["source_file"] == "historical data").sum())
    st.write("Recent records:", overall_df[overall_df["source_file"] != "historical data"].shape[0])
    st.write("Unique seasons:", sorted(overall_df["Season"].dropna().unique()))

    with st.expander("🔎 Filter Overall Data"):
        col1, col2, col3, col4, col5 = st.columns(5)
        seasons = sorted(overall_df["Season"].dropna().unique())
        teams = sorted(overall_df["TEAM"].dropna().unique())
        homes = sorted(overall_df["Home"].dropna().unique())
        aways = sorted(overall_df["Away"].dropna().unique())
        teamnames = sorted(overall_df["Team"].dropna().unique()) if "Team" in overall_df.columns else []

        o_seasons = col1.multiselect("Season", options=seasons)
        o_teams = col2.multiselect("TEAM", options=teams)
        o_home = col3.multiselect("Home", options=homes)
        o_away = col4.multiselect("Away", options=aways)
        o_search = col5.text_input("Search Team Name")

    filtered_overall = overall_df.copy()
    if o_seasons:
        filtered_overall = filtered_overall[filtered_overall["Season"].isin(o_seasons)]
    if o_teams:
        filtered_overall = filtered_overall[filtered_overall["TEAM"].isin(o_teams)]
    if o_home:
        filtered_overall = filtered_overall[filtered_overall["Home"].isin(o_home)]
    if o_away:
        filtered_overall = filtered_overall[filtered_overall["Away"].isin(o_away)]
    if o_search and "Team" in filtered_overall.columns:
        filtered_overall = filtered_overall[filtered_overall["Team"].str.contains(o_search, case=False, na=False)]

    st.success(f"✅ {filtered_overall.shape[0]} overall records shown")
    latest_overall_date = pd.to_datetime(filtered_overall["Date"], errors="coerce").dropna().max()
    if pd.notnull(latest_overall_date):
        st.markdown(f"**🗓️ Overall data current as of:** {latest_overall_date.date()}")

    st.dataframe(filtered_overall)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.download_button("💾 Download Overall CSV", filtered_overall.to_csv(index=False).encode("utf-8"), "overall_data.csv", "text/csv")
    with c2:
        if st.button("🔁 Reset Overall Cache"):
            if os.path.exists(Overall_Data_Load.CACHE_FILE):
                os.remove(Overall_Data_Load.CACHE_FILE)
                st.session_state["reset_cache_overall"] = True
                st.rerun()
            else:
                st.info("ℹ️ No overall cache found.")
        st.caption("⚠️ Only use if source overall data changed.")

