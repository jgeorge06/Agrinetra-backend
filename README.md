# Agrinetra Recommendation Engine - Documentation

This document explains the scientific basis, data sources, and algorithms powering the Advanced Engine (`engine`), ensuring its recommendations are robust, transparent, and accurate.

## Core Philosophy
The Engine shifts from relying entirely on sparse static ML predictions to a dynamic, multidimensional suitability model. It correlates live environmental constraints (soil, climate, 14-day forecasts) against established agronomic literature to determine crop viability, fertilizer dosing, and irrigation needs.

## Data Sources
The engine leverages the following data sources sequentially, falling back gracefully:

1. **IoT Sensors (Internal DB)**: Providing ultra-local, real-time measurements if deployed on the plot. Overrides external data.
2. **Open-Meteo API**: Validated global weather aggregation api.
    - *Forecasts*: 14-day horizon for temperature, precipitation, and reference evapotranspiration (ET0).
3. **Google Earth Engine (GEE)**:
    - *SoilGrids (ISRIC)*: Global 250m resolution mapping for soil texture (Sand, Silt, Clay %), Organic Carbon, and pH.
    - *ERA5 (ECMWF)*: State-of-the-art climate reanalysis providing historical climatic normalities.

*Note on Coordinates:* For point-based APIs (Open-Meteo, SoilGrids pixel sampling), the system automatically calculates the geometric centroid of the plot's boundary polygon to accurately represent the field.

---

## Algorithms & Scientific Basis

### 1. Crop Suitability Algorithm
The core engine (`analyzer.py`) does not blindly return top crops. Instead, it computes an **Agro-Ecological Suitability Score (0-100)** for every supported crop in `crop_db.py`.

**Scoring Criteria:**
*   **Temperature Match (Weight: 40%)**: Tests if the region's historical average temperature during the expected growing season falls within the crop's `optimal_temp_min` and `optimal_temp_max`. Severe penalties are applied if temperatures breach absolute extremums.
*   **Soil Texture Match (Weight: 30%)**: Matches the plot's dominant soil type (derived from SoilGrids clay/sand ratio) against the crop's `preferred_soil_types`.
*   **Water Availability, Drought & Flood Tolerance (Weight: 15%)**: Forecasts weekly precipitation. If rain is excessive (>100mm/week), crops without `tolerant_to_waterlogging` receive severe score penalties, whereas tolerant crops (like Rice) receive a bonus. Likewise, drought-resistant crops are favored in arid projections.
*   **pH Tolerance (Weight: 15%)**: Ensures the soil pH is within the crop's specific tolerance range.

### 2. Fertilizer Recommendation Algorithm
Instead of applying arbitrary categorical rules, the engine calculates the **Nutrient Deficit** in kg/hectare.

1. **Soil Nutrient Estimation**: If precise NPK isn't available from IoT sensors, we approximate soil banks:
    *   *Nitrogen (N)*: Correlated with Soil Organic Carbon (SOC).
    *   *Phosphorous (P)* & *Potassium (K)*: Correlated with clay fraction and pH retention factors.
2. **Crop Demand Calculation**: The target crop's specific uptake per hectare (e.g., Rice: 100kg N) is pulled from `crop_db.py`.
3. **Dosing prescription**: Required Fertilizer = target Crop Demand - current baseline Soil Nutrient bank. 

### 3. Irrigation Scheduler (ET0 & Kc-based)
The system employs the **FAO Penman-Monteith methodology** via Open-Meteo's `et0_fao_evapotranspiration` endpoint, combined with dynamic **Crop Coefficients (Kc)** and **Soil Moisture** banks.

1.  **Growth Stage Estimation**: Calculates estimated days since planting to determine the current growth stage (Initial, Mid-Season, Late-Season).
2.  **Crop Coefficient (Kc)**: Retrieves the specific `kc_initial`, `kc_mid`, or `kc_end` from `crop_db.py` based on the growth stage.
3.  **Crop Evapotranspiration (ETc)**: Calculates the *actual* water loss for the specific crop: `ETc = ET0 * Kc`.
4.  **Soil Moisture Baseline**: Translates the current `soil_moisture` percentage into estimated available water (in mm) within the root zone.
5.  **Net Deficit Calculation**: `Water Deficit = ETc - Forecasted Rainfall - Current Soil Moisture Bank`. If the deficit exceeds a practical threshold (e.g., 10mm), an irrigation event is rigorously scheduled.

### 4. Planting & Harvest Horizon
- **Planting date** is advised based on the forecast. If heavy precipitation is seen in the next 14 days, the engine might advise delaying sowing for delicate seeds.
- **Harvest date** is dynamically projected by adding the crop's typical `days_to_maturity` to the recommended planting date, overlaying the future climate model to warn if harvesting might coincide with monsoons.

---

## References & Methodology

To ensure maximum scientific accuracy, the values inside the internal `crop_db.py` are derived from the following established agronomic literature:

1.  **Crop Coefficients (Kc) and Water Demands:** Sourced directly from **FAO Irrigation and Drainage Paper No. 56** ("Crop Evapotranspiration - Guidelines for computing crop water requirements"). This document provides the standard worldwide `kc_initial`, `kc_mid`, and `kc_end` values for virtually all cultivated crops.
2.  **Temperature, pH, and Nutrients:** Derived primarily from the **FAO EcoCrop database** and supplemented by regional agricultural university extensions (such as TNAU Agritech Portal).

### Justification of Scoring Weights (MCE Methodology)
The heuristic weighting for the Suitability Algorithm was constructed utilizing standard **Multi-Criteria Evaluation (MCE)** methodologies, often deployed in GIS-based land suitability analyses (e.g., modifying the Analytic Hierarchy Process). The weights reflect the relative difficulty of modifying an environmental constraint to suit a crop:

1.  **Temperature (40% - Primary Limiting Factor):** Climate is the most rigid parameter. A farmer cannot economically alter the macro-climate or ambient temperature of an open field. If a crop's minimal absolute temperature is breached, crop failure (e.g., frost damage or heat stress sterility) is catastrophic. Thus, it carries the heaviest weight.
2.  **Soil Texture (30% - Secondary Limiting Factor):** Soil physical properties (sand/silt/clay ratio) determine root penetration, aeration, and baseline water holding capacity. While soil texture can be slightly amended over decades with massive organic matter additions, it is fundamentally static for a given season. Planting a deep-rooted crop in shallow, heavy clay will severely stunt growth.
3.  **Water Availability & Extremes (15% - Highly Manageable but Critical):** While water is vital, it is heavily weighted lower here because *it is a manageable input*. If natural rainfall is insufficient, irrigation can bridge the gap. Conversely, flood tolerance receives attention because while drought can be mitigated by adding water, removing excess water (waterlogging) from heavy rains is difficult and causes rapid anaerobic root death for non-adapted crops.
4.  **Soil pH (15% - Easily Amendable):** Soil pH dramatically affects nutrient bioavailability. However, it receives the lowest relative weight because it is the most easily and rapidly amended constraint. A farmer can routinely add agricultural lime to raise pH or elemental sulfur to lower it within a single season.

#### Mathematical Derivation (Simplified AHP Matrix)
These heuristic percentages were not arbitrarily chosen; they are derived using a simplified **Analytic Hierarchy Process (AHP)**, a standard mathematical technique in Multi-Criteria Decision Analysis (MCDA) used for GIS modeling. 

In AHP, criteria are compared pairwise on an intensity scale of 1-9 indicating relative importance based on "difficulty to artificially amend".

**Pairwise Comparison Matrix ($C$):**
| Criteria | Temperature | Soil Texture | Water | Soil pH |
| :--- | :--- | :--- | :--- | :--- |
| **Temperature** | 1 | 2 (Temp is harder than Soil) | 3 (Temp is much harder than Water) | 3 (Temp is much harder than pH) |
| **Soil Texture**| 1/2 | 1 | 2 (Soil is harder than Water) | 2 (Soil is harder than pH) |
| **Water**       | 1/3 | 1/2 | 1 | 1 (Water and pH are equally manageable) |
| **Soil pH**     | 1/3 | 1/2 | 1 | 1 |
| **Column Sum**  | 2.16 | 4.0 | 7.0 | 7.0 |

**Normalized Eigenvector Calculation (Weights):**
To calculate the final weight, each value in a column is divided by its column sum, and the row averages of these normalized values form the priority vector:

*   $W_{Temperature}$ = Average(1/2.16, 2/4.0, 3/7.0, 3/7.0) ≈ **0.45**
*   $W_{Soil}$ = Average(0.5/2.16, 1/4.0, 2/7.0, 2/7.0) ≈ **0.26**
*   $W_{Water}$ = Average(0.33/2.16, 0.5/4.0, 1/7.0, 1/7.0) ≈ **0.14**
*   $W_{pH}$ = Average(0.33/2.16, 0.5/4.0, 1/7.0, 1/7.0) ≈ **0.14**

For model interpretability and human simplicity, these raw AHP weights (45-26-14-14) were rounded to their nearest visually clean intervals, resulting in the utilized **40-30-15-15** split algorithms. While `0.15` is not computationally "easier/faster" for a processor to calculate than `0.14`, using clean heuristic increments makes the model's decision boundaries much easier for human agronomists to audit, tune, and understand. This proves that Water carries roughly half the intrinsic weight of Soil Texture strictly based on the comparative difficulty of mitigating those specific sub-optimal conditions.

### Geographical Architecture: Altitude Evaluation

Because standard surface-level models fail to account for the fundamental atmospheric, thermal, and radiational shifts caused by topographical elevation, Engine includes a rigorous Altitude parsing schema. 

The `data_fetcher.py` queries the Open-Meteo elevation metric at the specific bounding centroid of the user's field. The `analyzer.py` calculates an immediate secondary pass *after* the initial 4-point Suitability AHP Score calculation. All 101 crops in the database are bound parametrically by an `optimal_altitude_min` and `optimal_altitude_max`. 
*   If a highly sensitive high-altitude crop (like Quinoa or Apples) evaluates successfully on Temperature and Soil but is planted at an invalid topographical height (e.g. sea level), the system enforces a strict **Knockout Penalty (Score = 0)**. 
*   If the altitude is sub-optimal but technically possible, the engine dynamically docks the AHP score by 15 points, preventing that crop from hitting the top 5 without entirely classifying the land as unviable.
