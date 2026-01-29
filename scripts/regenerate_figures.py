"""
Script to regenerate all geospatial figures for the HEI Executive Report.

Iterates through all 5 periods and saves Light Mode maps to reports/ subdirectories.
This script uses the updated viz_utils module with carto-positron light map style.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.viz_utils import (
    PERIOD_RANGES,
    PERIOD_ORDER,
    REGION_COORDINATES,
    PH_CENTER,
    PH_DEFAULT_ZOOM,
    assign_period,
)


def load_data() -> pd.DataFrame:
    """Load the forecast data from parquet."""
    data_path = project_root / "data" / "processed" / "forecasts.parquet"
    return pd.read_parquet(data_path)


def create_period_map(
    df: pd.DataFrame,
    period_name: str,
    metric_name: str,
) -> go.Figure:
    """Create a static bubble map for a specific period and metric.
    
    Uses Light Mode styling for print-ready output.
    """
    start_year, end_year = PERIOD_RANGES[period_name]
    
    # Filter data for this period and metric
    filtered = df[
        (df["Year"] >= start_year) &
        (df["Year"] <= end_year) &
        (df["Metric"] == metric_name)
    ].copy()
    
    if filtered.empty:
        print(f"  ⚠ No data for {metric_name} in {period_name}")
        return None
    
    # Aggregate: average annual value per region
    geo_df = (
        filtered
        .groupby(["Region Code", "Region"], as_index=False, observed=False)["Value"]
        .mean()
    )
    
    # Add coordinates
    geo_df["lat"] = geo_df["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lat"]
    )
    geo_df["lon"] = geo_df["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lon"]
    )
    geo_df["region_name"] = geo_df["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, {"name": x}).get("name", x)
    )
    
    # Remove zeros for cleaner visualization
    geo_df = geo_df[geo_df["Value"] > 0]
    
    if geo_df.empty:
        print(f"  ⚠ No non-zero data for {metric_name} in {period_name}")
        return None
    
    max_value = geo_df["Value"].max()
    
    # Create static scatter mapbox
    fig = px.scatter_mapbox(
        geo_df,
        lat="lat",
        lon="lon",
        size="Value",
        color="Value",
        hover_name="region_name",
        hover_data={"Region Code": True, "Value": ":.1f", "lat": False, "lon": False},
        zoom=PH_DEFAULT_ZOOM,
        center=PH_CENTER,
        mapbox_style="carto-positron",  # Light mode map style
        title=f"{metric_name} - {period_name}",
        color_continuous_scale=[
            [0, "#2E4057"],      # Dark blue
            [0.25, "#4ECDC4"],   # Teal
            [0.5, "#FFE66D"],    # Yellow
            [0.75, "#FF6B6B"],   # Coral
            [1, "#C44536"]       # Red
        ],  # Original color gradient
        range_color=[0, max_value],
        size_max=50,
    )
    
    # Apply light mode styling for print
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black'),
        template="plotly_white",
        height=700,
        width=900,
        title=dict(
            font=dict(size=18, color='#1a365d'),
            x=0.5,
            xanchor="center"
        ),
        coloraxis_colorbar=dict(
            title=dict(text=f"Avg {metric_name}", font=dict(size=12, color='black')),
            thickness=15,
            len=0.7,
            tickfont=dict(color='black'),
        ),
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
    )
    
    return fig


def main():
    print("=" * 60)
    print("HEI Report Figure Regeneration - Light Mode")
    print("=" * 60)
    
    # Load data
    print("\n📊 Loading forecast data...")
    df = load_data()
    print(f"   Loaded {len(df):,} rows")
    
    # Metric mapping for filenames
    metric_files = {
        "Publication Quantity": "pub.png",
        "Citation Quantity": "citation.png",
        "Field-Weighted Citation Impact": "fwci.png",
    }
    
    # Period folder mapping
    period_folders = {
        "Pre-Pandemic (2015-2019)": "1. pre_pandemic",
        "During Pandemic (2020-2022)": "2. during_pandemic",
        "Post-Pandemic (2023-2025)": "3. post_pandemic",
        "Forecast Phase 1 (2026-2030)": "4. forecast_1",
        "Forecast Phase 2 (2031-2035)": "5. forecast_2",
    }
    
    reports_dir = project_root / "reports"
    
    # Generate figures for each period
    for period_name in PERIOD_ORDER:
        folder_name = period_folders[period_name]
        output_dir = reports_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 {period_name}")
        
        for metric_name, filename in metric_files.items():
            fig = create_period_map(df, period_name, metric_name)
            
            if fig is not None:
                output_path = output_dir / filename
                fig.write_image(str(output_path), scale=2)  # High resolution
                print(f"   ✓ Saved: {output_path.relative_to(project_root)}")
    
    print("\n" + "=" * 60)
    print("✅ All figures regenerated with Light Mode styling!")
    print("=" * 60)


if __name__ == "__main__":
    main()
