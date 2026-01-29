"""ETL module for Philippine HEI Research Productivity data.

Handles loading, cleaning, and transforming the multi-level Excel dataset
from wide format to long format for analysis and forecasting.
"""

import pandas as pd
from pathlib import Path


# === Constants ===
RAW_DATA_PATH = Path("data/raw/MASTER DATASET PRODUCTIVITYv2.xlsx")
PROCESSED_DATA_PATH = Path("data/processed/clean_metrics.parquet")
SHEET_NAME = "Prepared"

# Metadata columns that are NOT metric data
METADATA_COLS = ["REGION CODE", "REGION", "SCHOOL"]


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load Excel file with multi-level headers.
    
    Args:
        path: Path to the Excel file
        
    Returns:
        DataFrame with MultiIndex columns (Metric, Year)
    """
    df = pd.read_excel(
        path,
        sheet_name=SHEET_NAME,
        header=[0, 1],  # Capture both header rows
        engine="openpyxl"
    )
    return df


def parse_multiindex_columns(df: pd.DataFrame) -> tuple[list[str], dict[str, list[int]]]:
    """Parse MultiIndex columns to extract metrics and year mappings.
    
    Args:
        df: DataFrame with MultiIndex columns
        
    Returns:
        Tuple of (metadata_cols, metric_year_mapping)
        - metadata_cols: List of metadata column tuples
        - metric_year_mapping: Dict mapping metric names to list of years
    
    Note:
        Excel structure has metadata in format: ('Unnamed: X_level_0', 'COLUMN_NAME')
        Metric data is in format: ('Metric Name', Year)
    """
    metadata_cols = []
    metric_year_mapping = {}
    
    for col in df.columns:
        level0, level1 = col
        level0_str = str(level0)
        level1_str = str(level1)
        
        # Metadata columns have "Unnamed" in level0 and the actual name in level1
        if level0_str.startswith("Unnamed") and level1_str in METADATA_COLS:
            metadata_cols.append(col)
        elif level0_str.startswith("Unnamed"):
            # Other unnamed columns - skip or treat as metadata
            continue
        else:
            # This is a metric column - extract metric name and year
            metric_name = level0_str.strip()
            try:
                year = int(level1)
            except (ValueError, TypeError):
                # Skip non-numeric year columns
                continue
            
            if metric_name not in metric_year_mapping:
                metric_year_mapping[metric_name] = []
            metric_year_mapping[metric_name].append(year)
    
    return metadata_cols, metric_year_mapping


def melt_to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """Transform wide format DataFrame to long format.
    
    Target Schema:
    - Region Code (str)
    - Region (str)
    - School (str)
    - Year (int)
    - Metric (str)
    - Value (float)
    
    Args:
        df: DataFrame with MultiIndex columns
        
    Returns:
        Long format DataFrame with target schema
    """
    metadata_cols, metric_year_mapping = parse_multiindex_columns(df)
    
    # Extract metadata - flatten the MultiIndex for metadata columns
    # Column structure: ('Unnamed: X_level_0', 'COLUMN_NAME')
    # The actual column name is always in level1
    metadata_df = pd.DataFrame()
    for col in metadata_cols:
        level0, level1 = col
        # level1 contains the actual column name (e.g., 'REGION CODE')
        col_name = str(level1)
        metadata_df[col_name] = df[col]
    
    # Rename to target schema
    rename_map = {
        "REGION CODE": "Region Code",
        "REGION": "Region", 
        "SCHOOL": "School"
    }
    metadata_df = metadata_df.rename(columns=rename_map)
    
    # Melt each metric separately and concatenate
    all_melted = []
    
    for metric_name, years in metric_year_mapping.items():
        # Select columns for this metric
        metric_cols = [(metric_name, year) for year in years]
        existing_cols = [c for c in metric_cols if c in df.columns]
        
        if not existing_cols:
            continue
            
        # Create a temporary DataFrame with just this metric's data
        metric_data = df[existing_cols].copy()
        
        # Flatten column names to just years
        metric_data.columns = [col[1] for col in metric_data.columns]
        
        # Add metadata
        for col in metadata_df.columns:
            metric_data[col] = metadata_df[col].values
        
        # Melt
        melted = pd.melt(
            metric_data,
            id_vars=list(metadata_df.columns),
            var_name="Year",
            value_name="Value"
        )
        melted["Metric"] = metric_name
        all_melted.append(melted)
    
    # Concatenate all melted DataFrames
    result = pd.concat(all_melted, ignore_index=True)
    
    return result


def clean_values(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Value column - convert hyphens/blanks to 0, ensure floats.
    
    Args:
        df: Long format DataFrame with Value column
        
    Returns:
        DataFrame with cleaned Value column
    """
    df = df.copy()
    
    # === Region Code Corrections ===
    # CARAGA REGION is incorrectly coded as 'REGION VIII' in source data
    # The correct code is 'REGION XIII' (Caraga)
    caraga_mask = df["Region"].str.upper().str.contains("CARAGA", na=False)
    df.loc[caraga_mask, "Region Code"] = "REGION XIII"
    
    # Convert Value column: replace hyphens, empty strings, and NaN with 0
    df["Value"] = df["Value"].replace(["-", " - ", ""], pd.NA)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Value"] = df["Value"].fillna(0).astype(float)
    
    # Ensure Year is integer
    df["Year"] = df["Year"].astype(int)
    
    # Clean string columns
    for col in ["Region Code", "Region", "School"]:
        df[col] = df[col].astype(str).str.strip()
    
    # Reorder columns to match target schema
    column_order = ["Region Code", "Region", "School", "Year", "Metric", "Value"]
    df = df[column_order]
    
    return df


def export_to_parquet(df: pd.DataFrame, path: Path = PROCESSED_DATA_PATH) -> None:
    """Save DataFrame to Parquet format.
    
    Args:
        df: DataFrame to save
        path: Output path for the Parquet file
    """
    # Ensure output directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use categorical dtype for efficiency
    df = df.copy()
    for col in ["Region Code", "Region", "Metric"]:
        df[col] = df[col].astype("category")
    
    df.to_parquet(path, index=False)
    print(f"Saved {len(df):,} records to {path}")


def load_and_transform(
    input_path: Path = RAW_DATA_PATH,
    output_path: Path = PROCESSED_DATA_PATH
) -> pd.DataFrame:
    """Complete ETL pipeline: load, transform, clean, and save.
    
    Args:
        input_path: Path to raw Excel file
        output_path: Path for processed Parquet output
        
    Returns:
        Cleaned long-format DataFrame
    """
    print(f"Loading data from {input_path}...")
    df = load_raw_data(input_path)
    
    print("Parsing multi-level headers...")
    _, metric_mapping = parse_multiindex_columns(df)
    for metric, years in metric_mapping.items():
        print(f"  Found metric: {metric} ({min(years)}-{max(years)})")
    
    print("Melting to long format...")
    df_long = melt_to_long_format(df)
    
    print("Cleaning values...")
    df_clean = clean_values(df_long)
    
    print("Exporting to Parquet...")
    export_to_parquet(df_clean, output_path)
    
    return df_clean


# === Entry point for testing ===
if __name__ == "__main__":
    df = load_and_transform()
    print("\nSample data:")
    print(df.head(20))
    print(f"\nShape: {df.shape}")
    print(f"\nMetrics: {df['Metric'].unique().tolist()}")
    print(f"Years: {sorted(df['Year'].unique())}")
    print(f"Regions: {df['Region'].nunique()} unique")
    print(f"Schools: {df['School'].nunique()} unique")
