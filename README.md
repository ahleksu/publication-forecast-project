# 🎓 Philippine HEI Research Productivity Forecast

A Python-based forecasting pipeline and interactive Streamlit dashboard for analyzing research productivity (Publications & Citations) across Philippine Higher Education Institutions (HEIs).

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.53+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Data Pipeline](#-data-pipeline)
- [Forecasting Methodology](#-forecasting-methodology)
- [Dashboard](#-dashboard)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

---

## 🔍 Overview

This project analyzes research output data from 52 Philippine HEIs across 17 regions, spanning from 2015 to 2025, with automated forecasting through 2035. The system handles complex multi-level Excel headers, transforms wide-format data to analysis-ready long format, and applies time-series forecasting models.

### Key Metrics Tracked

| Metric | Description |
|--------|-------------|
| **Publication Quantity** | Number of research publications per institution per year |
| **Citation Quantity** | Total citations received by publications |
| **Field-Weighted Citation Impact (FWCI)** | Normalized citation impact relative to field average |

### Period Logic

```
Pre-Pandemic:  2015-2019 (baseline historical)
Pandemic:      2020-2022 (high volatility zone)
Post-Pandemic: 2023-2025 (recovery baseline)
Forecast:      2026-2035 (10-year projection)
```

---

## ✨ Features

- **Smart Excel Parsing** — Automatically handles merged multi-level headers
- **Wide-to-Long ETL** — Transforms complex spreadsheet structure to analysis-ready format
- **Dual-Model Forecasting** — Holt's Linear Trend with SMA fallback for sparse data
- **Interactive Dashboard** — Premium dark-themed Streamlit UI with:
  - Region and school filtering
  - Multi-school comparison charts
  - Historical vs forecast visualization
  - Detailed pivot tables

---

## 📁 Project Structure

```
publication-forecast-project/
├── .venv/                          # Virtual environment (managed by uv)
├── data/
│   ├── raw/
│   │   └── MASTER DATASET PRODUCTIVITY.xlsx   # Source data (read-only)
│   └── processed/
│       ├── clean_metrics.parquet   # ETL output (long format)
│       └── forecasts.parquet       # Historical + forecast data
├── src/
│   ├── etl.py                      # Data extraction & transformation
│   └── forecasting.py              # Time-series forecasting engine
├── app.py                          # Streamlit dashboard
├── main.py                         # Pipeline orchestrator
├── pyproject.toml                  # Dependency manifest (uv)
├── uv.lock                         # Lockfile (auto-generated)
├── prd.md                          # Product requirements document
└── README.md                       # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd publication-forecast-project

# Install dependencies (creates .venv automatically)
uv sync

# Verify installation
uv run python --version
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation and analysis |
| `openpyxl` | Excel file reading (required for .xlsx) |
| `plotly` | Interactive visualizations |
| `streamlit` | Web dashboard framework |
| `statsmodels` | Time-series forecasting (Holt's method) |
| `scikit-learn` | Machine learning utilities |

---

## 💻 Usage

### Quick Start

```bash
# Run the complete pipeline (ETL + Forecasting)
uv run python main.py

# Launch the interactive dashboard
uv run streamlit run app.py
```

### Individual Components

```bash
# Run only the ETL pipeline
uv run python src/etl.py

# Run only the forecasting engine
uv run python src/forecasting.py
```

---

## 🔄 Data Pipeline

### Input Data Structure

The source Excel file uses **merged multi-level headers**:

```
Row 1: |          | Publication Quantity      | Citation Quantity         |
Row 2: | SCHOOL   | 2015 | 2016 | ... | 2025 | 2015 | 2016 | ... | 2025 |
```

### ETL Process (`src/etl.py`)

```mermaid
flowchart LR
    A[Excel File] -->|pd.read_excel\nheader=[0,1]| B[MultiIndex DataFrame]
    B -->|parse_multiindex_columns| C[Identify Metrics & Years]
    C -->|melt_to_long_format| D[Long Format]
    D -->|clean_values| E[Final Schema]
    E -->|to_parquet| F[clean_metrics.parquet]
```

### Output Schema

| Column | Type | Example |
|--------|------|---------|
| `Region Code` | str | "NCR" |
| `Region` | str | "NATIONAL CAPITAL REGION" |
| `School` | str | "University of the Philippines Diliman" |
| `Year` | int | 2023 |
| `Metric` | str | "Publication Quantity" |
| `Value` | float | 245.0 |

### Data Statistics

- **Records**: 1,716 historical observations
- **Schools**: 52 unique institutions
- **Regions**: 17 Philippine regions
- **Years**: 2015-2025 (11 years)
- **Metrics**: 3 (Publication Qty, Citation Qty, FWCI)

---

## 📈 Forecasting Methodology

### Model Selection (`src/forecasting.py`)

The system dynamically selects the appropriate forecasting method based on data availability:

```python
if non_zero_data_points < 3:
    method = "Simple Moving Average (SMA)"
else:
    method = "Holt's Linear Trend"
```

### Holt's Linear Trend

Used when sufficient historical data exists. Captures both level and trend components:

```
Level:    L_t = α * Y_t + (1 - α) * (L_{t-1} + T_{t-1})
Trend:    T_t = β * (L_t - L_{t-1}) + (1 - β) * T_{t-1}
Forecast: F_{t+h} = L_t + h * T_t
```

### Simple Moving Average (Fallback)

Used for schools with sparse data (< 3 non-zero observations):

```
Forecast = mean(last 3 years of data)
```

### Output

Forecasts are appended to historical data with a `Type` column:

| Type | Description |
|------|-------------|
| `History` | Actual observed values (2015-2025) |
| `Forecast` | Predicted values (2026-2035) |

---

## 🖥️ Dashboard

### Features

| Component | Description |
|-----------|-------------|
| **Metric Selector** | Choose between Publication Qty, Citation Qty, or FWCI |
| **Region Filter** | Filter schools by Philippine region |
| **School Comparison** | Multi-select up to 6 schools for comparison |
| **Time Series Chart** | Interactive Plotly chart with history/forecast distinction |
| **Data Tables** | Tabbed view of historical and forecast data |

### Visual Design

- **Theme**: Premium dark mode with gradient styling
- **Colors**: Accent color `#4ECDC4` (teal), Background `#0E1117`
- **Charts**: 
  - Solid lines for historical data
  - Dashed lines for forecasts
  - Vertical marker at forecast boundary (2025.5)

### Accessing the Dashboard

```bash
uv run streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

---

## 📚 API Reference

### ETL Module (`src/etl.py`)

```python
# Main pipeline function
load_and_transform(
    input_path: Path = "data/raw/MASTER DATASET PRODUCTIVITY.xlsx",
    output_path: Path = "data/processed/clean_metrics.parquet"
) -> pd.DataFrame

# Individual functions
load_raw_data(path: Path) -> pd.DataFrame
parse_multiindex_columns(df: pd.DataFrame) -> tuple[list, dict]
melt_to_long_format(df: pd.DataFrame) -> pd.DataFrame
clean_values(df: pd.DataFrame) -> pd.DataFrame
export_to_parquet(df: pd.DataFrame, path: Path) -> None
```

### Forecasting Module (`src/forecasting.py`)

```python
# Main pipeline function
run_forecasting_pipeline(
    input_path: Path = "data/processed/clean_metrics.parquet",
    output_path: Path = "data/processed/forecasts.parquet"
) -> pd.DataFrame

# Forecasting functions
forecast_series(series: pd.Series, periods: int = 10) -> pd.Series
holts_linear_trend(series: pd.Series, periods: int) -> pd.Series
simple_moving_average(series: pd.Series, periods: int) -> pd.Series
```

### Dashboard (`app.py`)

```python
@st.cache_data
load_forecasts(path: Path) -> pd.DataFrame

create_time_series_chart(
    df: pd.DataFrame,
    schools: list[str],
    metric: str,
    title: str = None
) -> go.Figure
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Commands

```bash
# Sync dependencies after changes to pyproject.toml
uv sync

# Add a new dependency
uv add <package-name>

# Run with verbose output
uv run python -v main.py
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 📧 Contact

For questions or support, please open an issue in the repository.

---

<div align="center">
  <sub>Built with ❤️ for Philippine Higher Education Research Analytics</sub>
</div>
