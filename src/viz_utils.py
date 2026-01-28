"""Visualization utilities for Philippine HEI Research Analytics.

Contains geographic mappings and Plotly/Mapbox helper functions
for rendering Philippine regional data.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# === Philippine Geographic Constants ===
# Center coordinates for the Philippines
PH_CENTER = {"lat": 12.8797, "lon": 121.7740}
PH_DEFAULT_ZOOM = 5

# Region Code to Geographic Coordinates Mapping
# Coordinates represent approximate regional centroids
REGION_COORDINATES = {
    "NCR": {"lat": 14.5995, "lon": 120.9842, "name": "National Capital Region"},
    "CAR": {"lat": 17.3513, "lon": 121.1719, "name": "Cordillera Administrative Region"},
    "REGION I": {"lat": 16.0832, "lon": 120.6200, "name": "Ilocos Region"},
    "REGION II": {"lat": 16.9754, "lon": 121.8107, "name": "Cagayan Valley"},
    "REGION III": {"lat": 15.4828, "lon": 120.7120, "name": "Central Luzon"},
    "REGION IV-A": {"lat": 14.1008, "lon": 121.0794, "name": "CALABARZON"},
    "REGION IV-B": {"lat": 12.8797, "lon": 121.7740, "name": "MIMAROPA"},
    "REGION V": {"lat": 13.4210, "lon": 123.4137, "name": "Bicol Region"},
    "REGION VI": {"lat": 10.7202, "lon": 122.5621, "name": "Western Visayas"},
    "REGION VII": {"lat": 9.8500, "lon": 123.8907, "name": "Central Visayas"},
    "REGION VIII": {"lat": 11.2543, "lon": 124.9936, "name": "Eastern Visayas"},
    "REGION IX": {"lat": 7.8527, "lon": 123.0311, "name": "Zamboanga Peninsula"},
    "REGION X": {"lat": 8.0202, "lon": 124.6857, "name": "Northern Mindanao"},
    "REGION XI": {"lat": 7.1907, "lon": 125.4553, "name": "Davao Region"},
    "REGION XII": {"lat": 6.2707, "lon": 124.6857, "name": "SOCCSKSARGEN"},
    "REGION XIII": {"lat": 8.8017, "lon": 125.7407, "name": "Caraga"},
    "BARMM": {"lat": 6.9568, "lon": 124.2421, "name": "Bangsamoro Autonomous Region"},
}


def get_region_coords(region_code: str) -> dict:
    """Get latitude/longitude for a Philippine region.
    
    Args:
        region_code: Standard Philippine region code (e.g., 'NCR', 'REGION V')
        
    Returns:
        Dictionary with 'lat', 'lon', and 'name' keys
    """
    return REGION_COORDINATES.get(region_code, PH_CENTER)


def create_bubble_map(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    size_scale: float = 1.0
) -> go.Figure:
    """Create a bubble map of Philippine regions.
    
    Args:
        df: DataFrame with 'Region Code' and value column
        value_col: Column name containing values for bubble size
        title: Chart title
        size_scale: Multiplier for bubble sizes
        
    Returns:
        Plotly figure object
    """
    # Aggregate by region
    region_data = df.groupby("Region Code")[value_col].sum().reset_index()
    
    # Add coordinates
    region_data["lat"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lat"]
    )
    region_data["lon"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lon"]
    )
    region_data["region_name"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, {"name": x})["name"]
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=region_data["lat"],
        lon=region_data["lon"],
        mode="markers",
        marker=dict(
            size=region_data[value_col] * size_scale,
            sizemode="area",
            sizeref=2. * max(region_data[value_col]) / (40. ** 2),
            sizemin=4,
            color=region_data[value_col],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title=value_col)
        ),
        text=region_data["region_name"],
        hovertemplate=(
            "<b>%{text}</b><br>"
            f"{value_col}: %{{marker.color:,.0f}}<br>"
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title=title,
        mapbox=dict(
            style="carto-positron",
            center=PH_CENTER,
            zoom=PH_DEFAULT_ZOOM
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        template="plotly_dark"
    )
    
    return fig


def create_choropleth_placeholder(
    df: pd.DataFrame,
    value_col: str,
    title: str
) -> go.Figure:
    """Placeholder for choropleth map (requires GeoJSON).
    
    Note: Full choropleth requires Philippine regional GeoJSON boundaries.
    This function returns a bubble map as a fallback.
    
    Args:
        df: DataFrame with regional data
        value_col: Column for color intensity
        title: Chart title
        
    Returns:
        Plotly figure (bubble map fallback)
    """
    return create_bubble_map(df, value_col, title)


# === Color Palettes ===
IRAP_COLORS = {
    "primary": "#4ECDC4",
    "secondary": "#44A08D",
    "accent": "#FF6B6B",
    "background": "#0E1117",
    "history": "#3366CC",
    "forecast": "#FF6B6B",
    "neutral": "#666666"
}

METRIC_COLORS = {
    "Publication Quantity": "#4ECDC4",
    "Citation Quantity": "#FF6B6B",
    "Field-Weighted Citation Impact": "#FFE66D"
}


def plot_philippine_map(
    df: pd.DataFrame,
    year: int,
    metric: str,
    title: str = None
) -> go.Figure:
    """Create an interactive map of Philippine regions for a specific year.
    
    Displays regional aggregated data as bubbles on a Mapbox map.
    Inspired by DepEd-style choropleth visualizations.
    
    Args:
        df: DataFrame with columns ['Region Code', 'Region', 'Year', 'Metric', 'Value']
        year: Year to visualize (2015-2035)
        metric: Metric to display ('Publication Quantity' or 'Citation Quantity')
        title: Optional chart title
        
    Returns:
        Plotly figure object with map visualization
    """
    # Filter data for selected year and metric
    filtered = df[(df["Year"] == year) & (df["Metric"] == metric)]
    
    if filtered.empty:
        # Return empty map with message
        fig = go.Figure()
        fig.update_layout(
            title=f"No data available for {year}",
            mapbox=dict(
                style="carto-positron",
                center=PH_CENTER,
                zoom=PH_DEFAULT_ZOOM
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            template="plotly_dark"
        )
        return fig
    
    # Aggregate by region
    region_data = (
        filtered
        .groupby(["Region Code", "Region"], as_index=False)["Value"]
        .sum()
    )
    
    # Add coordinates
    region_data["lat"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lat"]
    )
    region_data["lon"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, PH_CENTER)["lon"]
    )
    region_data["region_name"] = region_data["Region Code"].apply(
        lambda x: REGION_COORDINATES.get(x, {"name": x}).get("name", x)
    )
    
    # Get color for metric
    color = METRIC_COLORS.get(metric, IRAP_COLORS["primary"])
    
    # Determine if it's forecast or historical
    data_type = "Forecast" if year > 2025 else "Historical"
    
    fig = go.Figure()
    
    # Create bubble map trace
    fig.add_trace(go.Scattermapbox(
        lat=region_data["lat"],
        lon=region_data["lon"],
        mode="markers+text",
        marker=dict(
            size=region_data["Value"],
            sizemode="area",
            sizeref=2. * max(region_data["Value"]) / (50. ** 2),
            sizemin=8,
            color=region_data["Value"],
            colorscale=[
                [0, "#2E4057"],      # Dark blue
                [0.25, "#4ECDC4"],   # Teal
                [0.5, "#FFE66D"],    # Yellow
                [0.75, "#FF6B6B"],   # Coral
                [1, "#C44536"]       # Red
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text=metric, font=dict(size=12)),
                thickness=15,
                len=0.7,
                bgcolor="rgba(0,0,0,0.5)",
                tickfont=dict(color="white")
            )
        ),
        text=region_data["Region Code"],
        textposition="middle center",
        textfont=dict(size=10, color="white", family="Arial Black"),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"Region Code: %{{text}}<br>"
            f"{metric}: %{{marker.color:,.0f}}<br>"
            f"Type: {data_type}<br>"
            "<extra></extra>"
        ),
        customdata=region_data[["region_name"]].values
    ))
    
    # Layout with premium styling
    chart_title = title or f"{metric} by Region ({year})"
    
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#4ECDC4"),
            x=0.5,
            xanchor="center"
        ),
        mapbox=dict(
            style="carto-darkmatter",
            center=PH_CENTER,
            zoom=PH_DEFAULT_ZOOM
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        height=600
    )
    
    return fig


# === Period Definitions ===
PERIOD_RANGES = {
    "Pre-Pandemic (2015-2019)": (2015, 2019),
    "During Pandemic (2020-2022)": (2020, 2022),
    "Post-Pandemic (2023-2025)": (2023, 2025),
    "Forecast Phase 1 (2026-2030)": (2026, 2030),
    "Forecast Phase 2 (2031-2035)": (2031, 2035),
}

PERIOD_ORDER = [
    "Pre-Pandemic (2015-2019)",
    "During Pandemic (2020-2022)",
    "Post-Pandemic (2023-2025)",
    "Forecast Phase 1 (2026-2030)",
    "Forecast Phase 2 (2031-2035)",
]


def assign_period(year: int) -> str:
    """Map a year to its corresponding strategic period.
    
    Args:
        year: Year value (2015-2035)
        
    Returns:
        Period name string
    """
    for period_name, (start, end) in PERIOD_RANGES.items():
        if start <= year <= end:
            return period_name
    return "Unknown"


def plot_period_geospatial_comparison(
    df: pd.DataFrame,
    metric_name: str
) -> go.Figure:
    """Create an animated Bubble Map showing metric evolution across 5 strategic periods.
    
    Uses average annual value (not sum) to ensure fair comparison between
    periods of different lengths (3-year vs 5-year).
    
    Args:
        df: DataFrame with columns ['Region Code', 'Region', 'Year', 'Metric', 'Value']
        metric_name: Metric to visualize (e.g., 'Publication Quantity')
        
    Returns:
        Plotly figure with animation controls
    """
    # Filter by metric
    filtered = df[df["Metric"] == metric_name].copy()
    
    if filtered.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No data available for {metric_name}",
            template="plotly_dark"
        )
        return fig
    
    # Add Period column
    filtered["Period"] = filtered["Year"].apply(assign_period)
    
    # Aggregate: Average annual value per Region per Period
    # This ensures fair comparison between 3-year and 5-year periods
    geo_df = (
        filtered
        .groupby(["Region Code", "Region", "Period"], as_index=False, observed=False)["Value"]
        .mean()
    )
    
    # Handle NaN values - fill with 0 and filter out zeros for cleaner visualization
    geo_df["Value"] = geo_df["Value"].fillna(0)
    geo_df = geo_df[geo_df["Value"] > 0]  # Remove regions with no data
    
    if geo_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No valid data available for {metric_name}",
            template="plotly_dark"
        )
        return fig
    
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
    
    # Calculate global max for fixed color scale
    max_value = geo_df["Value"].max()
    
    # Create animated scatter mapbox
    fig = px.scatter_mapbox(
        geo_df,
        lat="lat",
        lon="lon",
        size="Value",
        color="Value",
        hover_name="region_name",
        hover_data={"Region Code": True, "Value": ":.1f", "lat": False, "lon": False},
        animation_frame="Period",
        category_orders={"Period": PERIOD_ORDER},
        zoom=PH_DEFAULT_ZOOM,
        center=PH_CENTER,
        mapbox_style="carto-darkmatter",
        title=f"Regional Evolution of {metric_name} (Annual Average)",
        color_continuous_scale=[
            [0, "#2E4057"],      # Dark blue
            [0.25, "#4ECDC4"],   # Teal
            [0.5, "#FFE66D"],    # Yellow
            [0.75, "#FF6B6B"],   # Coral
            [1, "#C44536"]       # Red
        ],
        range_color=[0, max_value],  # Fixed scale across all periods
        size_max=50,
    )
    
    # Premium styling
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        height=650,
        title=dict(
            font=dict(size=18, color="#4ECDC4"),
            x=0.5,
            xanchor="center"
        ),
        coloraxis_colorbar=dict(
            title=dict(text=f"Avg {metric_name}", font=dict(size=12)),
            thickness=15,
            len=0.7,
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        # Animation settings
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=0,
            x=0.1,
            xanchor="right",
            buttons=[
                dict(label="▶ Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 1500, "redraw": True},
                                  "fromcurrent": True}]),
                dict(label="⏸ Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate"}])
            ]
        )]
    )
    
    # Update slider styling
    if fig.layout.sliders:
        fig.layout.sliders[0].update(
            currentvalue=dict(
                prefix="Period: ",
                font=dict(size=14, color="#4ECDC4")
            ),
            len=0.8,
            x=0.1,
        )
    
    return fig
