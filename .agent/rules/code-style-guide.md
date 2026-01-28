---
trigger: always_on
---

You are an expert in Python data pipelines, time-series forecasting, and Streamlit dashboard development for research analytics. This project analyzes Philippine HEI research productivity (Publications & Citations).

## Key Principles

- Write concise, technical responses with accurate Python examples.
- Prioritize readability and reproducibility in data pipelines.
- Use functional programming where appropriate; avoid unnecessary classes.
- Prefer vectorized operations over explicit loops for better performance.
- Use descriptive variable names that reflect the data they contain.
- Follow PEP 8 style guidelines for Python code.

## Dependency Management (uv)

- **Always use `uv`** for dependency management, not pip or poetry.
- Add dependencies with `uv add <package>`.
- Run scripts with `uv run python <script.py>` or `uv run streamlit run app.py`.
- The `pyproject.toml` is the single source of truth for dependencies.
- Never manually edit `uv.lock`; it is auto-generated.

## Project Structure

Follow this directory structure strictly:

```text
publication-forecast-project/
├── .venv/                  # Managed by uv
├── data/
│   ├── raw/                # Source Excel file (read-only)
│   └── processed/          # Parquet/CSV exports
├── src/
│   ├── etl.py              # Cleaning & Unpivoting logic
│   ├── forecasting.py      # Statsmodels logic
│   └── viz_utils.py        # Mapbox & Plotly helpers
├── main.py                 # Pipeline orchestrator
├── app.py                  # Streamlit Dashboard
├── pyproject.toml          # Dependency manifest
└── uv.lock                 # Lockfile
```

## Data Analysis and Manipulation

- Use **pandas** for data manipulation and analysis.
- Prefer method chaining for data transformations when possible.
- Use `loc` and `iloc` for explicit data selection.
- Utilize `groupby` operations for efficient data aggregation.
- Use `pd.melt()` for unpivoting wide-format data to long format.

### Excel Multi-Level Header Handling

- Use `pd.read_excel(file, header=[0, 1])` for multi-level headers.
- Flatten MultiIndex columns using tuple unpacking or `droplevel()`.
- Auto-detect year spans from headers; **never hardcode year values**.

### Data Cleaning Rules

- Handle `" - "` (hyphens) or empty cells by converting to `0`.
- Use `pd.to_numeric(errors='coerce')` for safe numeric conversion.
- Validate column names against expected schema after ETL.

### Target Schema (Long Format)

All analysis must use this schema:
- `Region Code` (str)
- `Region` (str)
- `School` (str)
- `Year` (int)
- `Metric` (str) — Values: `"Publication Quantity"`, `"Citation Quantity"`, `"FWCI"`
- `Value` (float)

## Time-Series Forecasting

- Use **statsmodels** for forecasting (Holt's Linear Trend method).
- If historical data has fewer than 3 points, fallback to Simple Moving Average.
- Be aware of period logic:
  - **Pre-Pandemic:** 2015–2019
  - **Pandemic:** 2020–2022 (high volatility)
  - **Post-Pandemic:** 2023–2025 (recovery baseline)
  - **Forecast Horizon:** 2026–2035

```python
from statsmodels.tsa.holtwinters import Holt

def forecast_series(series: pd.Series, periods: int = 10) -> pd.Series:
    """Apply Holt's Linear Trend; fallback to SMA if history < 3."""
    if len(series) < 3:
        return pd.Series([series.mean()] * periods)
    model = Holt(series).fit()
    return model.forecast(periods)
```

## Visualization Standards

- Use **Plotly** for interactive charts and **Mapbox** for geospatial maps.
- Do NOT use matplotlib or seaborn in this project.
- Create reusable plotting functions in `src/viz_utils.py`.
- Philippines map center: `lat=12.8797, lon=121.7740`.
- Style: Clean, academic aesthetic (DepEd style).

```python
import plotly.express as px

def create_choropleth(df: pd.DataFrame, value_col: str, title: str):
    """Create a Philippines choropleth map."""
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations="Region Code",
        color=value_col,
        center={"lat": 12.8797, "lon": 121.7740},
        zoom=5,
        mapbox_style="carto-positron",
        title=title,
    )
    return fig
```

## Streamlit Dashboard Best Practices

- Use `st.cache_data` for expensive data loading operations.
- Use `st.sidebar` for filters (Region, Metric, Year range).
- Organize layouts with `st.columns()` and `st.tabs()`.
- Use `st.plotly_chart(fig, use_container_width=True)` for responsive charts.
- Handle loading states with `st.spinner()`.

```python
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load and cache processed data."""
    return pd.read_parquet(path)
```

## Error Handling and Data Validation

- Implement data quality checks at the beginning of analysis.
- Handle missing data appropriately (convert to 0 per FR-02).
- Use try-except blocks for error-prone operations, especially Excel reading.
- Validate data types and ranges to ensure data integrity.
- Log warnings for unexpected data patterns.

## Performance Optimization

- Use vectorized operations in pandas and numpy for improved performance.
- Utilize efficient data structures (e.g., categorical dtype for Region/Metric).
- Export processed data to Parquet format for faster subsequent loads.
- Profile code to identify and optimize bottlenecks.

## Dependencies

Core dependencies for this project:
- pandas
- numpy
- openpyxl (Excel reading)
- streamlit
- plotly
- statsmodels

## Key Conventions

1. Begin analysis with data exploration and summary statistics.
2. Create reusable functions in the `src/` module for consistency.
3. Document data sources, assumptions, and methodologies clearly.
4. Use git for version control with meaningful commit messages.
5. Store raw data as read-only; write processed outputs to `data/processed/`.

## Running the Project

```bash
# Install dependencies
uv sync

# Run the ETL pipeline
uv run python main.py

# Launch the Streamlit dashboard
uv run streamlit run app.py
```

Refer to the official documentation of pandas, Plotly, Streamlit, and statsmodels for best practices and up-to-date APIs.