# Institutional Research Analytics Platform (IRAP)

**A Python-based forecasting engine for Philippine Higher Education Institutions (HEIs)**

Designed to analyze historical research output (2015–2025) and project future institutional performance through 2035.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Quick Start](#2-quick-start-uv-workflow)
3. [Data Pipeline Architecture](#3-data-pipeline-architecture-the-etl)
4. [Forecasting Methodology](#4-forecasting-methodology)
5. [Dashboard Features](#5-dashboard-features)
6. [Repository Structure](#6-repository-structure)
7. [Technical Specifications](#7-technical-specifications)

---

## 1. Project Overview

### Motivation

Philippine higher education research productivity has undergone significant structural changes, particularly during the COVID-19 pandemic period (2020–2022). Traditional trend analysis methods fail to account for this disruption. IRAP addresses this by implementing a **pandemic-aware forecasting framework** that segments temporal data into meaningful periods and applies appropriate statistical models.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Multi-Index Excel Parsing** | Handles complex merged-header spreadsheets without manual preprocessing |
| **Wide-to-Long Transformation** | Converts institutional reporting format to analysis-ready schema |
| **Adaptive Forecasting** | Dynamically selects between Holt's Linear Trend and SMA based on data density |
| **Period-Based Analysis** | Visualizes data across Pre-Pandemic, During, Post-Pandemic, and Forecast phases |
| **Geospatial Visualization** | Interactive Philippine map with Yearly Slider and Period Evolution animated views |
| **Executive Report** | Jupyter notebook with methodology documentation and stakeholder-ready outputs |
| **Excel Export** | Complete dataset export with period-based worksheets |

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Dependency Management | `uv` | Reproducible Python environments via lockfile |
| Data Processing | `pandas` + `openpyxl` | DataFrame operations and Excel I/O |
| Forecasting Engine | `statsmodels` | Holt's Exponential Smoothing implementation |
| Visualization | `plotly` + `kaleido` | Interactive charts and static image export |
| Dashboard | `streamlit` | Web-based analytical interface |
| Reporting | `jupyter` + `nbformat` | Executive report notebooks |

---

## 2. Quick Start (uv Workflow)

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation & Execution

```bash
# Clone and Initialize
git clone <repository_url>
cd publication-forecast-project
uv sync                           # Install dependencies from uv.lock

# Run the Pipeline
uv run python src/etl.py          # Step 1: Process Excel → Parquet
uv run python src/forecasting.py  # Step 2: Generate 10-year forecasts

# Launch Dashboard
uv run streamlit run app.py       # Accessible at http://localhost:8501
```

### Alternative: Full Pipeline Execution

```bash
uv run python main.py             # Runs ETL + Forecasting sequentially
```

### Complete Reproduction Guide

To fully reproduce all outputs from scratch:

```bash
# 1. Clone and set up environment
git clone <repository_url>
cd publication-forecast-project
uv sync

# 2. Run the complete data pipeline
uv run python main.py              # ETL + Forecasting → data/processed/

# 3. Launch the interactive dashboard
uv run streamlit run app.py        # Opens at http://localhost:8501

# 4. Generate the Executive Report notebook
uv run jupyter lab reports/HEI_Executive_Report.ipynb
# Then: Run All Cells (Ctrl+Shift+Enter)

# 5. Export to Excel (via dashboard)
# Navigate to Dashboard → Click "📥 Download Excel Report"
```

**Expected Outputs:**

| Output | Location | Description |
|--------|----------|-------------|
| Clean Data | `data/processed/clean.parquet` | Transformed long-format data |
| Forecast Data | `data/processed/forecasts.parquet` | 10-year projections (2026–2035) |
| Excel Report | Downloaded via dashboard | Complete multi-sheet workbook |
| Executive Report | `reports/HEI_Executive_Report.ipynb` | Methodology + visualizations |

---


## 3. Data Pipeline Architecture (The ETL)

### The "Wide Format" Problem

The source dataset (`MASTER DATASET PRODUCTIVITY.xlsx`) employs a **multi-index header structure** common in institutional reporting:

```
┌──────────────┬─────────────────────────────────┬─────────────────────────────────┐
│              │      Publication Quantity       │       Citation Quantity         │
│    SCHOOL    ├──────┬──────┬──────┬───────────┼──────┬──────┬──────┬───────────┤
│              │ 2015 │ 2016 │ ...  │   2025    │ 2015 │ 2016 │ ...  │   2025    │
├──────────────┼──────┼──────┼──────┼───────────┼──────┼──────┼──────┼───────────┤
│ University A │  12  │  15  │ ...  │    45     │  89  │ 102  │ ...  │   312     │
└──────────────┴──────┴──────┴──────┴───────────┴──────┴──────┴──────┴───────────┘
```

### Transformation Strategy

The ETL module (`src/etl.py`) implements a **Wide-to-Long melt operation**:

```
INPUT (Wide):                              OUTPUT (Long):
┌────────┬──────┬──────┐                   ┌────────┬──────┬────────┬───────┐
│ School │ 2015 │ 2016 │       ──────►     │ School │ Year │ Metric │ Value │
├────────┼──────┼──────┤                   ├────────┼──────┼────────┼───────┤
│ Univ A │  12  │  15  │                   │ Univ A │ 2015 │ Pub Q  │  12   │
└────────┴──────┴──────┘                   │ Univ A │ 2016 │ Pub Q  │  15   │
                                           └────────┴──────┴────────┴───────┘
```

### Data Cleaning Rules

| Raw Value | Transformation | Rationale |
|-----------|----------------|-----------|
| `" - "` (hyphen) | → `0.0` | Missing data indicator in source |
| `""` (empty) | → `0.0` | Null coercion |
| `NaN` | → `0.0` | Consistent numeric handling |

### Output Schema

**File:** `data/processed/clean_metrics.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `Region Code` | `str` | Philippine region identifier (e.g., "NCR", "REGION V") |
| `Region` | `str` | Full region name |
| `School` | `str` | Institution name |
| `Year` | `int` | Academic year (2015–2025) |
| `Metric` | `str` | One of: "Publication Quantity", "Citation Quantity", "Field-Weighted Citation Impact" |
| `Value` | `float` | Observed metric value |

### Dataset Dimensions

| Dimension | Count |
|-----------|-------|
| Total Records | 1,716 |
| Unique Schools | 52 |
| Regions | 17 |
| Years | 11 (2015–2025) |
| Metrics | 3 |

---

## 4. Forecasting Methodology

### Temporal Segmentation Framework

To account for the structural break introduced by the COVID-19 pandemic, the forecasting engine segments historical data into **five distinct periods** per client requirements:

| Period | Years | Characterization | Treatment |
|--------|-------|------------------|-----------|
| **Pre-Pandemic** | 2015–2019 | Established baseline trends | Primary trend signal |
| **During Pandemic** | 2020–2022 | High volatility / Disruption | Acknowledged as outlier zone |
| **Post-Pandemic** | 2023–2025 | "New Normal" recovery | Recent baseline for projection |
| **Forecast Phase 1** | 2026–2030 | Short-term projection | 5-year forward estimate |
| **Forecast Phase 2** | 2031–2035 | Long-term projection | Extended 5-year estimate |

> **Note:** The current implementation uses the full 2015–2025 series for model fitting. Future iterations may implement weighted schemes to downweight pandemic-era observations.

### Algorithm Selection Logic

The forecasting engine (`src/forecasting.py`) dynamically selects the appropriate model based on data density:

```
┌─────────────────────────────────────────────────────────────┐
│                    For each (School, Metric):               │
├─────────────────────────────────────────────────────────────┤
│  Count non-zero observations in training period (2015–2025) │
│                              │                              │
│              ┌───────────────┴───────────────┐              │
│              ▼                               ▼              │
│    n ≥ 3 non-zero points          n < 3 non-zero points    │
│              │                               │              │
│              ▼                               ▼              │
│   ┌─────────────────────┐       ┌─────────────────────┐    │
│   │ Holt's Linear Trend │       │ Simple Moving Avg   │    │
│   │ (Captures momentum) │       │ (Conservative est.) │    │
│   └─────────────────────┘       └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Holt's Linear Trend Method

For institutions with sufficient historical data, we apply **Holt's Exponential Smoothing** (double exponential smoothing), which decomposes the time series into level and trend components:

**Level Equation:**
$$L_t = \alpha Y_t + (1 - \alpha)(L_{t-1} + T_{t-1})$$

**Trend Equation:**
$$T_t = \beta(L_t - L_{t-1}) + (1 - \beta)T_{t-1}$$

**Forecast Equation:**
$$\hat{Y}_{t+h} = L_t + h \cdot T_t$$

Where:
- $L_t$ = Level at time $t$
- $T_t$ = Trend at time $t$
- $\alpha, \beta$ = Smoothing parameters (optimized via MLE)
- $h$ = Forecast horizon

**Implementation:** `statsmodels.tsa.holtwinters.Holt`

### Simple Moving Average (Fallback)

For institutions with sparse data (< 3 non-zero observations), Holt's method risks overfitting or producing unstable forecasts. We apply a **3-period Simple Moving Average**:

$$\hat{Y}_{t+h} = \frac{1}{3}\sum_{i=t-2}^{t} Y_i$$

This produces a conservative, flat projection that avoids explosive or negative forecasts.

### Post-Processing Constraints

| Constraint | Implementation | Rationale |
|------------|----------------|-----------|
| Non-negativity | `max(0, forecast)` | Publication and citation counts cannot be negative |
| Discrete rounding | `round()` for count metrics | Publications and Citations are whole numbers |
| Continuous FWCI | No rounding | Field-Weighted Citation Impact is a calculated ratio |
| Forecast Tagging | `Type = "Forecast"` | Distinguishes projected values from historical observations |

### Metric-Specific Rounding

| Metric | Rounding | Example |
|--------|----------|---------|
| Publication Quantity | Nearest integer | 45.7 → 46 |
| Citation Quantity | Nearest integer | 312.3 → 312 |
| Field-Weighted Citation Impact | No rounding (continuous) | 1.234 → 1.234 |

### Output Schema

**File:** `data/processed/forecasts.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `Region Code` | `str` | Philippine region identifier |
| `Region` | `str` | Full region name |
| `School` | `str` | Institution name |
| `Year` | `int` | Year (2015–2035) |
| `Metric` | `str` | Metric type |
| `Value` | `float` | Observed or forecasted value |
| `Type` | `str` | Either "History" or "Forecast" |

---

## 5. Dashboard Features

The Streamlit dashboard (`app.py`) provides an interactive interface for exploring research productivity data.

### Filter Controls (Sidebar)

| Filter | Options | Description |
|--------|---------|-------------|
| **Metric** | All Metrics, Publication Quantity, Citation Quantity, FWCI | Select which metric to visualize |
| **Region** | All Regions + 17 individual regions | Filter by Philippine administrative region |
| **Schools** | Aggregated view or multi-select (up to 6) | Compare specific schools or view national totals |
| **Period** | All Periods + 5 defined periods | Filter to specific time periods |

### Analysis Tabs

#### 📈 Time Series Analysis
- Interactive line charts with historical and forecast data
- Period shading (Pre-Pandemic, During, Post-Pandemic, Forecast phases)
- Comparison of multiple schools or aggregated national view
- Dashed lines indicate forecasted values

#### 🗺️ Geospatial Analysis

**View Mode Toggle:**
| Mode | Description |
|------|-------------|
| **Yearly Slider** | View single-year regional distribution with slider navigation (2015–2035) |
| **Period Evolution** | Animated bubble map showing evolution across all 5 strategic periods |

**Period Evolution Features:**
- Animated transitions through Pre-Pandemic → During → Post → Forecast Phase 1 → Forecast Phase 2
- Play/Pause controls and period slider
- Fixed color scale for consistent interpretation across periods
- Uses average annual values (not totals) for fair comparison between periods of different lengths

#### 📊 Period Comparison
- Bar chart comparing totals across all 5 periods
- Summary table with Total, Average per Year, and Year range
- Quick visual comparison of Pre vs During vs Post-pandemic trends

### Excel Export

The dashboard includes a **Download Excel Report** button that generates a comprehensive workbook with:

| Sheet Name | Contents |
|------------|----------|
| Complete Data | Full dataset (2015–2035, all metrics) |
| Historical (2015-2025) | Only observed data (long format) |
| Forecast (2026-2035) | Only projected data (long format) |
| **Historical Figures** | Wide format: `Publication 2015`, `CIT 2015`, `FWCI 2015`, ... |
| **Forecasted Figures** | Wide format: `Publication 2026`, `CIT 2026`, `FWCI 2026`, ... |
| Pre-Pandemic (2015-2019) | Period-specific slice |
| During Pandemic (2020-2022) | Period-specific slice |
| Post-Pandemic (2023-2025) | Period-specific slice |
| Forecast Phase 1 (2026-2030) | First 5-year forecast |
| Forecast Phase 2 (2031-2035) | Second 5-year forecast |
| Summary by Region | Aggregated statistics |

### Executive Report Notebook

A standalone Jupyter notebook (`reports/HEI_Executive_Report.ipynb`) provides a stakeholder-ready document with:

| Section | Content |
|---------|----------|
| Abstract | Strategic overview of the analysis |
| Methodology | Pandemic structural break rationale + Holt's equation |
| National Overview | Period summary tables with styling |
| Geospatial Analysis | Animated regional evolution maps |
| Strategic Outlook | 2026–2035 projection summary |
| Excel Export | Generates `HEI_Research_Report_Data.xlsx` |

**Running the Report:**
```bash
cd reports
uv run jupyter notebook HEI_Executive_Report.ipynb
```

---

## 6. Repository Structure

```
publication-forecast-project/
│
├── data/
│   ├── raw/
│   │   ├── MASTER DATASET PRODUCTIVITY.xlsx   # Source data (read-only)
│   │   └── Sample Visual.jpg                  # Reference visualization
│   └── processed/
│       ├── clean_metrics.parquet              # ETL output
│       └── forecasts.parquet                  # Final dataset with projections
│
├── reports/
│   ├── HEI_Executive_Report.ipynb            # Stakeholder-ready Jupyter report
│   └── HEI_Research_Report_Data.xlsx         # Generated Excel export (after running notebook)
│
├── src/
│   ├── etl.py              # Excel parsing with multi-header support
│   │                       # Functions: load_raw_data(), melt_to_long_format()
│   │
│   ├── forecasting.py      # Statsmodels-based forecasting engine
│   │                       # Functions: holts_linear_trend(), forecast_series()
│   │                       # Includes discrete rounding for count metrics
│   │
│   └── viz_utils.py        # Geographic utilities and Plotly helpers
│                           # Contains: REGION_COORDINATES, plot_philippine_map(),
│                           # plot_period_geospatial_comparison(), assign_period()
│
├── app.py                  # Streamlit dashboard entry point
│                           # Features: ALL filters, period comparison, geospatial map, Excel export
│
├── main.py                 # Pipeline orchestrator
│                           # Executes: ETL → Forecasting in sequence
│
├── pyproject.toml          # Dependency manifest (managed by uv)
├── uv.lock                 # Reproducible dependency lockfile
├── prd.md                  # Product requirements document
└── README.md               # This documentation
```

### Module Responsibilities

| Module | Primary Responsibility | Key Exports |
|--------|------------------------|-------------|
| `src/etl.py` | Data ingestion and transformation | `load_and_transform()` |
| `src/forecasting.py` | Time-series model application | `run_forecasting_pipeline()`, `DISCRETE_METRICS` |
| `src/viz_utils.py` | Philippine geographic constants and maps | `REGION_COORDINATES`, `plot_philippine_map()`, `plot_period_geospatial_comparison()`, `assign_period()` |
| `app.py` | User interface, visualization, and export | Streamlit application |
| `main.py` | Pipeline orchestration | CLI entry point |
| `reports/HEI_Executive_Report.ipynb` | Stakeholder documentation | Executable report with Excel export |

---

## 7. Technical Specifications

### System Requirements

| Requirement | Specification |
|-------------|---------------|
| Python Version | 3.12+ |
| Package Manager | uv (recommended) |
| Memory | ≥ 4GB RAM |
| Storage | ≥ 100MB for processed data |

### Performance Characteristics

| Operation | Approximate Duration | Output Size |
|-----------|---------------------|-------------|
| ETL Pipeline | ~3 seconds | 10 KB (Parquet) |
| Forecasting | ~5 seconds | 25 KB (Parquet) |
| Dashboard Launch | ~2 seconds | N/A |
| Excel Export | ~1 second | ~500 KB |

### Forecast Accuracy Considerations

> **Disclaimer:** The forecasts generated by IRAP are statistical projections based on historical trends. They do not account for:
> - Policy changes in research funding
> - Institutional strategic initiatives
> - External economic factors
> - Changes in publication venue standards
>
> Users should treat forecasts as **indicative scenarios** rather than definitive predictions.

---

## License

MIT License

---

## Citation

If using IRAP for academic research, please cite:

```
Institutional Research Analytics Platform (IRAP). (2026).
Philippine HEI Research Productivity Forecasting System.
https://github.com/<repository>
```

---

<div align="center">
<sub>Developed for Philippine Higher Education Research Analytics</sub>
</div>
