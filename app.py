"""Streamlit Dashboard for Philippine HEI Research Productivity Analysis.

Provides interactive visualization of historical and forecasted research metrics.
Period-based analysis: Pre-pandemic (2015-2019), During (2020-2022), 
Post-pandemic (2023-2025), Forecast (2026-2030, 2031-2035).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO

from src.viz_utils import plot_philippine_map, plot_period_geospatial_comparison


# === Constants ===
FORECAST_DATA_PATH = Path("data/processed/forecasts.parquet")
EXCEL_OUTPUT_PATH = Path("data/processed/hei_research_data_complete.xlsx")

# Period definitions per client requirements
PERIODS = {
    "Pre-Pandemic (2015-2019)": (2015, 2019),
    "During Pandemic (2020-2022)": (2020, 2022),
    "Post-Pandemic (2023-2025)": (2023, 2025),
    "Forecast Phase 1 (2026-2030)": (2026, 2030),
    "Forecast Phase 2 (2031-2035)": (2031, 2035),
}

# Color scheme for premium aesthetics
COLORS = {
    "history": "#3366CC",
    "forecast": "#FF6B6B",
    "background": "#0E1117",
    "accent": "#4ECDC4"
}


@st.cache_data
def load_forecasts(path: Path = FORECAST_DATA_PATH) -> pd.DataFrame:
    """Load and cache forecasted data.
    
    Args:
        path: Path to forecasts.parquet
        
    Returns:
        DataFrame with historical and forecasted data
    """
    return pd.read_parquet(path)


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel with separate sheets for periods.
    
    Args:
        df: Complete DataFrame with historical and forecast data
        
    Returns:
        Excel file as bytes for download
    """
    output = BytesIO()
    
    def create_wide_format(data: pd.DataFrame) -> pd.DataFrame:
        """Convert long format to wide: Metric Year columns."""
        wide = data.pivot_table(
            index=['Region Code', 'Region', 'School'],
            columns=['Year', 'Metric'],
            values='Value',
            aggfunc='first'
        )
        
        # Flatten MultiIndex columns: "Publication 2015", "CIT 2015", "FWCI 2015"
        def abbrev_metric(m):
            if 'Publication' in m: return 'Publication'
            elif 'Citation' in m: return 'CIT'
            else: return 'FWCI'
        
        wide.columns = [f"{abbrev_metric(metric)} {year}" for year, metric in wide.columns]
        
        # Order columns by year then Publication/CIT/FWCI
        years = sorted(set(int(c.split()[-1]) for c in wide.columns))
        ordered_cols = []
        for year in years:
            for prefix in ['Publication', 'CIT', 'FWCI']:
                col = f"{prefix} {year}"
                if col in wide.columns:
                    ordered_cols.append(col)
        
        return wide[ordered_cols].reset_index().sort_values(['Region Code', 'School'])
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Full dataset
        df.to_excel(writer, sheet_name='Complete Data', index=False)
        
        # Historical only (long format)
        historical = df[df["Type"] == "History"]
        historical.to_excel(writer, sheet_name='Historical (2015-2025)', index=False)
        
        # Forecast only (long format)
        forecast = df[df["Type"] == "Forecast"]
        forecast.to_excel(writer, sheet_name='Forecast (2026-2035)', index=False)
        
        # Wide format worksheets
        historical_wide = create_wide_format(historical)
        historical_wide.to_excel(writer, sheet_name='Historical Figures', index=False)
        
        forecast_wide = create_wide_format(forecast)
        forecast_wide.to_excel(writer, sheet_name='Forecasted Figures', index=False)
        
        # Period-based sheets
        for period_name, (start, end) in PERIODS.items():
            period_df = df[(df["Year"] >= start) & (df["Year"] <= end)]
            # Clean sheet name (max 31 chars)
            sheet_name = period_name[:31]
            period_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Summary by Region and Metric
        summary = df.groupby(["Region", "Metric", "Type"])["Value"].agg(
            ["sum", "mean", "count"]
        ).reset_index()
        summary.columns = ["Region", "Metric", "Type", "Total", "Average", "Count"]
        summary.to_excel(writer, sheet_name='Summary by Region', index=False)
    
    return output.getvalue()



def create_time_series_chart(
    df: pd.DataFrame,
    schools: list[str] | None,
    metric: str,
    title: str = None,
    show_all: bool = False
) -> go.Figure:
    """Create interactive time series chart comparing multiple schools.
    
    Args:
        df: DataFrame with forecast data
        schools: List of school names to compare (None if show_all=True)
        metric: Metric to display
        title: Optional chart title
        show_all: If True, aggregate all data instead of per-school
        
    Returns:
        Plotly figure object
    """
    # Filter by metric
    filtered = df[df["Metric"] == metric].copy()
    
    if show_all:
        # Aggregate by Year and Type
        agg = filtered.groupby(["Year", "Type"])["Value"].sum().reset_index()
        agg = agg.sort_values("Year")
        
        fig = go.Figure()
        
        # Historical data
        history = agg[agg["Type"] == "History"]
        if not history.empty:
            fig.add_trace(go.Scatter(
                x=history["Year"],
                y=history["Value"],
                name="All Schools (History)",
                mode="lines+markers",
                line=dict(color=COLORS["history"], width=3),
                marker=dict(size=8),
            ))
        
        # Forecast data
        forecast = agg[agg["Type"] == "Forecast"]
        if not forecast.empty:
            fig.add_trace(go.Scatter(
                x=forecast["Year"],
                y=forecast["Value"],
                name="All Schools (Forecast)",
                mode="lines+markers",
                line=dict(color=COLORS["forecast"], width=3, dash="dash"),
                marker=dict(size=8, symbol="diamond"),
            ))
    else:
        # Filter by selected schools
        filtered = filtered[filtered["School"].isin(schools)]
        filtered = filtered.sort_values(["School", "Year"])
        
        fig = go.Figure()
        school_colors = px.colors.qualitative.Set2
        
        for i, school in enumerate(schools):
            school_data = filtered[filtered["School"] == school]
            color = school_colors[i % len(school_colors)]
            
            # Historical data (solid line)
            history = school_data[school_data["Type"] == "History"]
            if not history.empty:
                fig.add_trace(go.Scatter(
                    x=history["Year"],
                    y=history["Value"],
                    name=f"{school[:30]}... (History)" if len(school) > 30 else f"{school} (History)",
                    mode="lines+markers",
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    legendgroup=school
                ))
            
            # Forecast data (dashed line)
            forecast = school_data[school_data["Type"] == "Forecast"]
            if not forecast.empty:
                fig.add_trace(go.Scatter(
                    x=forecast["Year"],
                    y=forecast["Value"],
                    name=f"{school[:30]}... (Forecast)" if len(school) > 30 else f"{school} (Forecast)",
                    mode="lines+markers",
                    line=dict(color=color, width=2, dash="dash"),
                    marker=dict(size=6, symbol="diamond"),
                    legendgroup=school
                ))
    
    # Add period shading
    period_colors = ["rgba(46,64,87,0.3)", "rgba(255,107,107,0.2)", 
                     "rgba(78,205,196,0.2)", "rgba(255,230,109,0.15)", "rgba(255,230,109,0.1)"]
    
    for i, (period_name, (start, end)) in enumerate(PERIODS.items()):
        fig.add_vrect(
            x0=start - 0.5, x1=end + 0.5,
            fillcolor=period_colors[i % len(period_colors)],
            opacity=0.5,
            layer="below",
            line_width=0,
            annotation_text=period_name.split(" (")[0],
            annotation_position="top left",
            annotation_font_size=9,
            annotation_font_color="rgba(255,255,255,0.6)"
        )
    
    # Layout
    fig.update_layout(
        title=title or f"{metric} Over Time",
        xaxis_title="Year",
        yaxis_title=metric,
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=150)
    )
    
    return fig


def main():
    """Main Streamlit application."""
    
    # Page config
    st.set_page_config(
        page_title="Philippine HEI Research Forecast",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for premium aesthetics
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
        }
        .stSelectbox label, .stMultiSelect label {
            color: #4ECDC4 !important;
            font-weight: 600;
        }
        h1 {
            background: linear-gradient(90deg, #4ECDC4, #44A08D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .metric-card {
            background: rgba(78, 205, 196, 0.1);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(78, 205, 196, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎓 Philippine HEI Research Productivity Forecast")
    st.markdown("*Analyzing research output trends for Higher Education Institutions (2015-2035)*")
    
    # Load data
    try:
        df = load_forecasts()
    except FileNotFoundError:
        st.error("⚠️ Forecast data not found! Please run the ETL and forecasting pipelines first.")
        st.code("uv run python src/etl.py\nuv run python src/forecasting.py", language="bash")
        return
    
    # === Sidebar Filters ===
    st.sidebar.header("🔧 Filters")
    
    # Metric selector with ALL option
    metrics = ["All Metrics"] + df["Metric"].unique().tolist()
    selected_metric = st.sidebar.selectbox(
        "📈 Select Metric",
        metrics,
        index=1  # Default to first actual metric
    )
    
    # Region filter with ALL option
    regions = ["All Regions"] + sorted(df["Region"].unique().tolist())
    selected_region = st.sidebar.selectbox(
        "🗺️ Filter by Region",
        regions,
        index=0
    )
    
    # Apply region filter
    if selected_region != "All Regions":
        df_filtered = df[df["Region"] == selected_region]
    else:
        df_filtered = df
    
    # School selector with ALL option
    available_schools = sorted(df_filtered["School"].unique().tolist())
    
    show_all_schools = st.sidebar.checkbox(
        "📊 Show All Schools (Aggregated)",
        value=True,
        help="When checked, shows aggregated data for all schools instead of individual school comparison"
    )
    
    if not show_all_schools:
        default_schools = available_schools[:3] if len(available_schools) >= 3 else available_schools
        selected_schools = st.sidebar.multiselect(
            "🏫 Select Schools to Compare",
            available_schools,
            default=default_schools,
            max_selections=6
        )
        
        if not selected_schools:
            st.warning("Please select at least one school from the sidebar.")
            return
    else:
        selected_schools = None
    
    # Period filter
    period_options = ["All Periods"] + list(PERIODS.keys())
    selected_period = st.sidebar.selectbox(
        "📅 Filter by Period",
        period_options,
        index=0
    )
    
    # Apply period filter
    if selected_period != "All Periods":
        start_year, end_year = PERIODS[selected_period]
        df_filtered = df_filtered[(df_filtered["Year"] >= start_year) & (df_filtered["Year"] <= end_year)]
    
    # === Export Section in Sidebar ===
    st.sidebar.markdown("---")
    st.sidebar.header("📥 Export Data")
    
    excel_data = export_to_excel(df)
    st.sidebar.download_button(
        label="📥 Download Excel Report",
        data=excel_data,
        file_name="hei_research_data_complete.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download complete dataset with historical and forecasted data"
    )
    
    # Main content
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    latest_year = df[df["Type"] == "History"]["Year"].max()
    
    with col1:
        total_schools = df["School"].nunique()
        st.metric("📚 Total Schools", total_schools)
    
    with col2:
        total_regions = df["Region"].nunique()
        st.metric("🗺️ Regions Covered", total_regions)
    
    with col3:
        st.metric("📅 Historical Range", f"2015-{latest_year}")
    
    with col4:
        st.metric("🔮 Forecast Range", f"{latest_year + 1}-2035")
    
    st.markdown("---")
    
    # === Main Analysis Tabs ===
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
        "🗺️ Geospatial Analysis",
        "📈 Time Series Analysis", 
        "📊 Period Comparison"
    ])
    
    with analysis_tab2:
        if selected_metric == "All Metrics":
            # Show separate charts for each metric
            for metric in df["Metric"].unique():
                st.subheader(f"📊 {metric} Trends")
                fig = create_time_series_chart(
                    df_filtered,
                    selected_schools,
                    metric,
                    title=f"{metric} - Historical vs Forecast",
                    show_all=show_all_schools
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f"📊 {selected_metric} Trends")
            fig = create_time_series_chart(
                df_filtered,
                selected_schools,
                selected_metric,
                title=f"{selected_metric} - Historical vs Forecast",
                show_all=show_all_schools
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with analysis_tab1:
        display_metric = selected_metric if selected_metric != "All Metrics" else "Publication Quantity"
        st.subheader(f"🗺️ Regional {display_metric} Distribution")
        
        # Apply region filter for map data
        if selected_region != "All Regions":
            map_df = df[df["Region"] == selected_region]
        else:
            map_df = df
        
        # View mode toggle - default to Period Evolution
        view_mode = st.radio(
            "📊 View Mode",
            ["Period Evolution", "Yearly Slider"],
            horizontal=True,
            help="Period Evolution: Animated comparison across all 5 strategic periods. Yearly Slider: View one year at a time."
        )
        
        if view_mode == "Yearly Slider":
            # Calculate year range based on period filter
            if selected_period != "All Periods":
                period_start, period_end = PERIODS[selected_period]
                min_year = period_start
                max_year = period_end
            else:
                min_year = int(df["Year"].min())
                max_year = int(df["Year"].max())
            
            map_year = st.slider(
                "📅 Select Year",
                min_value=min_year,
                max_value=max_year,
                value=min(max_year, max(min_year, 2025)),  # Default to 2025 or stay within range
                step=1,
                help="Slide to view regional distribution for different years"
            )
            
            # Determine period for the selected year
            year_period = "Unknown"
            for period_name, (start, end) in PERIODS.items():
                if start <= map_year <= end:
                    year_period = period_name
                    break
            
            # Year type indicator
            if map_year <= 2025:
                st.info(f"📊 **Historical Data** for {map_year} | Period: {year_period}")
            else:
                st.warning(f"🔮 **Forecasted Data** for {map_year} | Period: {year_period}")
            
            # Render the map with filtered data
            with st.spinner("Loading map..."):
                map_fig = plot_philippine_map(
                    map_df,
                    year=map_year,
                    metric=display_metric,
                    title=f"{display_metric} by Region ({map_year})"
                )
                st.plotly_chart(map_fig, use_container_width=True)
            
            # Regional summary for selected year (sorted from highest to lowest)
            st.markdown("##### Regional Summary (Top 5)")
            regional_summary = map_df[
                (map_df["Year"] == map_year) & (map_df["Metric"] == display_metric)
            ].groupby("Region")["Value"].sum().sort_values(ascending=False).head(5)
            
            if not regional_summary.empty:
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Create bar chart with explicit sorting
                    summary_sorted = regional_summary.reset_index()
                    summary_sorted.columns = ["Region", display_metric]
                    bar_fig = px.bar(
                        summary_sorted,
                        x="Region",
                        y=display_metric,
                        title="Top 5 Regions",
                        template="plotly_dark",
                        color=display_metric,
                        color_continuous_scale=["#2E4057", "#4ECDC4", "#FFE66D"]
                    )
                    bar_fig.update_layout(
                        xaxis={"categoryorder": "total descending"},
                        showlegend=False,
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(bar_fig, use_container_width=True)
                with col2:
                    st.dataframe(summary_sorted, use_container_width=True)
        
        else:
            # Period Evolution - animated bubble map
            # Apply period filter if selected
            if selected_period != "All Periods":
                period_start, period_end = PERIODS[selected_period]
                period_map_df = map_df[(map_df["Year"] >= period_start) & (map_df["Year"] <= period_end)]
                st.info(f"🎬 **Period View**: Showing data for {selected_period}")
            else:
                period_map_df = map_df
                st.info("🎬 **Period Evolution View**: Animated comparison across all 5 strategic periods. "
                       "Use the Play button or slider to navigate through periods.")
            
            with st.spinner("Generating animated map..."):
                period_fig = plot_period_geospatial_comparison(period_map_df, display_metric)
                st.plotly_chart(period_fig, use_container_width=True)
            
            st.markdown("""
            **Period Definitions:**
            - **Pre-Pandemic (2015-2019):** Baseline research productivity
            - **During Pandemic (2020-2022):** COVID-19 impact period
            - **Post-Pandemic (2023-2025):** Recovery phase
            - **Forecast Phase 1 (2026-2030):** Near-term projection
            - **Forecast Phase 2 (2031-2035):** Long-term projection
            """)
    
    with analysis_tab3:
        st.subheader("📊 Period-Based Comparison")
        st.markdown("""
        Compare research productivity across defined periods:
        - **Pre-Pandemic:** 2015-2019
        - **During Pandemic:** 2020-2022
        - **Post-Pandemic:** 2023-2025
        - **Forecast Phase 1:** 2026-2030
        - **Forecast Phase 2:** 2031-2035
        """)
        
        display_metric_period = selected_metric if selected_metric != "All Metrics" else "Publication Quantity"
        
        # Apply region filter for period comparison
        if selected_region != "All Regions":
            period_comparison_df = df[df["Region"] == selected_region]
        else:
            period_comparison_df = df
        
        # Calculate period summaries
        period_data = []
        for period_name, (start, end) in PERIODS.items():
            period_df = period_comparison_df[(period_comparison_df["Year"] >= start) & (period_comparison_df["Year"] <= end) & 
                          (period_comparison_df["Metric"] == display_metric_period)]
            total = period_df["Value"].sum()
            avg_per_year = period_df.groupby("Year")["Value"].sum().mean()
            period_data.append({
                "Period": period_name,
                "Total": total,
                "Avg per Year": avg_per_year,
                "Years": f"{start}-{end}"
            })
        
        period_summary = pd.DataFrame(period_data)
        
        # Bar chart of periods
        fig = px.bar(
            period_summary,
            x="Period",
            y="Total",
            color="Period",
            title=f"{display_metric_period} by Period",
            template="plotly_dark",
            color_discrete_sequence=["#2E4057", "#FF6B6B", "#4ECDC4", "#FFE66D", "#FFA07A"]
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(
            period_summary.style.format({"Total": "{:,.0f}", "Avg per Year": "{:,.1f}"}),
            use_container_width=True
        )
    
    # Detailed comparison table
    st.markdown("---")
    st.subheader("📋 Detailed Data View")
    
    tab1, tab2 = st.tabs(["Historical Data", "Forecast Data"])
    
    display_metric_table = selected_metric if selected_metric != "All Metrics" else "Publication Quantity"
    
    with tab1:
        history_filter = df_filtered[
            (df_filtered["Metric"] == display_metric_table) &
            (df_filtered["Type"] == "History")
        ]
        if not show_all_schools and selected_schools:
            history_filter = history_filter[history_filter["School"].isin(selected_schools)]
        
        history_df = history_filter.pivot_table(
            index="School",
            columns="Year",
            values="Value",
            aggfunc="first"
        ).round(2)
        st.dataframe(history_df, use_container_width=True)
    
    with tab2:
        forecast_filter = df_filtered[
            (df_filtered["Metric"] == display_metric_table) &
            (df_filtered["Type"] == "Forecast")
        ]
        if not show_all_schools and selected_schools:
            forecast_filter = forecast_filter[forecast_filter["School"].isin(selected_schools)]
        
        forecast_df = forecast_filter.pivot_table(
            index="School",
            columns="Year",
            values="Value",
            aggfunc="first"
        ).round(2)
        st.dataframe(forecast_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "📈 Forecasts generated using Holt's Linear Trend method | "
        "Data: CHED Philippine HEI Research Productivity Dataset | "
        "Publication & Citation counts are rounded to integers"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
