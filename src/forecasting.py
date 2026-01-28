"""Forecasting engine for Philippine HEI Research Productivity data.

Applies Holt's Linear Trend method to each School + Metric combination,
with fallback to Simple Moving Average when insufficient historical data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.holtwinters import Holt


# === Constants ===
PROCESSED_DATA_PATH = Path("data/processed/clean_metrics.parquet")
FORECAST_OUTPUT_PATH = Path("data/processed/forecasts.parquet")

# Period definitions
TRAINING_START = 2015
TRAINING_END = 2025
FORECAST_START = 2026
FORECAST_END = 2035
FORECAST_HORIZON = FORECAST_END - FORECAST_START + 1  # 10 years

# Minimum non-zero data points required for Holt's method
MIN_HISTORY_POINTS = 3

# Metrics that should be rounded to integers (discrete counts)
DISCRETE_METRICS = ["Publication Quantity", "Citation Quantity"]


def load_clean_data(path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load the cleaned metrics parquet file.
    
    Args:
        path: Path to the clean_metrics.parquet file
        
    Returns:
        Long-format DataFrame with historical data
    """
    return pd.read_parquet(path)


def simple_moving_average(series: pd.Series, periods: int = FORECAST_HORIZON) -> pd.Series:
    """Apply Simple Moving Average using last 3 years.
    
    Fallback method when Holt's Linear Trend cannot be applied.
    
    Args:
        series: Historical values (sorted by year)
        periods: Number of forecast periods
        
    Returns:
        Series of forecasted values
    """
    # Use mean of last 3 values (or all values if less than 3)
    window = min(3, len(series))
    avg = series.tail(window).mean()
    return pd.Series([avg] * periods)


def holts_linear_trend(series: pd.Series, periods: int = FORECAST_HORIZON) -> pd.Series:
    """Apply Holt's Linear Trend method.
    
    Args:
        series: Historical values (sorted by year)
        periods: Number of forecast periods
        
    Returns:
        Series of forecasted values
    """
    try:
        model = Holt(series.values, initialization_method="estimated")
        fit = model.fit(optimized=True)
        forecast = fit.forecast(periods)
        return pd.Series(forecast)
    except Exception:
        # Fallback to SMA if Holt's fails
        return simple_moving_average(series, periods)


def forecast_series(series: pd.Series, periods: int = FORECAST_HORIZON) -> pd.Series:
    """Apply appropriate forecasting method based on data availability.
    
    Logic:
    - If non-zero data points < 3: Use Simple Moving Average
    - Otherwise: Use Holt's Linear Trend
    
    Args:
        series: Historical values (sorted by year)
        periods: Number of forecast periods
        
    Returns:
        Series of forecasted values
    """
    # Count non-zero points
    non_zero_count = (series > 0).sum()
    
    if non_zero_count < MIN_HISTORY_POINTS:
        return simple_moving_average(series, periods)
    else:
        return holts_linear_trend(series, periods)


def generate_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """Generate forecasts for each School + Metric combination.
    
    Args:
        df: Long-format DataFrame with historical data
        
    Returns:
        DataFrame containing both historical and forecasted rows,
        tagged with 'Type' column ("History" vs "Forecast")
    """
    # Filter to training period
    df_train = df[(df["Year"] >= TRAINING_START) & (df["Year"] <= TRAINING_END)].copy()
    
    # Add Type column to historical data
    df_train["Type"] = "History"
    
    all_forecasts = []
    
    # Group by School and Metric
    groups = df_train.groupby(["Region Code", "Region", "School", "Metric"])
    total_groups = len(groups)
    
    print(f"Generating forecasts for {total_groups} School-Metric combinations...")
    
    for i, ((region_code, region, school, metric), group) in enumerate(groups):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{total_groups}")
        
        # Sort by year and get values
        group = group.sort_values("Year")
        series = group.set_index("Year")["Value"]
        
        # Generate forecast
        forecast_values = forecast_series(series)
        
        # Create forecast rows
        forecast_years = list(range(FORECAST_START, FORECAST_END + 1))
        forecast_rows = pd.DataFrame({
            "Region Code": region_code,
            "Region": region,
            "School": school,
            "Year": forecast_years,
            "Metric": metric,
            "Value": forecast_values.values,
            "Type": "Forecast"
        })
        
        all_forecasts.append(forecast_rows)
    
    # Combine historical and forecasted data
    df_forecasts = pd.concat(all_forecasts, ignore_index=True)
    result = pd.concat([df_train, df_forecasts], ignore_index=True)
    
    # Ensure proper data types
    result["Year"] = result["Year"].astype(int)
    result["Value"] = result["Value"].astype(float)
    
    # Clip negative forecasts to 0 (counts can't be negative)
    result.loc[result["Value"] < 0, "Value"] = 0.0
    
    # Round discrete metrics to nearest integer
    for metric in DISCRETE_METRICS:
        mask = result["Metric"] == metric
        result.loc[mask, "Value"] = result.loc[mask, "Value"].round(0)
    
    return result


def save_forecasts(df: pd.DataFrame, path: Path = FORECAST_OUTPUT_PATH) -> None:
    """Save forecasts to Parquet format.
    
    Args:
        df: DataFrame with historical and forecasted data
        path: Output path for the Parquet file
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use categorical dtype for efficiency
    df = df.copy()
    for col in ["Region Code", "Region", "Metric", "Type"]:
        df[col] = df[col].astype("category")
    
    df.to_parquet(path, index=False)
    print(f"Saved {len(df):,} records to {path}")


def run_forecasting_pipeline(
    input_path: Path = PROCESSED_DATA_PATH,
    output_path: Path = FORECAST_OUTPUT_PATH
) -> pd.DataFrame:
    """Complete forecasting pipeline: load, forecast, and save.
    
    Args:
        input_path: Path to clean_metrics.parquet
        output_path: Path for forecasts.parquet output
        
    Returns:
        DataFrame with historical and forecasted data
    """
    print(f"Loading data from {input_path}...")
    df = load_clean_data(input_path)
    print(f"  Loaded {len(df):,} historical records")
    
    print("Generating forecasts...")
    df_with_forecasts = generate_forecasts(df)
    
    history_count = len(df_with_forecasts[df_with_forecasts["Type"] == "History"])
    forecast_count = len(df_with_forecasts[df_with_forecasts["Type"] == "Forecast"])
    print(f"  Generated {forecast_count:,} forecast records")
    print(f"  Total records: {history_count + forecast_count:,}")
    
    print("Saving forecasts...")
    save_forecasts(df_with_forecasts, output_path)
    
    return df_with_forecasts


# === Entry point for testing ===
if __name__ == "__main__":
    df = run_forecasting_pipeline()
    
    print("\n=== Summary ===")
    print(f"Years: {sorted(df['Year'].unique())}")
    print(f"Metrics: {df['Metric'].unique().tolist()}")
    print(f"Schools: {df['School'].nunique()}")
    
    print("\n=== Sample Forecast (first 3 schools for Publications) ===")
    sample = df[
        (df["Metric"] == "Publication Quantity") &
        (df["Type"] == "Forecast") &
        (df["Year"] == 2030)
    ].head(6)
    print(sample[["School", "Year", "Value", "Type"]])
