## 1. PROJECT OVERVIEW
Develop a Python-based forecasting pipeline and Streamlit dashboard to analyze research productivity (Publications & Citations) for Philippine HEIs.
**Key Constraint:** The system must use `uv` for dependency management and handle complex multi-level Excel headers.

## 2. DATA SPECIFICATIONS (CRITICAL)
### 2.1 Input Structure (The "Wide" Problem)
The input Excel file is structured with **multi-level headers**:
* **Row 1:** Metric groupings (e.g., "Publication Quantity" spanning cols D-N, "Citation Quantity" spanning cols O-Y).
* **Row 2:** Year labels (2015, 2016... 2025) nested under each Metric.
* **Columns A-C:** Metadata (`REGION CODE`, `REGION`, `SCHOOL`).

### 2.2 ETL Requirements
The pipeline must **Unpivot (Melt)** this structure into a "Long Format" DataFrame with the following schema for analysis:
* `Region Code` (str)
* `Region` (str)
* `School` (str)
* `Year` (int)
* `Metric` (str) - Values: "Publication Quantity", "Citation Quantity", "FWCI"
* `Value` (float)

### 2.3 Period Logic (Pandemic Awareness)
* **Pre-Pandemic:** 2015–2019
* **Pandemic:** 2020–2022 (High volatility zone)
* **Post-Pandemic:** 2023–2025 (Recovery baseline)
* **Forecast:** 2026–2035

## 3. TECHNICAL ARCHITECTURE (uv Based)
### 3.1 Directory Structure
```text
publication-forecast-project/
├── .venv/                  # Managed by uv
├── data/
│   ├── raw/                # Source Excel file
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

### 3.2 Visualization Standards

* **Geospatial:** Choropleth or Bubble Map focusing on the Philippines (Lat 12.8797, Long 121.7740).
* **Style:** Clean, academic aesthetic similar to the provided "Sample Visual" (DepEd style maps).

## 4. FUNCTIONAL REQUIREMENTS

* **FR-01 (Smart Ingest):** Automatically detect the span of years in the Excel header. Do not hardcode "2025" if the data extends further or stops shorter.
* **FR-02 (Cleaning):** Handle " - " (hyphens) or empty cells as `0`.
* **FR-03 (Forecasting):** Apply Holt’s Linear Trend. If history < 3 points, use Simple Moving Average.
* **FR-04 (Dashboard):** Allow filtering by Region to see specific School performance curves.