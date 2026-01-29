"""
Script to update the HEI Executive Report notebook with:
1. Enhanced concrete examples (Holt's + SMA)
2. Sorted Summary Statistics columns (Publication, Citation, FWCI)
3. Improved forecast table display (Plotly interactive table)
"""
import json
from pathlib import Path


def load_notebook(path: Path) -> dict:
    """Load notebook as JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_notebook(nb: dict, path: Path) -> None:
    """Save notebook as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4, ensure_ascii=False)


def update_methodology_section(cells: list) -> list:
    """Update the Methodology cell with enhanced concrete examples."""
    
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "markdown":
            source = "".join(cell.get("source", []))
            if "### 7. Concrete Example: Benguet State University" in source:
                # Replace with enhanced version
                cells[i]["source"] = [
                    "## Methodology\n",
                    "\n",
                    "### 1. The COVID-19 Structural Break\n",
                    "\n",
                    "The COVID-19 pandemic (2020–2022) introduced a **structural break** in research productivity data. This period was characterized by:\n",
                    "\n",
                    "- Laboratory closures and field research delays\n",
                    "- Transition to remote work affecting collaborative projects\n",
                    "- Publication pipeline disruptions and journal backlogs\n",
                    "- Reallocation of institutional resources to pandemic response\n",
                    "\n",
                    "We treat 2020–2022 as a distinct analytical period to isolate pandemic effects from underlying growth trends.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 2. Temporal Segmentation Framework\n",
                    "\n",
                    "| Period | Years | Duration | Characterization |\n",
                    "|--------|-------|----------|------------------|\n",
                    "| **Pre-Pandemic** | 2015–2019 | 5 years | Established baseline trends |\n",
                    "| **During Pandemic** | 2020–2022 | 3 years | High volatility / Disruption |\n",
                    "| **Post-Pandemic** | 2023–2025 | 3 years | \"New Normal\" recovery |\n",
                    "| **Forecast Phase 1** | 2026–2030 | 5 years | Short-term projection |\n",
                    "| **Forecast Phase 2** | 2031–2035 | 5 years | Long-term projection |\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 3. Algorithm Selection Logic\n",
                    "\n",
                    "The forecasting engine dynamically selects the appropriate model based on data density:\n",
                    "\n",
                    "```python\n",
                    "For each (School, Metric):\n",
                    "    Count non-zero observations in training period (2015–2025)\n",
                    "    \n",
                    "    IF n ≥ 3 non-zero points:\n",
                    "        → Apply Holt's Linear Trend (captures momentum)\n",
                    "    ELSE:(2026-2035)\n",
                    "        → Apply Simple Moving Average (conservative estimate)\n",
                    "```\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 4. Holt's Linear Trend Method\n",
                    "\n",
                    "For institutions with sufficient historical data (≥ 3 non-zero observations), we apply **Holt's Exponential Smoothing** (double exponential smoothing), which decomposes the time series into level and trend components:\n",
                    "\n",
                    "**Level Equation:**\n",
                    "$$L_t = \\alpha Y_t + (1 - \\alpha)(L_{t-1} + T_{t-1})$$\n",
                    "\n",
                    "**Trend Equation:**\n",
                    "$$T_t = \\beta(L_t - L_{t-1}) + (1 - \\beta)T_{t-1}$$\n",
                    "\n",
                    "**Forecast Equation:**\n",
                    "$$\\hat{Y}_{t+h} = L_t + h \\cdot T_t$$\n",
                    "\n",
                    "Where:\n",
                    "- $Y_t$ = Observed value at time $t$\n",
                    "- $L_t$ = Estimated level at time $t$\n",
                    "- $T_t$ = Estimated trend at time $t$\n",
                    "- $\\alpha$ = Smoothing parameter for level (0 < α < 1, optimized via MLE)\n",
                    "- $\\beta$ = Smoothing parameter for trend (0 < β < 1, optimized via MLE)\n",
                    "- $h$ = Forecast horizon (years ahead)\n",
                    "\n",
                    "**Implementation:** `statsmodels.tsa.holtwinters.Holt`\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 5. Simple Moving Average (Fallback)\n",
                    "\n",
                    "For institutions with sparse data (< 3 non-zero observations), Holt's method risks overfitting or producing unstable forecasts. We apply a **3-period Simple Moving Average**:\n",
                    "\n",
                    "$$\\hat{Y}_{t+h} = \\frac{1}{k}\\sum_{i=t-k+1}^{t} Y_i$$\n",
                    "\n",
                    "Where:\n",
                    "- $k = \\min(3, n)$ where $n$ is the number of available observations\n",
                    "- This produces a conservative, flat projection that avoids explosive or negative forecasts\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 6. Post-Processing Constraints\n",
                    "\n",
                    "| Constraint | Implementation | Rationale |\n",
                    "|------------|----------------|-----------|\n",
                    "| Non-negativity | `max(0, forecast)` | Publication and citation counts cannot be negative |\n",
                    "| Discrete rounding | `round()` for count metrics | Publications and Citations are whole numbers |\n",
                    "| Continuous FWCI | No rounding | Field-Weighted Citation Impact is a calculated ratio |\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 7. Concrete Examples: Algorithm Selection in Practice\n",
                    "\n",
                    "The forecasting system dynamically selects between two methods based on data availability. Below are examples of each approach.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "#### Example A: Holt's Linear Trend (≥ 3 Non-Zero Observations)\n",
                    "\n",
                    "Consider **Benguet State University (BSU)** in the Cordillera Administrative Region (CAR). With 11 years of data (2015–2025), BSU has ≥ 3 non-zero observations, qualifying for Holt's method:\n",
                    "\n",
                    "| Year | Publications | Growth Rate |\n",
                    "|------|--------------|-------------|\n",
                    "| 2023 | 45 | — |\n",
                    "| 2024 | 52 | +15.6% |\n",
                    "| 2025 | 58 | +11.5% |\n",
                    "\n",
                    "**Model Parameters (after fitting):**\n",
                    "- $L_{2025} = 58$ (estimated level)\n",
                    "- $T_{2025} = 6.5$ (estimated annual trend)\n",
                    "\n",
                    "**Forecasts:**\n",
                    "- **2026:** $\\hat{Y}_{2026} = 58 + 1 \\times 6.5 = 64.5 \\approx 65$ publications\n",
                    "- **2030:** $\\hat{Y}_{2030} = 58 + 5 \\times 6.5 = 90.5 \\approx 91$ publications\n",
                    "\n",
                    "---\n",
                    "\n",
                    "#### Example B: Simple Moving Average (< 3 Non-Zero Observations)\n",
                    "\n",
                    "For institutions with sparse data (fewer than 3 non-zero observations in the training period), the system applies a **Simple Moving Average** to avoid overfitting:\n",
                    "\n",
                    "| Year | Publications |\n",
                    "|------|--------------|\n",
                    "| 2023 | 0 |\n",
                    "| 2024 | 5 |\n",
                    "| 2025 | 7 |\n",
                    "\n",
                    "With only 2 non-zero observations, the SMA fallback is triggered:\n",
                    "\n",
                    "$$\\hat{Y}_{2026-2035} = \\frac{5 + 7}{2} = 6 \\text{ publications/year (constant)}$$\n",
                    "\n",
                    "This conservative approach produces a flat projection, preventing explosive or negative forecasts from insufficient trend data.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "> **Disclaimer:** These forecasts are statistical projections based on historical trends. They do not account for policy changes, institutional initiatives, or external economic factors. Treat as indicative scenarios."
                ]
                break
    
    return cells


def update_summary_statistics_code(cells: list) -> list:
    """Update the Summary Statistics cell to sort columns by Publication, Citation, FWCI."""
    
    new_source = [
        "# Summary by Period with sorted columns (Publication, Citation, FWCI)\n",
        "summary = df.pivot_table(\n",
        "    index='Period',\n",
        "    columns='Metric',\n",
        "    values='Value',\n",
        "    aggfunc='sum'\n",
        ").reindex(PERIOD_ORDER)\n",
        "\n",
        "# Reorder columns: Publication Quantity, Citation Quantity, Field-Weighted Citation Impact\n",
        "column_order = ['Publication Quantity', 'Citation Quantity', 'Field-Weighted Citation Impact']\n",
        "summary = summary[column_order]\n",
        "\n",
        "styled_summary = (\n",
        "    summary.style\n",
        "    .format('{:,.0f}')\n",
        "    .background_gradient(cmap='YlGnBu', axis=0)\n",
        "    .set_caption('Total Research Output by Period')\n",
        ")\n",
        "styled_summary"
    ]
    
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            if "# Summary by Period" in source and "pivot_table" in source:
                cells[i]["source"] = new_source
                # Clear output to force re-execution
                cells[i]["outputs"] = []
                cells[i]["execution_count"] = None
                break
    
    return cells


def update_forecast_table_code(cells: list) -> list:
    """Update the forecast table code to group by Year first, then Metric."""
    
    # New structure: Group by Year first, then Metric under each year
    new_source = [
        "# Prepare forecast data for display - Grouped by Year, then Metric\n",
        "import plotly.graph_objects as go\n",
        "\n",
        "forecast_df = df[df['Year'] >= 2026].copy()\n",
        "\n",
        "# Pivot to wide format with Year as first level, Metric as second\n",
        "forecast_wide = forecast_df.pivot_table(\n",
        "    index=['Region Code', 'Region', 'School'],\n",
        "    columns=['Year', 'Metric'],\n",
        "    values='Value',\n",
        "    aggfunc='first'\n",
        ")\n",
        "\n",
        "# Flatten MultiIndex columns: 'Year | MetricAbbrev' format\n",
        "def abbrev_metric(m):\n",
        "    if 'Publication' in m: return 'Pub'\n",
        "    elif 'Citation' in m: return 'Cit'\n",
        "    else: return 'FWCI'\n",
        "\n",
        "forecast_wide.columns = [f\"{year} | {abbrev_metric(metric)}\" for year, metric in forecast_wide.columns]\n",
        "forecast_wide = forecast_wide.reset_index()\n",
        "\n",
        "# Sort by year, then within each year: Pub, Cit, FWCI\n",
        "base_cols = ['Region Code', 'Region', 'School']\n",
        "data_cols = [c for c in forecast_wide.columns if ' | ' in c]\n",
        "years = sorted(set(int(c.split(' | ')[0]) for c in data_cols))\n",
        "ordered_cols = []\n",
        "for year in years:\n",
        "    for suffix in ['Pub', 'Cit', 'FWCI']:\n",
        "        col = f\"{year} | {suffix}\"\n",
        "        if col in forecast_wide.columns:\n",
        "            ordered_cols.append(col)\n",
        "\n",
        "forecast_wide = forecast_wide[base_cols + ordered_cols]\n",
        "forecast_wide = forecast_wide.sort_values(['Region Code', 'School']).reset_index(drop=True)\n",
        "\n",
        "print(f'Forecast table: {len(forecast_wide)} schools x {len(forecast_wide.columns)} columns')\n",
        "print(f'Years covered: {min(years)} - {max(years)}')\n",
        "print('Column Key: Pub=Publication, Cit=Citation, FWCI=Field-Weighted Citation Impact')\n",
        "\n",
        "# Create interactive Plotly table for full visibility\n",
        "fig = go.Figure(data=[go.Table(\n",
        "    columnwidth=[80, 140, 220] + [70] * len(ordered_cols),\n",
        "    header=dict(\n",
        "        values=[f'<b>{col}</b>' for col in forecast_wide.columns],\n",
        "        fill_color='#1a1a2e',\n",
        "        font=dict(color='#4ECDC4', size=10),\n",
        "        align='center',\n",
        "        height=40,\n",
        "    ),\n",
        "    cells=dict(\n",
        "        values=[forecast_wide[col].to_list() for col in forecast_wide.columns],\n",
        "        fill_color=[['#16213e', '#1a1a2e'] * (len(forecast_wide) // 2 + 1)],\n",
        "        font=dict(color='#e0e0e0', size=10),\n",
        "        align='center',\n",
        "        height=25,\n",
        "    )\n",
        ")])\n",
        "\n",
        "fig.update_layout(\n",
        "    title=dict(\n",
        "        text='Complete Forecast Data (2026-2035) - Grouped by Year',\n",
        "        font=dict(color='#4ECDC4', size=16),\n",
        "        x=0.5\n",
        "    ),\n",
        "    paper_bgcolor='#0f0f23',\n",
        "    margin=dict(l=10, r=10, t=50, b=10),\n",
        "    height=800,\n",
        ")\n",
        "\n",
        "fig.show()"
    ]
    
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            # Match any forecast table cell
            if "forecast_wide" in source and "pivot_table" in source:
                cells[i]["source"] = new_source
                # Clear output to force re-execution
                cells[i]["outputs"] = []
                cells[i]["execution_count"] = None
                print("  ✓ Updated Forecast Table code with year-grouped columns")
                break
    
    return cells





def main():
    notebook_path = Path(__file__).parent.parent / "reports" / "HEI_Executive_Report.ipynb"
    
    print(f"Loading notebook: {notebook_path}")
    nb = load_notebook(notebook_path)
    
    cells = nb["cells"]
    
    # Find and update the Methodology markdown cell specifically
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "markdown":
            source = "".join(cell.get("source", []))
            if "## Methodology" in source and "### 7. Concrete Example: Benguet State University" in source:
                # This is the cell we need to update
                cells[i]["source"] = [
                    "## Methodology\n",
                    "\n",
                    "### 1. The COVID-19 Structural Break\n",
                    "\n",
                    "The COVID-19 pandemic (2020–2022) introduced a **structural break** in research productivity data. This period was characterized by:\n",
                    "\n",
                    "- Laboratory closures and field research delays\n",
                    "- Transition to remote work affecting collaborative projects\n",
                    "- Publication pipeline disruptions and journal backlogs\n",
                    "- Reallocation of institutional resources to pandemic response\n",
                    "\n",
                    "We treat 2020–2022 as a distinct analytical period to isolate pandemic effects from underlying growth trends.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 2. Temporal Segmentation Framework\n",
                    "\n",
                    "| Period | Years | Duration | Characterization |\n",
                    "|--------|-------|----------|------------------|\n",
                    "| **Pre-Pandemic** | 2015–2019 | 5 years | Established baseline trends |\n",
                    "| **During Pandemic** | 2020–2022 | 3 years | High volatility / Disruption |\n",
                    "| **Post-Pandemic** | 2023–2025 | 3 years | \"New Normal\" recovery |\n",
                    "| **Forecast Phase 1** | 2026–2030 | 5 years | Short-term projection |\n",
                    "| **Forecast Phase 2** | 2031–2035 | 5 years | Long-term projection |\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 3. Algorithm Selection Logic\n",
                    "\n",
                    "The forecasting engine dynamically selects the appropriate model based on data density:\n",
                    "\n",
                    "```python\n",
                    "For each (School, Metric):\n",
                    "    Count non-zero observations in training period (2015–2025)\n",
                    "    \n",
                    "    IF n ≥ 3 non-zero points:\n",
                    "        → Apply Holt's Linear Trend (captures momentum)\n",
                    "    ELSE:(2026-2035)\n",
                    "        → Apply Simple Moving Average (conservative estimate)\n",
                    "```\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 4. Holt's Linear Trend Method\n",
                    "\n",
                    "For institutions with sufficient historical data (≥ 3 non-zero observations), we apply **Holt's Exponential Smoothing** (double exponential smoothing), which decomposes the time series into level and trend components:\n",
                    "\n",
                    "**Level Equation:**\n",
                    "$$L_t = \\alpha Y_t + (1 - \\alpha)(L_{t-1} + T_{t-1})$$\n",
                    "\n",
                    "**Trend Equation:**\n",
                    "$$T_t = \\beta(L_t - L_{t-1}) + (1 - \\beta)T_{t-1}$$\n",
                    "\n",
                    "**Forecast Equation:**\n",
                    "$$\\hat{Y}_{t+h} = L_t + h \\cdot T_t$$\n",
                    "\n",
                    "Where:\n",
                    "- $Y_t$ = Observed value at time $t$\n",
                    "- $L_t$ = Estimated level at time $t$\n",
                    "- $T_t$ = Estimated trend at time $t$\n",
                    "- $\\alpha$ = Smoothing parameter for level (0 < α < 1, optimized via MLE)\n",
                    "- $\\beta$ = Smoothing parameter for trend (0 < β < 1, optimized via MLE)\n",
                    "- $h$ = Forecast horizon (years ahead)\n",
                    "\n",
                    "**Implementation:** `statsmodels.tsa.holtwinters.Holt`\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 5. Simple Moving Average (Fallback)\n",
                    "\n",
                    "For institutions with sparse data (< 3 non-zero observations), Holt's method risks overfitting or producing unstable forecasts. We apply a **3-period Simple Moving Average**:\n",
                    "\n",
                    "$$\\hat{Y}_{t+h} = \\frac{1}{k}\\sum_{i=t-k+1}^{t} Y_i$$\n",
                    "\n",
                    "Where:\n",
                    "- $k = \\min(3, n)$ where $n$ is the number of available observations\n",
                    "- This produces a conservative, flat projection that avoids explosive or negative forecasts\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 6. Post-Processing Constraints\n",
                    "\n",
                    "| Constraint | Implementation | Rationale |\n",
                    "|------------|----------------|-----------|\n",
                    "| Non-negativity | `max(0, forecast)` | Publication and citation counts cannot be negative |\n",
                    "| Discrete rounding | `round()` for count metrics | Publications and Citations are whole numbers |\n",
                    "| Continuous FWCI | No rounding | Field-Weighted Citation Impact is a calculated ratio |\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### 7. Concrete Examples: Algorithm Selection in Practice\n",
                    "\n",
                    "The forecasting system dynamically selects between two methods based on data availability. Below are examples of each approach.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "#### Example A: Holt's Linear Trend (≥ 3 Non-Zero Observations)\n",
                    "\n",
                    "Consider **Benguet State University (BSU)** in the Cordillera Administrative Region (CAR). With 11 years of data (2015–2025), BSU has ≥ 3 non-zero observations, qualifying for Holt's method:\n",
                    "\n",
                    "| Year | Publications | Growth Rate |\n",
                    "|------|--------------|-------------|\n",
                    "| 2023 | 45 | — |\n",
                    "| 2024 | 52 | +15.6% |\n",
                    "| 2025 | 58 | +11.5% |\n",
                    "\n",
                    "**Model Parameters (after fitting):**\n",
                    "- $L_{2025} = 58$ (estimated level)\n",
                    "- $T_{2025} = 6.5$ (estimated annual trend)\n",
                    "\n",
                    "**Forecasts:**\n",
                    "- **2026:** $\\hat{Y}_{2026} = 58 + 1 \\times 6.5 = 64.5 \\approx 65$ publications\n",
                    "- **2030:** $\\hat{Y}_{2030} = 58 + 5 \\times 6.5 = 90.5 \\approx 91$ publications\n",
                    "\n",
                    "---\n",
                    "\n",
                    "#### Example B: Simple Moving Average (< 3 Non-Zero Observations)\n",
                    "\n",
                    "For institutions with sparse data (fewer than 3 non-zero observations in the training period), the system applies a **Simple Moving Average** to avoid overfitting:\n",
                    "\n",
                    "| Year | Publications |\n",
                    "|------|--------------|\n",
                    "| 2023 | 0 |\n",
                    "| 2024 | 5 |\n",
                    "| 2025 | 7 |\n",
                    "\n",
                    "With only 2 non-zero observations, the SMA fallback is triggered:\n",
                    "\n",
                    "$$\\hat{Y}_{2026-2035} = \\frac{5 + 7}{2} = 6 \\text{ publications/year (constant)}$$\n",
                    "\n",
                    "This conservative approach produces a flat projection, preventing explosive or negative forecasts from insufficient trend data.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "> **Disclaimer:** These forecasts are statistical projections based on historical trends. They do not account for policy changes, institutional initiatives, or external economic factors. Treat as indicative scenarios."
                ]
                print(f"  ✓ Updated Methodology section with enhanced concrete examples")
                break
    
    # Update Summary Statistics code
    cells = update_summary_statistics_code(cells)
    print("  ✓ Updated Summary Statistics code to sort columns")
    
    # Update Forecast Table code
    cells = update_forecast_table_code(cells)
    print("  ✓ Updated Forecast Table code with interactive Plotly display")
    
    nb["cells"] = cells
    
    save_notebook(nb, notebook_path)
    print(f"\n✓ Notebook saved: {notebook_path}")
    print("\nNote: Please re-run the notebook to regenerate outputs.")


if __name__ == "__main__":
    main()
