"""Pipeline orchestrator for Philippine HEI Research Productivity analysis.

Runs the complete ETL and forecasting pipeline in sequence.
"""

from pathlib import Path
from src.etl import load_and_transform
from src.forecasting import run_forecasting_pipeline


def main():
    """Run the complete data pipeline."""
    print("=" * 60)
    print("Philippine HEI Research Productivity Pipeline")
    print("=" * 60)
    
    # Step 1: ETL
    print("\n[Step 1/2] Running ETL Pipeline...")
    print("-" * 40)
    df_clean = load_and_transform()
    
    # Step 2: Forecasting
    print("\n[Step 2/2] Running Forecasting Pipeline...")
    print("-" * 40)
    df_forecasts = run_forecasting_pipeline()
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Clean data:  data/processed/clean_metrics.parquet")
    print(f"  - Forecasts:   data/processed/forecasts.parquet")
    print(f"\nTo launch the dashboard:")
    print(f"  uv run streamlit run app.py")


if __name__ == "__main__":
    main()
