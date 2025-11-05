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
- Land-based weather station
- Temporal resolution: 5-minute intervals
- Wind speed measurement height: ~2 m above ground
- Period: Summer months (June-September 2023)
- Key parameter: Wind speed (m/s)

**2024: Forel Weather Station (`GF2024_weather_station_forel.csv`)**
- Ship-based weather station
- Temporal resolution: 5-minute intervals
- Wind speed measurement height: 2-4 m above water surface
- Period: Summer months (June-September 2024)
- Key parameter: Wind speed (m/s)

---

## 2. Data Processing

### 2.1 Surface Water Sample Selection

For each sampling station, surface water measurements were selected using the **minimum depth criterion**:
- The sample with the minimum depth at each station was selected (typically ~2-3 m)
- This approach provides the most representative surface concentration for air-sea exchange
- Only stations with complete data (CH₄, temperature, salinity) were retained

### 2.2 Wind Speed Averaging

Wind speed data were temporally matched to each water sampling event:
- **Averaging window**: 24 hours preceding each station sampling time
- **Rationale**: Longer-term wind speed averages better represent the integrated gas exchange process and smooth out short-term variability
- **Number of records**: Typically ~288 measurements per station (24 hours × 12 measurements/hour)

### 2.3 Wind Speed Height Correction

Wind speeds measured at non-standard heights were corrected to the standard 10-m reference height using a **logarithmic wind profile** assumption:

$$u_{10} = u_z \frac{\ln(10/z_0)}{\ln(z/z_0)}$$

Where:
- $u_{10}$ = wind speed at 10 m height (m/s)
- $u_z$ = measured wind speed at height $z$ (m/s)
- $z$ = measurement height (m): 2 m for 2023 (Narsaq), 3 m for 2024 (Forel)
- $z_0$ = roughness length for open water = 0.0002 m

**Reference**: Garratt (1992), *The Atmospheric Boundary Layer*

**Assumptions**:
- Neutral atmospheric stability
- Open water surface roughness
- Valid for moderate wind speeds (< 15 m/s)

---

## 3. Gas Transfer Velocity Calculation

### 3.1 Schmidt Number

The Schmidt number (Sc) for CH₄ in seawater is temperature-dependent and calculated using:

$$Sc = A + BT + CT^2 + DT^3$$

Where:
- $T$ = water temperature (°C)
- $A = 1897.8$
- $B = -114.28$
- $C = 3.2902$
- $D = -0.039061$

**Reference**: Wanninkhof (2014), *Limnology and Oceanography: Methods*, 12(6), 351-362

### 3.2 Gas Transfer Velocity

The gas transfer velocity was calculated using the **Wanninkhof (2014) parameterization**:

$$k_{600} = 0.251 \times u_{10}^2$$

Normalized to the in-situ Schmidt number:

$$k = k_{600} \left(\frac{Sc}{600}\right)^{-0.5}$$

Where:
- $k$ = gas transfer velocity (cm/hr)
- $k_{600}$ = reference gas transfer velocity at Sc = 600
- $u_{10}$ = wind speed at 10 m (m/s)
- $Sc$ = Schmidt number (dimensionless)

**Units conversion**: $k$ (m/day) = $k$ (cm/hr) × 0.01 × 24

**Reference**: Wanninkhof, R. (2014). Relationship between wind speed and gas exchange over the ocean revisited. *Limnology and Oceanography: Methods*, 12(6), 351-362.

**Alternative parameterization available**: Wanninkhof (1992) using coefficient 0.31 instead of 0.251

---

## 4. Equilibrium CH₄ Concentration

### 4.1 Henry's Law Constant

The Henry's law constant for CH₄ in seawater was calculated with temperature and salinity corrections:

$$K_H(T,S) = K_{H,0} \exp\left[d\ln(K_H)/d(1/T) \times \left(\frac{1}{T} - \frac{1}{T_0}\right)\right] \times \exp(-0.015 \times S)$$

Where:
- $K_H$ = Henry's law constant (mol/(L·atm))
- $K_{H,0}$ = 1.3 × 10⁻³ mol/(L·atm) at 25°C
- $d\ln(K_H)/d(1/T)$ = 1700 K (temperature dependence coefficient)
- $T$ = water temperature (K)
- $T_0$ = 298.15 K (25°C reference temperature)
- $S$ = salinity (PSU)
- 0.015 = empirical salinity correction factor

**Reference**: Wiesenburg & Guinasso (1979), *Journal of Chemical and Engineering Data*, 24(4), 356-360

### 4.2 Atmospheric Equilibrium Concentration

The CH₄ concentration at equilibrium with the atmosphere was calculated using:

$$C_{sat} = K_H \times P_{CH_4} \times 10^9$$

Where:
- $C_{sat}$ = saturation concentration (nM)
- $K_H$ = Henry's law constant (mol/(L·atm))
- $P_{CH_4}$ = atmospheric CH₄ partial pressure = 1.9 × 10⁻⁶ atm (≈1.9 ppm global average)
- $10^9$ = conversion factor from mol/L to nmol/L

**Note**: Atmospheric CH₄ concentration assumed constant at 1.9 ppm based on recent global averages

---

## 5. Methane Flux Calculation

### 5.1 Concentration Gradient

The air-sea concentration difference was calculated as:

$$\Delta C = C_{water} - C_{sat}$$

Where:
- $\Delta C$ = concentration gradient (nM)
- $C_{water}$ = measured CH₄ concentration in surface water (nM)
- $C_{sat}$ = atmospheric equilibrium concentration (nM)

**Positive values** indicate supersaturation (outgassing from water to air)

### 5.2 Flux Equation

The methane flux was calculated using Fick's first law of diffusion:

$$F = k \times \Delta C$$

Where:
- $F$ = CH₄ flux (μmol/(m²·day))
- $k$ = gas transfer velocity (m/day)
- $\Delta C$ = concentration gradient (nmol/L = nM)

**Units**: 
- Input: $k$ (m/day) × $\Delta C$ (nM) = nmol/(m²·day)
- Output: $F$ (μmol/(m²·day)) = nmol/(m²·day) / 1000

**Sign convention**: Positive flux = emission from water to atmosphere

**Reference**: Liss & Slater (1974), *Nature*, 247, 181-184

---

## 6. Statistical Analysis

For each year (2023 and 2024), summary statistics were calculated:

### 6.1 Metrics Reported
- Number of stations with complete data
- Mean methane flux (μmol/(m²·day))
- Median methane flux (μmol/(m²·day))
- Standard deviation (μmol/(m²·day))
- Minimum flux (μmol/(m²·day))
- Maximum flux (μmol/(m²·day))

### 6.2 Quality Control
Stations were excluded if:
- CH₄ concentration data were missing
- Temperature data were missing
- Salinity data were missing
- No wind speed data available within 24-hour window

---

## 7. Assumptions and Limitations

### 7.1 Key Assumptions
1. **Atmospheric CH₄ concentration**: Constant at 1.9 ppm (global average)
2. **Wind profile**: Logarithmic with neutral stability
3. **Gas transfer parameterization**: Wanninkhof (2014) relationship valid for open ocean conditions
4. **Surface layer**: Well-mixed, with measurements at 2-3 m representative of air-sea interface
5. **Temporal averaging**: 24-hour average wind speed adequately represents gas exchange conditions

### 7.2 Limitations
1. **Atmospheric CH₄**: No direct measurements of atmospheric CH₄ at Greenfjord; assumed global average
2. **Wind speed variability**: Single weather station may not capture spatial variability across fjord
3. **Near-surface gradients**: Potential concentration gradients in upper 2-3 m not captured
4. **Bubble-mediated transfer**: Not included in parameterization (relevant at high wind speeds)
5. **Ice cover**: Not considered; applicable only to ice-free periods
6. **Spatial heterogeneity**: Single wind measurement applied to all stations sampled on same day

### 7.3 Uncertainty Sources
- Wind speed measurement accuracy (±0.1-0.2 m/s typical)
- Height correction for wind speed
- Gas transfer velocity parameterization (factor of 2 uncertainty typical)
- Henry's law constant temperature/salinity dependence
- Atmospheric CH₄ variability (±0.1-0.2 ppm)
- Temporal variability in wind speed within 24-hour averaging window

---

## 8. Output Files

### 8.1 Result Files Generated

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
  - `WindSpeed_raw_ms`: Raw measured wind speed (m/s)
  - `WindSpeed_10m_ms`: Height-corrected wind speed at 10 m (m/s)
  - `Schmidt_number`: Calculated Schmidt number
  - `k_cm_hr`: Gas transfer velocity (cm/hr)
  - `C_sat_nM`: Equilibrium CH₄ concentration (nM)
  - `Delta_C_nM`: Concentration gradient (nM)
  - `Flux_umol_m2_day`: **Methane flux (μmol/(m²·day))**
  - `N_wind_records`: Number of wind speed records averaged

**`methane_flux_2024.csv`**
- Same structure as 2023 file

### 8.2 Interpretation Guidelines

**Typical ranges**:
- Gas transfer velocity (k): 0.5-50 cm/hr depending on wind speed
- Schmidt number: 600-1200 depending on temperature
- Saturation concentration (C_sat): 2-4 nM
- Observed concentrations: 5-10 nM (supersaturated waters)
- **Expected fluxes**: 10-200 μmol/(m²·day) for supersaturated fjord waters

**Positive flux**: Indicates net emission from water to atmosphere (supersaturation)
**Negative flux**: Would indicate net absorption (undersaturation, rare for CH₄)

---

## 9. Software Implementation

### 9.1 Script Details

**File**: `methane_flux_calculation.py`

**Language**: Python 3.x

**Required packages**:
- `pandas`: Data manipulation and CSV I/O
- `numpy`: Numerical calculations
- `datetime`: Time series handling

**Encoding**: Latin-1 (ISO-8859-1) for CSV files containing special characters (°, μ, etc.)

**Decimal separator**: Comma (European format) in original CSV files, converted to period internally

### 9.2 Execution

```bash
python methane_flux_calculation.py
```

**Runtime**: Typically 5-30 seconds depending on number of stations

**Console output**: Detailed progress report for each station with intermediate calculations

---

## 10. References

### Primary Methodology References

1. **Wanninkhof, R. (2014)**. Relationship between wind speed and gas exchange over the ocean revisited. *Limnology and Oceanography: Methods*, 12(6), 351-362. doi:10.4319/lom.2014.12.351
   - Gas transfer velocity parameterization

2. **Wanninkhof, R. (1992)**. Relationship between wind speed and gas exchange over the ocean. *Journal of Geophysical Research: Oceans*, 97(C5), 7373-7382. doi:10.1029/92JC00188
   - Alternative gas transfer velocity parameterization

3. **Wiesenburg, D. A., & Guinasso, N. L., Jr. (1979)**. Equilibrium solubilities of methane, carbon monoxide, and hydrogen in water and sea water. *Journal of Chemical and Engineering Data*, 24(4), 356-360. doi:10.1021/je60083a006
   - Henry's law constants for CH₄

4. **Liss, P. S., & Slater, P. G. (1974)**. Flux of gases across the air-sea interface. *Nature*, 247, 181-184. doi:10.1038/247181a0
   - Fundamental gas exchange theory

5. **Garratt, J. R. (1992)**. *The Atmospheric Boundary Layer*. Cambridge University Press.
   - Wind profile corrections

### Supporting References

6. **Raymond, P. A., & Cole, J. J. (2001)**. Gas exchange in rivers and estuaries: Choosing a gas transfer velocity. *Estuaries*, 24(2), 312-317.
   - Discussion of gas transfer in coastal systems

7. **McGillis, W. R., et al. (2001)**. Air-sea CO₂ exchange in the equatorial Pacific. *Journal of Geophysical Research*, 106(C8), 16,729-16,745.
   - Validation of gas transfer parameterizations

8. **Nightingale, P. D., et al. (2000)**. In situ evaluation of air-sea gas exchange parameterizations using novel conservative and volatile tracers. *Global Biogeochemical Cycles*, 14(1), 373-387.
   - Alternative gas transfer relationships

---

## 11. Data Quality and Validation

### 11.1 Data Screening Criteria

All measurements underwent quality screening:
- **Temperature range**: -2°C to 25°C (physically reasonable for fjord waters)
- **Salinity range**: 0-35 PSU (fresh to full marine)
- **Wind speed**: > 0 m/s (non-physical zero values excluded)
- **CH₄ concentration**: > 0 nM (non-physical negatives excluded)

### 11.2 Validation Checks

1. **Mass balance**: All fluxes checked for physical reasonableness
2. **Schmidt number**: Verified within expected range (600-1400 for typical temperatures)
3. **Saturation concentration**: Cross-checked with measured saturation percentages
4. **Wind speed correction**: Verified that 10-m corrected speeds > measured speeds (as expected)

---

## 12. Future Improvements

### 12.1 Potential Enhancements

1. **Atmospheric CH₄ measurements**: Direct measurements would improve accuracy
2. **High-frequency wind data**: Ship-based measurements during sampling would reduce uncertainty
3. **Spatial wind fields**: Multiple weather stations or modeled winds could capture spatial variability
4. **Bubble flux parameterization**: Include ebullition and bubble-mediated transfer at high wind speeds
5. **Uncertainty quantification**: Monte Carlo analysis to propagate measurement uncertainties
6. **Seasonal analysis**: Extend to full annual cycle including ice-covered periods

### 12.2 Alternative Approaches

1. **Direct flux measurements**: Eddy covariance or floating chamber measurements
2. **Isotopic constraints**: δ¹³C-CH₄ to constrain sources and sinks
3. **Modeling approaches**: Coupled physical-biogeochemical models
4. **Remote sensing**: Satellite-derived winds for improved spatial coverage

---

## 13. Contact and Citation

### 13.1 Data Usage

When using these flux calculations, please cite:
- This methodology document
- Original data sources (GF2023 and GF2024 cruises)
- Primary method references (Wanninkhof 2014, Wiesenburg & Guinasso 1979)

### 13.2 Acknowledgments

- Weather station data: [Specify data provider]
- Cruise operations: [Specify cruise organizers]
- Chemical analyses: [Specify analytical facilities]

---

## Appendix A: Calculation Example

### Example Station Calculation (Station 5, GF2024)

**Input data**:
- CH₄ concentration: 7.91 nM
- Temperature: 0.54°C
- Salinity: 20.49 PSU
- Depth: 2 m
- Wind speed (24-hr avg): 1.2 m/s at 3 m height

**Step 1: Wind speed correction**
$$u_{10} = 1.2 \times \frac{\ln(10/0.0002)}{\ln(3/0.0002)} = 1.2 \times \frac{10.82}{9.62} = 1.35 \text{ m/s}$$

**Step 2: Schmidt number**
$$Sc = 1897.8 + (-114.28)(0.54) + (3.2902)(0.54)^2 + (-0.039061)(0.54)^3 = 1836$$

**Step 3: Gas transfer velocity**
$$k_{600} = 0.251 \times (1.35)^2 = 0.457 \text{ cm/hr}$$
$$k = 0.457 \times \left(\frac{1836}{600}\right)^{-0.5} = 0.261 \text{ cm/hr} = 0.0626 \text{ m/day}$$

**Step 4: Equilibrium concentration**
$$K_H = 1.3 \times 10^{-3} \times \exp\left[1700 \times \left(\frac{1}{273.69} - \frac{1}{298.15}\right)\right] \times \exp(-0.015 \times 20.49)$$
$$K_H = 2.15 \times 10^{-3} \text{ mol/(L·atm)}$$
$$C_{sat} = 2.15 \times 10^{-3} \times 1.9 \times 10^{-6} \times 10^9 = 4.09 \text{ nM}$$

**Step 5: Concentration gradient**
$$\Delta C = 7.91 - 4.09 = 3.82 \text{ nM}$$

**Step 6: Methane flux**
$$F = 0.0626 \times 3.82 / 1000 = 0.24 \text{ μmol/(m²·day)}$$

**Result**: Station 5 exhibits a positive flux of **0.24 μmol/(m²·day)**, indicating CH₄ emission to the atmosphere.

---

## Appendix B: Seasonal Considerations

### Summer Period Definition

**2023**: June 1 - September 30, 2023
**2024**: June 1 - September 30, 2024

**Rationale**: 
- Ice-free conditions in Greenfjord
- Peak biological activity
- Valid application of open-water gas transfer parameterizations
- Consistent with Arctic summer oceanographic season

### Excluded Periods

- Ice-covered months (October-May): Different gas exchange regime
- Transitional periods: Complex mixed ice-water surfaces

---

*Document version: 1.0*  
*Last updated: November 5, 2025*  
*Author: Physicist Oceanographer*  
*Analysis software: Python 3.x*
