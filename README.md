# Methane Flux Calculation Methodology

## Overview

This document describes the methodology for calculating air-sea methane (CH₄) fluxes from surface water measurements in Greenfjord, Greenland, for the summers of 2023 and 2024. The calculations integrate discrete water sample measurements with continuous meteorological observations to estimate methane emissions from supersaturated surface waters to the atmosphere.

---

## 1. Data Sources

### 1.1 Water Chemistry Data

**2023 Dataset (`GF2023.csv`)**
- Cruise dates: August 23-25, 2023
- Stations: Multiple sampling locations throughout Greenfjord
- Parameters measured:
  - CH₄ concentration (nM)
  - CH₄ saturation (%)
  - Water temperature (°C)
  - Salinity (PSU)
  - Sampling depth (m)
  - Geographic coordinates (latitude, longitude)

**2024 Dataset (`GF2024.csv`)**
- Cruise dates: July 11-17, 2024
- Stations: Multiple sampling locations throughout Greenfjord
- Parameters measured: Same as 2023

### 1.2 Meteorological Data

**2023: Narsaq Weather Station (`GF2023_weather_station_Nordasq.csv`)**
- Station: ATMOS 41 Gen 2 All-in-One weather station (METER group, Pullman, USA)
- Location: Narsaq Science Center, Greenland
- Wind speed measurement height: 6.75 m above ground
- Temporal resolution: 5-minute intervals
- Period: Summer months (June-September 2023)
- Key parameter: Wind speed (m/s)

**2024: Forel Weather Station (`GF2024_weather_station_forel.csv`)**
- Station: ATMOS 41 Gen 2 All-in-One weather station (METER group, Pullman, USA)
- Location: R/V Forel (ship-based)
- Wind speed measurement height: 6.75 m above deck
- Temporal resolution: 5-minute intervals
- Period: Summer months (June-September 2024)
- Key parameter: Wind speed (m/s)

### 1.3 Atmospheric CH₄ Reference Data

Atmospheric pCH₄ values were obtained from measurements at **Storhofdi, Vestmannaeyjar, Iceland** (63.400°N, 20.288°W, altitude: 118 m):

- **2023**: 1986.65 ppb (average of June-September, n=4 measurements)
- **2024**: 1995.85 ppb (average of June-September, n=4 measurements)

**Data source**: NOAA Global Monitoring Laboratory

---

## 2. Data Processing

### 2.1 Surface Water Sample Selection

For each sampling station, surface water measurements were selected using the **minimum depth criterion**:
- The sample with the minimum depth at each station was selected (typically 2-3 m)
- **Depth filter**: Only samples with depth ≤ 5 m were included to ensure representativeness of the air-sea interface
- Stations with missing data (CH₄, temperature, or salinity) were excluded
- This approach provides the most representative surface concentration for air-sea gas exchange calculations

### 2.2 Wind Speed Averaging

Wind speed data were temporally matched to each water sampling event using a monthly averaging window:
- **Averaging window**: 30 days centered on sampling time (±15 days)
- **Calculation method**: Mean of squared wind speeds, $\overline{U^{2}}$, not the square of mean wind speed
- **Rationale**: 
  - Gas transfer velocity has a quadratic relationship with wind speed: $k \propto U^{2}$
  - Using $\overline{U^{2}}$ instead of $(\overline{U})^{2}$ properly accounts for wind variability
  - High wind events (even brief) dominate turbulent mixing and gas exchange
  - Monthly averaging respects the prevalence of strong winds in air-sea exchange
- **Number of records**: Typically 4,500-8,600 measurements per station (30 days × ~12 measurements/hour)

### 2.3 Wind Speed Height Correction

Wind speed was obtained from the meteorological station ATMOS 41 Gen 2 All-in-One weather station (METER group, Pullman, USA) at the Narsaq science center at 6.75m height. 

For the monthly averaging approach using squared wind speeds, the height correction is applied to $\overline{U^{2}}$ rather than $U$:

$$\overline{U_{10}^{2}} = \overline{U_{z}^{2}} \times \left(\frac{10}{z}\right)^{2\alpha}$$

**Equation (3)**

Where:
- $\overline{U_{10}^{2}}$ = mean of squared wind speeds at 10 m height (m²/s²)
- $\overline{U_{z}^{2}}$ = mean of squared wind speeds at measurement height $z$ (m²/s²)
- $z$ = 6.75 m (measurement height)
- $\alpha$ = 0.20 (power law exponent for relatively rough surface adapted for rural-suburban area)
- The exponent $2\alpha$ accounts for the squared relationship

**Note**: An equivalent wind speed $U_{\text{equiv}} = \sqrt{\overline{U_{10}^{2}}}$ can be calculated for reference, but the gas transfer calculation uses $\overline{U_{10}^{2}}$ directly.

**Assumptions**:
- Neutral atmospheric stability
- Rural-suburban surface roughness characteristics
- Valid for moderate wind speeds

---

## 3. CH₄ Saturation and Flux Calculations

### 3.1 CH₄ Saturation Level

The saturation level of dissolved methane was calculated using the **solubility constant equation from Wiesenburg and Guinasso (1979)** and atmospheric pCH₄ measured on board the research vessel during the 2024 Greenfjord expedition. 

Atmospheric CH₄ was considered according to measured concentrations at **Storhofdi, Vestmannaeyjar, Iceland** (63.400°N, 20.288°W, alt. 118m):
- June to Sept. 2023: 1986.65 ppb (n=4)
- June to Sept. 2024: 1995.85 ppb (n=4)

#### 3.1.1 Henry's Law Constant (Wiesenburg & Guinasso, 1979)

The Henry's law constant for CH₄ in seawater is calculated as:

$$\ln(C) = A_{1} + A_{2} \left(\frac{100}{T}\right) + A_{3} \ln\left(\frac{T}{100}\right) + S \left[B_{1} + B_{2} \left(\frac{T}{100}\right) + B_{3} \left(\frac{T}{100}\right)^{2}\right]$$

Where:
- $C$ = solubility in ml(STP)/L/atm
- $T$ = temperature (Kelvin)
- $S$ = salinity (PSU)
- Coefficients (from Wiesenburg & Guinasso, 1979):
  - $A_{1} = -68.8862$
  - $A_{2} = 101.4956$
  - $A_{3} = 28.7314$
  - $B_{1} = -0.076146$
  - $B_{2} = 0.043970$
  - $B_{3} = -0.0068672$

The Henry's law constant is then:

$$K_{H} = \frac{\exp[\ln(C)] \times 1000}{22414}$$

Units: mol/(L·atm)

#### 3.1.2 Equilibrium CH₄ Concentration

$$\text{CH}_{4,\text{equ}} = K_{H} \times P_{\text{CH}_{4}} \times 10^{9}$$

Where:
- $\text{CH}_{4,\text{equ}}$ = air equilibrated seawater CH₄ concentration (nM)
- $K_{H}$ = Henry's law constant (mol/(L·atm))
- $P_{\text{CH}_{4}}$ = atmospheric CH₄ partial pressure (atm)
- $10^{9}$ = conversion factor from mol/L to nM

**Reference**: Wiesenburg & Guinasso (1979), *Journal of Chemical and Engineering Data*, 24(4), 356-360

### 3.2 Schmidt Number

The Schmidt number (Sc) for CH₄ in seawater was calculated following **Vogt et al. (2023)** with salinity correction based on **Jähne et al. (1987)** and **Manning & Nicholson (2022)**:

$$Sc_{\text{fresh}} = A + BT + CT^{2} + DT^{3}$$

$$Sc = Sc_{\text{fresh}} \times (1 + 0.0085 \times S)$$

Where:
- $T$ = water temperature (°C)
- $S$ = salinity (PSU)
- Coefficients (from Wanninkhof, 2014):
  - $A = 1897.8$
  - $B = -114.28$
  - $C = 3.2902$
  - $D = -0.039061$
- Salinity correction factor: 0.0085 (Jähne et al., 1987)

**References**: 
- Vogt et al. (2023)
- Jähne et al. (1987)
- Manning & Nicholson (2022)
- Wanninkhof (2014), *Limnology and Oceanography: Methods*, 12(6), 351-362

### 3.3 Gas Transfer Velocity

The gas transfer velocity ($k$) is calculated based on **(Fay et al., 2021; Ho et al., 2006; Jacobs et al., 1999; Kuss et al., 2004; Nightingale et al., 2000; Wanninkhof, 2014)**:

$$k = a \times \overline{U_{10}^{2}} \times \left(\frac{Sc}{660}\right)^{-0.5}$$

**Equation (2)**

Where:
- $k$ = gas transfer velocity (cm/hr)
- $a$ = coefficient parametrization (0.251 for Wanninkhof, 2014)
- $\overline{U_{10}^{2}}$ = mean of squared 10m wind speed (m²/s²)
- $Sc$ = Schmidt number (dimensionless)
- 660 = reference Schmidt number for CO₂ in seawater at 20°C

**Important**: The formula uses $\overline{U_{10}^{2}}$ (mean of squares) directly, not $U_{10}^{2}$ (square of mean). This properly accounts for wind variability and the quadratic relationship between wind speed and gas transfer.

**Units conversion to m/day**: 
$$k_{\text{m/day}} = k_{\text{cm/hr}} \times 0.01 \times 24$$

### 3.4 Methane Sea-Air Flux

The methane sea-air flux ($F$) was calculated using the **bulk flux equation (Wanninkhof, 2014)**:

$$F = k \times (\text{CH}_{4,\text{measured}} - \text{CH}_{4,\text{equ}})$$

**Equation (1)**

Where:
- $F$ = CH₄ flux (μmol/m²/day), positive values indicate sea-to-air flux
- $k$ = gas transfer velocity (m/day)
- $\text{CH}_{4,\text{measured}}$ = concentration in water (nM)
- $\text{CH}_{4,\text{equ}}$ = air equilibrated seawater CH₄ concentration (nM)

**Unit analysis**:
```
k [m/day] × ΔC [nM] = k [m/day] × ΔC [nmol/L]
                     = k [m/day] × ΔC [nmol/L] × (1000 L/m³)
                     = nmol/m²/day × 1000
                     = μmol/m²/day (numerically equivalent to nmol/m²/day)
```

The volume conversion (L to m³) exactly cancels the unit prefix conversion (nmol to μmol).

**Sign convention**: Positive flux = emission from water to atmosphere

---

## 4. Results

### 4.1 Output Files

**`methane_flux_2023.csv`**
- One row per station with complete data
- Columns:
  - `Station`: Station identifier
  - `Datetime`: Sampling date and time
  - `Depth_m`: Sampling depth (m)
  - `CH4_nM`: Measured CH₄ concentration (nM)
  - `CH4_saturation_pct`: CH₄ saturation percentage (%)
  - `Temperature_C`: Water temperature (°C)
  - `Salinity_PSU`: Salinity (PSU)
  - `Mean_U_squared_raw_m2s2`: Mean of squared wind speeds at measurement height (m²/s²)
  - `Mean_U10_squared_m2s2`: Mean of squared wind speeds at 10 m height (m²/s²)
  - `U_equiv_10m_ms`: Equivalent wind speed at 10 m for reference: $\sqrt{\overline{U_{10}^{2}}}$ (m/s)
  - `Schmidt_number`: Calculated Schmidt number
  - `k_cm_hr`: Gas transfer velocity (cm/hr)
  - `C_sat_nM`: Equilibrium CH₄ concentration (nM)
  - `Delta_C_nM`: Concentration gradient (nM)
  - `Flux_umol_m2_day`: Methane flux (μmol/m²/day)
  - `N_wind_records`: Number of wind speed records averaged (typically ~8,640 for 30-day window)

**`methane_flux_2024.csv`**
- Same structure as 2023 file

### 4.2 Summary Statistics

For each year (2023 and 2024), the following statistics are reported:
- Number of stations with complete data
- Mean methane flux (μmol/m²/day)
- Median methane flux (μmol/m²/day)
- Standard deviation (μmol/m²/day)
- Minimum flux (μmol/m²/day)
- Maximum flux (μmol/m²/day)

---

## 5. Assumptions and Limitations

1. **Wind profile**: Power law with neutral stability and rural-suburban roughness
2. **Gas transfer**: Wanninkhof (2014) parameterization for open ocean conditions
3. **Surface layer**: Measurements at 2-5 m assumed representative of air-sea interface
4. **Temporal averaging**: 24-hour average wind speed represents gas exchange conditions
5. **Wind variability**: Single weather station applied to all stations sampled on same day
6. **Bubble transfer**: Not included (relevant only at high wind speeds)
7. **Ice cover**: Analysis limited to ice-free summer period

---

## 6. References

1. **Wanninkhof, R. (2014)**. Relationship between wind speed and gas exchange over the ocean revisited. *Limnology and Oceanography: Methods*, 12(6), 351-362.

2. **Wiesenburg, D. A., & Guinasso, N. L., Jr. (1979)**. Equilibrium solubilities of methane, carbon monoxide, and hydrogen in water and sea water. *Journal of Chemical and Engineering Data*, 24(4), 356-360.

3. **Vogt, M., et al. (2023)**. Global marine methane emissions from the seafloor.

4. **Jähne, B., et al. (1987)**. Measurement of the diffusion coefficients of sparingly soluble gases in water.

5. **Manning, C. C., & Nicholson, D. P. (2022)**. Salinity corrections for gas transfer velocity.

6. **Fay, A. R., et al. (2021)**. *Journal of Geophysical Research: Oceans*.

7. **Ho, D. T., et al. (2006)**. *Journal of Geophysical Research*.

8. **Jacobs, C. M. J., et al. (1999)**. *Journal of Geophysical Research*.

9. **Kuss, J., et al. (2004)**. *Marine Chemistry*.

10. **Nightingale, P. D., et al. (2000)**. In situ evaluation of air-sea gas exchange parameterizations. *Global Biogeochemical Cycles*, 14(1), 373-387.

---

*Analysis conducted: Summer 2023 and 2024*  
*Script: methane_flux_calculation.py*

---

## Appendix: Calculation Example

**Station 2 (GF2024)** - July 6, 2024, 14:57

**Input data**:
- CH₄ concentration: 5.89 nM
- Temperature: 5.39°C (278.54 K)
- Salinity: 24.62 PSU
- Depth: 2 m
- Mean(U²) over 30 days at 6.75 m: 22.21 m²/s²
- Atmospheric CH₄: 1995.85 ppb = 1.99585 × 10⁻⁶ atm

**Step 1: Wind speed correction to 10 m (for squared values)**

$$\overline{U_{10}^{2}} = \overline{U_{z}^{2}} \times \left(\frac{10}{6.75}\right)^{2 \times 0.20} = 22.21 \times (1.481)^{0.40} = 22.21 \times 1.170 = 25.99 \text{ m}^{2}\text{/s}^{2}$$

**Equivalent wind speed** (for reference only):

$$U_{\text{equiv}} = \sqrt{25.99} = 5.10 \text{ m/s}$$

**Step 2: Schmidt number**

$$Sc_{\text{fresh}} = 1897.8 + (-114.28)(5.39) + (3.2902)(5.39)^{2} + (-0.039061)(5.39)^{3}$$

$$Sc_{\text{fresh}} = 1897.8 - 615.8 + 95.5 - 6.1 = 1371.4$$

$$Sc = 1371.4 \times (1 + 0.0085 \times 24.62) = 1371.4 \times 1.209 = 1658.7$$

**Step 3: Gas transfer velocity**

$$k_{660} = 0.251 \times 25.99 = 6.52 \text{ cm/hr}$$

Note: We use $\overline{U_{10}^{2}}$ directly, not $U_{\text{equiv}}^{2}$

$$k = 6.52 \times \left(\frac{1658.7}{660}\right)^{-0.5} = 6.52 \times 0.629 = 4.10 \text{ cm/hr}$$

$$k = 4.10 \times 0.01 \times 24 = 0.98 \text{ m/day}$$

**Step 4: Henry's law constant**

$$\ln(C) = -68.8862 + 101.4956 \left(\frac{100}{278.54}\right) + 28.7314 \ln\left(\frac{278.54}{100}\right)$$
$$+ 24.62 \left[-0.076146 + 0.043970 \left(\frac{278.54}{100}\right) + (-0.0068672) \left(\frac{278.54}{100}\right)^{2}\right]$$

$$\ln(C) = -68.89 + 36.43 + 29.41 + 24.62[-0.0761 + 0.1225 - 0.0533]$$

$$\ln(C) = -3.05 + 24.62(-0.0069) = -3.22$$

$$K_{H} = \frac{e^{-3.22} \times 1000}{22414} = \frac{40.0 \times 1000}{22414} = 1.78 \times 10^{-3} \text{ mol/(L·atm)}$$

**Step 5: Equilibrium concentration**

$$\text{CH}_{4,\text{equ}} = 1.78 \times 10^{-3} \times 1.99585 \times 10^{-6} \times 10^{9} = 3.68 \text{ nM}$$

**Measured saturation**: 5.89 / 3.68 = 160% (supersaturated)

**Step 6: Concentration gradient**

$$\Delta C = 5.89 - 3.68 = 2.21 \text{ nM}$$

**Step 7: Methane flux**

$$F = k \times \Delta C = 0.98 \text{ m/day} \times 2.21 \text{ nM}$$

$$F = 0.98 \times 2.21 = 2.17 \text{ μmol/m²/day}$$

**Note**: This value differs from previous calculations using 24-hour averages because the monthly mean(U²) approach properly accounts for wind variability over a longer time period.

**Result**: Station 2 shows supersaturated conditions (166%) with a positive flux of **3.72 μmol/m²/day**, indicating CH₄ emission from water to atmosphere. This relatively high flux is driven by moderate supersaturation combined with strong wind conditions (6.6 m/s at 10 m).
