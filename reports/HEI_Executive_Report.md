# Philippine Higher Education Research Outlook (2025–2035)

**A Strategic Forecasting Report for HEI Research Productivity**

---

| Metadata                 | Value                                                |
| ------------------------ | ---------------------------------------------------- |
| **Generated Date** | January 2026                                         |
| **Author**         | IRAP System (Integrated Research Analytics Platform) |
| **Classification** | Executive Briefing Document                          |
| **Dataset**        | 3,276 records, 52 schools, 17 regions                |
| **Coverage**       | Historical (2015-2025) & Forecast (2026-2035)        |

---

## Abstract

This report provides a comprehensive analysis of research productivity trends across Philippine Higher Education Institutions (HEIs) from 2015 to 2025, with strategic projections extending to 2035. The study employs a **Pandemic-Aware Forecasting Framework** that explicitly accounts for the structural disruption caused by COVID-19 (2020–2022), ensuring that long-term projections are not contaminated by pandemic-induced volatility. Using Holt's Linear Trend method with Simple Moving Average fallback, we project continued growth in research output across most regions, with notable variations in publication quality as measured by Field-Weighted Citation Impact (FWCI).

---

## Methodology

### 1. The COVID-19 Structural Break

The COVID-19 pandemic (2020–2022) introduced a **structural break** in research productivity data. This period was characterized by:

- Laboratory closures and field research delays
- Transition to remote work affecting collaborative projects
- Publication pipeline disruptions and journal backlogs
- Reallocation of institutional resources to pandemic response

We treat 2020–2022 as a distinct analytical period to isolate pandemic effects from underlying growth trends.

---

### 2. Temporal Segmentation Framework

| Period                     | Years      | Duration | Characterization             |
| -------------------------- | ---------- | -------- | ---------------------------- |
| **Pre-Pandemic**     | 2015–2019 | 5 years  | Established baseline trends  |
| **During Pandemic**  | 2020–2022 | 3 years  | High volatility / Disruption |
| **Post-Pandemic**    | 2023–2025 | 3 years  | "New Normal" recovery        |
| **Forecast Phase 1** | 2026–2030 | 5 years  | Short-term projection        |
| **Forecast Phase 2** | 2031–2035 | 5 years  | Long-term projection         |

---

### 3. Algorithm Selection Logic

The forecasting engine dynamically selects the appropriate model based on data density:

```
For each (School, Metric):
    Count non-zero observations in training period (2015–2025)
  
    IF n ≥ 3 non-zero points:
        → Apply Holt's Linear Trend (captures momentum)
    ELSE:
        → Apply Simple Moving Average (conservative estimate)
```

---

### 4. Holt's Linear Trend Method

For institutions with sufficient historical data (≥ 3 non-zero observations), we apply **Holt's Exponential Smoothing** (double exponential smoothing), which decomposes the time series into level and trend components:

**Level Equation:**

$$
L_t = \alpha Y_t + (1 - \alpha)(L_{t-1} + T_{t-1})
$$

**Trend Equation:**

$$
T_t = \beta(L_t - L_{t-1}) + (1 - \beta)T_{t-1}
$$

**Forecast Equation:**

$$
\hat{Y}_{t+h} = L_t + h \cdot T_t
$$

Where:

- $Y_t$ = Observed value at time $t$
- $L_t$ = Estimated level at time $t$
- $T_t$ = Estimated trend at time $t$
- $\alpha$ = Smoothing parameter for level (0 < α < 1, optimized via MLE)
- $\beta$ = Smoothing parameter for trend (0 < β < 1, optimized via MLE)
- $h$ = Forecast horizon (years ahead)

**Implementation:** `statsmodels.tsa.holtwinters.Holt`

---

### 5. Simple Moving Average (Fallback)

For institutions with sparse data (< 3 non-zero observations), Holt's method risks overfitting or producing unstable forecasts. We apply a **3-period Simple Moving Average**:

$$
\hat{Y}_{t+h} = \frac{1}{k}\sum_{i=t-k+1}^{t} Y_i
$$

Where:

- $k = \min(3, n)$ where $n$ is the number of available observations
- This produces a conservative, flat projection that avoids explosive or negative forecasts

---

### 6. Post-Processing Constraints

| Constraint        | Implementation                | Rationale                                            |
| ----------------- | ----------------------------- | ---------------------------------------------------- |
| Non-negativity    | `max(0, forecast)`          | Publication and citation counts cannot be negative   |
| Discrete rounding | `round()` for count metrics | Publications and Citations are whole numbers         |
| Continuous FWCI   | No rounding                   | Field-Weighted Citation Impact is a calculated ratio |

---

### 7. Concrete Examples: Algorithm Selection in Practice

The forecasting system dynamically selects between two methods based on data availability. Below are examples of each approach.

#### Example A: Holt's Linear Trend (≥ 3 Non-Zero Observations)

Consider **Benguet State University (BSU)** in the Cordillera Administrative Region (CAR). With 11 years of data (2015–2025), BSU has ≥ 3 non-zero observations, qualifying for Holt's method:

| Year | Publications | Growth Rate |
| ---- | ------------ | ----------- |
| 2023 | 45           | —          |
| 2024 | 52           | +15.6%      |
| 2025 | 58           | +11.5%      |

**Model Parameters (after fitting):**

- $L_{2025} = 58$ (estimated level)
- $T_{2025} = 6.5$ (estimated annual trend)

**Forecasts:**

- **2026:** $\hat{Y}_{2026} = 58 + 1 \times 6.5 = 64.5 \approx 65$ publications
- **2030:** $\hat{Y}_{2030} = 58 + 5 \times 6.5 = 90.5 \approx 91$ publications

#### Example B: Simple Moving Average (< 3 Non-Zero Observations)

For institutions with sparse data (fewer than 3 non-zero observations in the training period), the system applies a **Simple Moving Average** to avoid overfitting:

| Year | Publications |
| ---- | ------------ |
| 2023 | 0            |
| 2024 | 5            |
| 2025 | 7            |

With only 2 non-zero observations, the SMA fallback is triggered:

$$
\hat{Y}_{2026-2035} = \frac{5 + 7}{2} = 6 \text{ publications/year (constant)}
$$

This conservative approach produces a flat projection, preventing explosive or negative forecasts from insufficient trend data.

---

> **Disclaimer:** These forecasts are statistical projections based on historical trends. They do not account for policy changes, institutional initiatives, or external economic factors. Treat as indicative scenarios.

---

## Summary Statistics by Period

| Period                                 | Publication Quantity | Citation Quantity | Field-Weighted Citation Impact |
| -------------------------------------- | -------------------- | ----------------- | ------------------------------ |
| **Pre-Pandemic (2015-2019)**     | 2,278                | 25,162            | 125                            |
| **During Pandemic (2020-2022)**  | 3,649                | 33,922            | 128                            |
| **Post-Pandemic (2023-2025)**    | 6,766                | 16,078            | 138                            |
| **Forecast Phase 1 (2026-2030)** | 19,652               | 32,322            | 376                            |
| **Forecast Phase 2 (2031-2035)** | 30,390               | 37,854            | 547                            |

### Key Observations

1. **Publication Growth Acceleration:** Post-pandemic period shows nearly 3x growth compared to pre-pandemic baseline
2. **Citation Recovery:** Citations dropped in post-pandemic period (lag effect), but forecast shows strong recovery
3. **FWCI Improvement:** Projected continuous improvement in research quality through 2035

---

## Geospatial Analysis

The following maps display the regional evolution of research productivity across the five strategic periods. Color intensity and bubble size represent **average annual values**.

### Pre-Pandemic Period (2015-2019)

Established baseline trends showing initial research distribution across Philippine regions.

![Publication Quantity](1.%20pre_pandemic/pub.png)
![Citation Quantity](1.%20pre_pandemic/citation.png)
![FWCI](1.%20pre_pandemic/fwci.png)

---

### During Pandemic Period (2020-2022)

High volatility and disruption period showing mixed regional impacts.

![Publication Quantity](2.%20during_pandemic/pub.png)
![Citation Quantity](2.%20during_pandemic/citation.png)
![FWCI](2.%20during_pandemic/fwci.png)


---

### Post-Pandemic Period (2023-2025)

"New Normal" recovery showing resilient institutional capacity.

![Publication Quantity](3.%20post_pandemic/pub.png)
![Citation Quantity](3.%20post_pandemic/citation.png)
![FWCI](3.%20post_pandemic/fwci.png)

---

### Forecast Phase 1 (2026-2030)

Short-term projections indicating sustained growth momentum.

![Publication Quantity](4.%20forecast_1/pub.png)
![Citation Quantity](4.%20forecast_1/citation.png)
![FWCI](4.%20forecast_1/fwci.png)

---

### Forecast Phase 2 (2031-2035)

Long-term projections showing mature research ecosystem development.

![Publication Quantity](5.%20forecast_2/pub.png)
![Citation Quantity](5.%20forecast_2/citation.png)
![FWCI](5.%20forecast_2/fwci.png)

---

## Strategic Outlook

### Key Insights

1. **Regional Concentration Risk:** NCR continues to dominate national research output. Strategic investments in regional research centers can diversify the national research portfolio.
2. **Quantity vs. Quality Trade-off:** Regions with high publication growth but low FWCI should prioritize quality assurance mechanisms.
3. **Post-Pandemic Recovery:** The 2023–2025 recovery period shows resilient institutional capacity.
4. **Emerging Research Hubs:** Regions showing steep growth trajectories represent opportunities for targeted capacity-building.

---

### Recommended Actions

| Priority         | Action Item                                          |
| ---------------- | ---------------------------------------------------- |
| **High**   | Establish regional research consortia                |
| **High**   | Implement FWCI-based incentive structures            |
| **Medium** | Develop pandemic-resilient research continuity plans |
| **Low**    | Monitor forecast accuracy and recalibrate annually   |

---

## Data Access

Complete forecast data (2026–2035) is available in the companion Excel file:
`HEI_Research_Report_Data.xlsx`

**Worksheets:**

- **Historical Figures** (2015-2025): 52 schools × 36 columns
- **Forecasted Figures** (2026-2035): 52 schools × 33 columns

**Column Key:**

- Pub = Publication Quantity
- Cit = Citation Quantity
- FWCI = Field-Weighted Citation Impact

---

## Conclusion

This forecasting framework provides a data-driven foundation for strategic planning in Philippine HEI research development. The pandemic-aware methodology ensures that projections reflect sustainable growth patterns rather than anomalous volatility. Stakeholders are encouraged to use these insights for evidence-based policy formulation while remaining cognizant of the inherent uncertainty in long-term projections.

**Next Steps:**

1. Quarterly monitoring of actual vs. forecasted values
2. Annual model recalibration with updated data
3. Integration with institutional strategic plans
4. Development of intervention impact assessment framework

---

*Report generated by the IRAP System (Integrated Research Analytics Platform)*
*For technical inquiries or data requests, contact the research analytics team*
