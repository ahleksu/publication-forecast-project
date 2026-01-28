"""Streamlit Dashboard for Philippine HEI Research Productivity Analysis.

Provides interactive visualization of historical and forecasted research metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# === Constants ===
FORECAST_DATA_PATH = Path("data/processed/forecasts.parquet")

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


def create_time_series_chart(
    df: pd.DataFrame,
    schools: list[str],
    metric: str,
    title: str = None
) -> go.Figure:
    """Create interactive time series chart comparing multiple schools.
    
    Args:
        df: DataFrame with forecast data
        schools: List of school names to compare
        metric: Metric to display
        title: Optional chart title
        
    Returns:
        Plotly figure object
    """
    # Filter data
    filtered = df[(df["School"].isin(schools)) & (df["Metric"] == metric)]
    
    # Sort by year
    filtered = filtered.sort_values(["School", "Year"])
    
    # Create figure
    fig = go.Figure()
    
    # Color palette for schools
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
    
    # Add vertical line at forecast start
    fig.add_vline(
        x=2025.5,
        line_dash="dot",
        line_color="rgba(255,255,255,0.3)",
        annotation_text="Forecast Start",
        annotation_position="top"
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
    
    # Sidebar
    st.sidebar.header("🔧 Filters")
    
    # Metric selector
    metrics = df["Metric"].unique().tolist()
    selected_metric = st.sidebar.selectbox(
        "📈 Select Metric",
        metrics,
        index=0
    )
    
    # Region filter
    regions = sorted(df["Region"].unique().tolist())
    selected_region = st.sidebar.selectbox(
        "🗺️ Filter by Region",
        ["All Regions"] + regions,
        index=0
    )
    
    # Apply region filter
    if selected_region != "All Regions":
        df_filtered = df[df["Region"] == selected_region]
    else:
        df_filtered = df
    
    # School selector (multi-select)
    available_schools = sorted(df_filtered["School"].unique().tolist())
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
    
    # Main content
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    latest_year = df[df["Type"] == "History"]["Year"].max()
    forecast_year = 2030
    
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
    
    # Time series chart
    st.subheader(f"📊 {selected_metric} Trends")
    
    fig = create_time_series_chart(
        df_filtered,
        selected_schools,
        selected_metric,
        title=f"{selected_metric} - Historical vs Forecast"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed comparison table
    st.subheader("📋 Detailed Comparison")
    
    tab1, tab2 = st.tabs(["Historical Data", "Forecast Data"])
    
    with tab1:
        history_df = df_filtered[
            (df_filtered["School"].isin(selected_schools)) &
            (df_filtered["Metric"] == selected_metric) &
            (df_filtered["Type"] == "History")
        ].pivot_table(
            index="School",
            columns="Year",
            values="Value",
            aggfunc="first"
        ).round(2)
        st.dataframe(history_df, use_container_width=True)
    
    with tab2:
        forecast_df = df_filtered[
            (df_filtered["School"].isin(selected_schools)) &
            (df_filtered["Metric"] == selected_metric) &
            (df_filtered["Type"] == "Forecast")
        ].pivot_table(
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
        "Data: CHED Philippine HEI Research Productivity Dataset"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
