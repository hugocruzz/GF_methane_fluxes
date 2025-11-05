"""
Methane Flux Calculation Script
=================================

This script calculates methane fluxes from surface water to the atmosphere
for Greenfjord stations in 2023 and 2024.

Methodology:
1. Extract CH4 concentrations and saturation data at minimum depth (2m) for each station
2. Match each station's sampling time with corresponding wind speed data from weather stations
3. Calculate gas transfer velocity (k) using wind speed with Wanninkhof (2014) parameterization
4. Compute methane flux using: F = k × (CH4_measured - CH4_equilibrium)
   where CH4_measured is the concentration in water and CH4_equilibrium is calculated
   using atmospheric CH4 measurements from Storhofdi, Iceland

Key methodology points:
- Atmospheric CH4: Measured at Storhofdi, Iceland (63.400°N, 20.288°W)
  * 2023: 1986.65 ppb (June-Sept average, n=4)
  * 2024: 1995.85 ppb (June-Sept average, n=4)
- Wind speed correction: Power law U10 = U_z * (10/z)^α with α=0.20 (rural-suburban)
- Schmidt number: Temperature and salinity dependent (Vogt et al. 2023)
- Gas transfer velocity: k = 0.251 * U10² * (Sc/660)^-0.5 (Wanninkhof 2014)
- Solubility: Wiesenburg & Guinasso (1979) with temperature and salinity corrections

References:
- Wanninkhof (2014), Limnology and Oceanography: Methods
- Wiesenburg & Guinasso (1979), J. Chem. Eng. Data
- Vogt et al. (2023), Jähne et al. (1987), Manning & Nicholson (2022)

Author: Physicist Oceanographer
Date: November 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTS
# ============================================================================

# Schmidt number for CH4 in seawater (at 20°C, typical reference)
# Sc varies with temperature: Sc = A + B*T + C*T^2 + D*T^3
# For CH4: coefficients from Wanninkhof (2014)
SC_A = 1897.8
SC_B = -114.28
SC_C = 3.2902
SC_D = -0.039061

# Reference Schmidt number for normalization
SC_600 = 600

# Henry's law constant for CH4 (mol/L/atm) at 25°C
# Temperature dependent: KH = KH0 * exp[d(ln(KH))/d(1/T) * (1/T - 1/T0)]
KH_25C = 1.3e-3  # mol/(L·atm)
D_LN_KH_DT = 1700  # K (temperature dependence)

# Atmospheric CH4 concentration (measured at Storhofdi, Iceland)
# 2023: June-Sept average = 1986.65 ppb (n=4)
# 2024: June-Sept average = 1995.85 ppb (n=4)
ATM_CH4_2023_PPB = 1986.65  # ppb
ATM_CH4_2024_PPB = 1995.85  # ppb
ATM_CH4_2023_ATM = ATM_CH4_2023_PPB / 1e9  # convert ppb to atm
ATM_CH4_2024_ATM = ATM_CH4_2024_PPB / 1e9  # convert ppb to atm

# Standard atmospheric pressure
ATM_PRESSURE = 1.0  # atm (approximately)

# Measurement height correction factor (from measurement height to 10m standard)
# Wind speed typically measured at different heights needs correction

# ============================================================================
# FUNCTIONS
# ============================================================================

def schmidt_number(temperature_celsius, salinity_psu):
    """
    Calculate Schmidt number for CH4 in seawater as a function of temperature and salinity.
    
    Parameters:
    -----------
    temperature_celsius : float or array
        Water temperature in degrees Celsius
    salinity_psu : float or array
        Salinity (PSU)
        
    Returns:
    --------
    Sc : float or array
        Schmidt number (dimensionless)
    
    Reference:
    ----------
    Vogt et al. (2023) with salinity correction from Jähne et al. (1987) 
    and Manning & Nicholson (2022)
    Base coefficients from Wanninkhof (2014)
    """
    T = temperature_celsius
    # Base Schmidt number for freshwater
    Sc_fresh = SC_A + SC_B * T + SC_C * T**2 + SC_D * T**3
    
    # Salinity correction factor (Jähne et al., 1987)
    # Sc increases with salinity due to increased viscosity
    salinity_correction = 1.0 + 0.0085 * salinity_psu
    
    Sc = Sc_fresh * salinity_correction
    return Sc


def wind_speed_correction(u_measured, z_measured=6.75, z_target=10.0, alpha=0.20):
    """
    Correct wind speed from measurement height to standard 10m height.
    Uses power law profile for rural-suburban conditions.
    
    Parameters:
    -----------
    u_measured : float or array
        Wind speed at measurement height (m/s)
    z_measured : float
        Measurement height (m), default 6.75m (Narsaq station height)
    z_target : float
        Target height (m), default 10m (standard)
    alpha : float
        Power law exponent (default 0.20 for relatively rough surface/rural-suburban area)
        
    Returns:
    --------
    u_10 : float or array
        Wind speed at 10m height (m/s)
        
    Reference:
    ----------
    Power law profile: U10 = U_z * (10/z)^alpha
    Alpha = 0.20 for rural-suburban area (relatively rough surface)
    """
    u_10 = u_measured * (z_target / z_measured)**alpha
    return u_10


def gas_transfer_velocity_wanninkhof(u10, Sc, method='wanninkhof2014'):
    """
    Calculate gas transfer velocity using Wanninkhof relationships.
    
    Parameters:
    -----------
    u10 : float or array
        Wind speed at 10m height (m/s)
    Sc : float or array
        Schmidt number (dimensionless)
    method : str
        'wanninkhof2014' (default) or 'wanninkhof1992'
        
    Returns:
    --------
    k : float or array
        Gas transfer velocity (cm/hr)
        
    Reference:
    ----------
    Wanninkhof, R. (2014). Relationship between wind speed and gas exchange 
    over the ocean revisited. Limnology and Oceanography: Methods, 12(6), 351-362.
    """
    if method == 'wanninkhof2014':
        # k600 = 0.251 * u10^2 * (Sc/600)^-0.5  [cm/hr]
        k600 = 0.251 * u10**2
    elif method == 'wanninkhof1992':
        # k600 = 0.31 * u10^2 * (Sc/600)^-0.5  [cm/hr]
        k600 = 0.31 * u10**2
    else:
        raise ValueError("Method must be 'wanninkhof2014' or 'wanninkhof1992'")
    
    # Normalize to actual Schmidt number
    k = k600 * (Sc / SC_600)**(-0.5)
    
    return k


def henry_law_ch4(temperature_celsius, salinity_psu):
    """
    Calculate Henry's law constant for CH4 in seawater.
    
    Parameters:
    -----------
    temperature_celsius : float or array
        Water temperature (°C)
    salinity_psu : float or array
        Salinity (PSU)
        
    Returns:
    --------
    KH : float or array
        Henry's law constant (mol/(L·atm))
        
    Reference:
    ----------
    Wiesenburg & Guinasso (1979) with salinity correction
    """
    T_kelvin = temperature_celsius + 273.15
    T0_kelvin = 298.15  # 25°C reference
    
    # Temperature dependence
    KH = KH_25C * np.exp(D_LN_KH_DT * (1/T_kelvin - 1/T0_kelvin))
    
    # Salinity correction (empirical)
    # KH(S) = KH(0) * exp(-S * correction_factor)
    salinity_correction = np.exp(-0.0150 * salinity_psu)
    KH = KH * salinity_correction
    
    return KH


def calculate_ch4_saturation_concentration(temperature_celsius, salinity_psu, 
                                           atm_ch4_atm):
    """
    Calculate CH4 concentration at equilibrium with atmosphere.
    
    Parameters:
    -----------
    temperature_celsius : float or array
        Water temperature (°C)
    salinity_psu : float or array
        Salinity (PSU)
    atm_ch4_atm : float
        Atmospheric CH4 partial pressure (atm)
        
    Returns:
    --------
    C_sat : float or array
        Saturation concentration (nmol/L or nM)
    """
    KH = henry_law_ch4(temperature_celsius, salinity_psu)
    # C = KH * P, convert from mol/L to nmol/L
    C_sat_nM = KH * atm_ch4_atm * 1e9
    return C_sat_nM


def calculate_methane_flux(C_water_nM, temperature_celsius, salinity_psu, 
                          u10_ms, atm_ch4_atm, atm_ch4_ppb):
    """
    Calculate methane flux from water to atmosphere.
    
    Parameters:
    -----------
    C_water_nM : float or array
        CH4 concentration in surface water (nM or nmol/L)
    temperature_celsius : float or array
        Water temperature (°C)
    salinity_psu : float or array
        Salinity (PSU)
    u10_ms : float or array
        Wind speed at 10m (m/s)
    atm_ch4_atm : float
        Atmospheric CH4 partial pressure (atm)
    atm_ch4_ppb : float
        Atmospheric CH4 concentration (ppb) for output
        
    Returns:
    --------
    flux : float or array
        CH4 flux (μmol/m²/day), positive = sea to air
    C_sat_nM : float
        Saturation concentration (nM)
    delta_C_nM : float
        Concentration gradient (nM)
    k_cm_hr : float
        Gas transfer velocity (cm/hr)
    Sc : float
        Schmidt number
    atm_ch4_ppb : float
        Atmospheric CH4 concentration (ppb)
    """
    # Calculate saturation concentration
    C_sat_nM = calculate_ch4_saturation_concentration(
        temperature_celsius, salinity_psu, atm_ch4_atm
    )
    
    # Calculate concentration gradient (water - air equilibrium)
    print(f"Saturation concentration in water : {C_sat_nM} nM")
    delta_C_nM = C_water_nM - C_sat_nM
    
    # Calculate Schmidt number with salinity correction
    Sc = schmidt_number(temperature_celsius, salinity_psu)
    
    # Calculate gas transfer velocity (cm/hr)
    k_cm_hr = gas_transfer_velocity_wanninkhof(u10_ms, Sc)
    
    # Convert k to m/day: (cm/hr) * (1 m/100 cm) * (24 hr/day)
    k_m_day = k_cm_hr * 0.01 * 24
    
    # Calculate flux: F = k * ΔC
    # ΔC in nM (nmol/L), k in m/day
    # F = k (m/day) * ΔC (nmol/L) = nmol/(m²·day)
    # Convert to μmol/(m²·day): divide by 1000
    flux_umol_m2_day = k_m_day * delta_C_nM / 1000
    
    return flux_umol_m2_day, C_sat_nM, delta_C_nM, k_cm_hr, Sc, atm_ch4_ppb


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_gf2023_data(filepath):
    """
    Load 2023 Greenfjord CH4 data.
    
    Parameters:
    -----------
    filepath : str
        Path to GF2023.csv file
        
    Returns:
    --------
    df : DataFrame
        Cleaned and processed data
    """
    print("\n" + "="*70)
    print("LOADING 2023 DATA")
    print("="*70)
    
    # Read CSV with semicolon delimiter and proper encoding
    df = pd.read_csv(filepath, sep=';', decimal=',', encoding='latin-1')
    
    # Parse datetime
    df['datetime'] = pd.to_datetime(
        df['dd/mm/yyyy'] + ' ' + df['hh:mm'],
        format='%d/%m/%Y %H:%M:%S'
    )
    
    # Convert numeric columns to proper types (handle comma decimal separator)
    numeric_columns = ['Depth (m)', 'CH4 (nM)', 'CH4 saturation', 'Temperature (°C)', 
                       'Salinity (PSU)', 'NO3NO2 (µM)', 'NO2 (µM)']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter for minimum depth at each station (closest to 2m)
    # Group by station and get row with minimum depth
    df_surface = df.loc[df.groupby('Station')['Depth (m)'].idxmin()]
    
    print(f"\nTotal stations: {len(df_surface)}")
    print(f"Date range: {df_surface['datetime'].min()} to {df_surface['datetime'].max()}")
    print(f"\nSurface depths (m): {df_surface['Depth (m)'].values}")
    
    return df_surface


def load_gf2024_data(filepath):
    """
    Load 2024 Greenfjord CH4 data.
    
    Parameters:
    -----------
    filepath : str
        Path to GF2024.csv file
        
    Returns:
    --------
    df : DataFrame
        Cleaned and processed data
    """
    print("\n" + "="*70)
    print("LOADING 2024 DATA")
    print("="*70)
    
    # Read CSV with semicolon delimiter
    df = pd.read_csv(filepath, sep=';', decimal=',', encoding='latin-1')
    #drop first line
    df = df.drop(index=0).reset_index(drop=True)
    # Parse datetime
    df['datetime'] = pd.to_datetime(
        df['dd/mm/yyy'] + ' ' + df['hh:mm'],
        format='%d/%m/%Y %H:%M:%S'
    )
    
    # Convert numeric columns to proper types (handle comma decimal separator)
    numeric_columns = ['depth ', 'CH4', 'CH4 saturation', 'Temperature', 'Salinity', 
                       'NO3+NO2 ', 'NO2 ', 'PO4 ', 'Si(OH)4  ']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter for minimum depth at each station (closest to 2m)
    df_surface = df.loc[df.groupby('Station')['depth '].idxmin()]
    
    print(f"\nTotal stations: {len(df_surface)}")
    print(f"Date range: {df_surface['datetime'].min()} to {df_surface['datetime'].max()}")
    print(f"\nSurface depths (m): {df_surface['depth '].values}")
    
    return df_surface


def load_weather_narsaq_2023(filepath):
    """
    Load Narsaq weather station data for 2023.
    
    Parameters:
    -----------
    filepath : str
        Path to weather station CSV file
        
    Returns:
    --------
    df : DataFrame
        Weather data with datetime index
    """
    print("\n" + "="*70)
    print("LOADING NARSAQ WEATHER STATION DATA (2023)")
    print("="*70)
    # Skip the header rows (first 2 rows are empty or header)
    df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding='latin-1')
    #Drop first line
    df = df.drop(index=0).reset_index(drop=True)
    # Parse datetime
    df['datetime'] = pd.to_datetime(df['Timestamps'], format='%m/%d/%Y %I:%M:%S %p')
    
    # Filter for summer months (June to September)
    df = df[(df['datetime'].dt.month >= 6) & (df['datetime'].dt.month <= 9)]
    
    # Filter for year 2023
    df = df[df['datetime'].dt.year == 2023]
    
    print(f"\nTotal records: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Wind speed range: {df[' m/s Wind Speed'].min():.2f} - {df[' m/s Wind Speed'].max():.2f} m/s")
    
    return df


def load_weather_forel_2024(filepath):
    """
    Load Forel (boat) weather station data for 2024.
    
    Parameters:
    -----------
    filepath : str
        Path to weather station CSV file
        
    Returns:
    --------
    df : DataFrame
        Weather data with datetime index
    """
    print("\n" + "="*70)
    print("LOADING FOREL WEATHER STATION DATA (2024)")
    print("="*70)
    
    # Skip the header rows
    df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding='latin-1')
    #Drop first line
    df = df.drop(index=0).reset_index(drop=True)
    # Parse datetime
    df['datetime'] = pd.to_datetime(df['Timestamps'], format='%m/%d/%Y %I:%M:%S %p')
    
    # Filter for summer months (June to September)
    df = df[(df['datetime'].dt.month >= 6) & (df['datetime'].dt.month <= 9)]
    
    # Filter for year 2024
    df = df[df['datetime'].dt.year == 2024]
    
    print(f"\nTotal records: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Wind speed range: {df[' m/s Wind Speed'].min():.2f} - {df[' m/s Wind Speed'].max():.2f} m/s")
    
    return df


def match_wind_speed(station_datetime, weather_df, window_hours=24):
    """
    Match station sampling time with weather station wind speed.
    Uses average wind speed over a specified time window before sampling.
    
    Parameters:
    -----------
    station_datetime : datetime
        Station sampling datetime
    weather_df : DataFrame
        Weather station data
    window_hours : float
        Time window for averaging (hours before sampling)
        
    Returns:
    --------
    wind_speed : float
        Average wind speed (m/s)
    n_records : int
        Number of weather records used in average
    """
    # Define time window
    end_time = station_datetime
    start_time = station_datetime - timedelta(hours=window_hours)
    
    # Filter weather data within window
    mask = (weather_df['datetime'] >= start_time) & (weather_df['datetime'] <= end_time)
    wind_data = weather_df.loc[mask, ' m/s Wind Speed']
    
    if len(wind_data) > 0:
        return wind_data.mean(), len(wind_data)
    else:
        return np.nan, 0


# ============================================================================
# MAIN FLUX CALCULATION
# ============================================================================

def calculate_fluxes_2023():
    """
    Calculate methane fluxes for all 2023 stations.
    """
    print("\n" + "#"*70)
    print("# METHANE FLUX CALCULATION - 2023")
    print("#"*70)
    
    # Load data
    gf2023 = load_gf2023_data('GF2023.csv')
    weather_2023 = load_weather_narsaq_2023('GF2023_weather_station_Nordasq.csv')
    
    # Prepare results dataframe
    results = []
    
    print("\n" + "="*70)
    print("CALCULATING FLUXES FOR EACH STATION")
    print("="*70)
    
    for idx, row in gf2023.iterrows():
        station = row['Station']
        datetime_sample = row['datetime']
        depth = row['Depth (m)']
        ch4_nM = row['CH4 (nM)']
        ch4_sat_pct = row['CH4 saturation']
        temp_C = row['Temperature (°C)']
        salinity_psu = row['Salinity (PSU)']
        
        print(f"\n{'='*70}")
        print(f"Station {station} - {datetime_sample}")
        print(f"{'='*70}")
        print(f"  Depth: {depth:.2f} m")
        print(f"  CH4 concentration: {ch4_nM:.2f} nM")
        print(f"  CH4 saturation: {ch4_sat_pct:.1f} %")
        print(f"  Temperature: {temp_C:.2f} °C")
        print(f"  Salinity: {salinity_psu:.2f} PSU")
        
        # Skip if CH4 data is missing
        if pd.isna(ch4_nM) or pd.isna(temp_C) or pd.isna(salinity_psu):
            print("  ⚠ Missing data - skipping station")
            continue
        
        # Match wind speed (24-hour average before sampling)
        wind_speed_raw, n_records = match_wind_speed(datetime_sample, weather_2023, window_hours=24)
        
        if pd.isna(wind_speed_raw) or n_records == 0:
            print(f"  ⚠ No wind speed data available - skipping station")
            continue
        
        print(f"  Wind speed (raw, ~6.75m height Narsaq): {wind_speed_raw:.2f} m/s (avg of {n_records} records)")
        
        # Correct wind speed to 10m height using power law (alpha=0.20)
        wind_speed_10m = wind_speed_correction(wind_speed_raw, z_measured=6.75, z_target=10.0, alpha=0.20)
        print(f"  Wind speed (corrected to 10m): {wind_speed_10m:.2f} m/s")
        print(f"  Atmospheric CH4: {ATM_CH4_2023_PPB:.2f} ppb")
        
        # Calculate flux
        flux, C_sat, delta_C, k, Sc, atm_ch4_output = calculate_methane_flux(
            ch4_nM, temp_C, salinity_psu, wind_speed_10m, ATM_CH4_2023_ATM, ATM_CH4_2023_PPB
        )
        
        print(f"\n  FLUX CALCULATION RESULTS:")
        print(f"  -------------------------")
        print(f"  Schmidt number: {Sc:.1f}")
        print(f"  Gas transfer velocity (k): {k:.2f} cm/hr")
        print(f"  Saturation concentration (C_sat): {C_sat:.2f} nM")
        print(f"  Concentration gradient (ΔC): {delta_C:.2f} nM")
        print(f"  METHANE FLUX: {flux:.2f} μmol/m²/day")
        
        # Store results
        results.append({
            'Station': station,
            'Datetime': datetime_sample,
            'Depth_m': depth,
            'CH4_nM': ch4_nM,
            'CH4_saturation_pct': ch4_sat_pct,
            'CH4_air_ppb': atm_ch4_output,
            'Temperature_C': temp_C,
            'Salinity_PSU': salinity_psu,
            'WindSpeed_raw_ms': wind_speed_raw,
            'WindSpeed_10m_ms': wind_speed_10m,
            'Schmidt_number': Sc,
            'k_cm_hr': k,
            'C_sat_nM': C_sat,
            'Delta_C_nM': delta_C,
            'Flux_umol_m2_day': flux,
            'N_wind_records': n_records
        })
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS - 2023")
    print("="*70)
    print(f"\nNumber of stations with flux calculations: {len(results_df)}")
    print(f"\nMethane flux statistics (μmol/m²/day):")
    print(f"  Mean: {results_df['Flux_umol_m2_day'].mean():.2f}")
    print(f"  Median: {results_df['Flux_umol_m2_day'].median():.2f}")
    print(f"  Std: {results_df['Flux_umol_m2_day'].std():.2f}")
    print(f"  Min: {results_df['Flux_umol_m2_day'].min():.2f}")
    print(f"  Max: {results_df['Flux_umol_m2_day'].max():.2f}")
    
    # Save results
    results_df.to_csv('methane_flux_2023.csv', index=False)
    print(f"\nResults saved to: methane_flux_2023.csv")
    
    return results_df


def calculate_fluxes_2024():
    """
    Calculate methane fluxes for all 2024 stations.
    """
    print("\n" + "#"*70)
    print("# METHANE FLUX CALCULATION - 2024")
    print("#"*70)
    
    # Load data
    gf2024 = load_gf2024_data('GF2024.csv')
    weather_2024 = load_weather_forel_2024('GF2024_weather_station_forel.csv')
    
    # Prepare results dataframe
    results = []
    
    print("\n" + "="*70)
    print("CALCULATING FLUXES FOR EACH STATION")
    print("="*70)
    
    for idx, row in gf2024.iterrows():
        station = row['Station']
        datetime_sample = row['datetime']
        depth = row['depth ']
        ch4_nM = row['CH4']
        ch4_sat_pct = row['CH4 saturation']
        temp_C = row['Temperature']
        salinity_psu = row['Salinity']
        
        print(f"\n{'='*70}")
        print(f"Station {station} - {datetime_sample}")
        print(f"{'='*70}")
        print(f"  Depth: {depth:.2f} m")
        print(f"  CH4 concentration: {ch4_nM:.2f} nM")
        print(f"  CH4 saturation: {ch4_sat_pct:.1f} %")
        print(f"  Temperature: {temp_C:.2f} °C")
        print(f"  Salinity: {salinity_psu:.2f} PSU")
        
        # Skip if CH4 data is missing
        if pd.isna(ch4_nM) or pd.isna(temp_C) or pd.isna(salinity_psu):
            print("  ⚠ Missing data - skipping station")
            continue
        
        # Match wind speed (24-hour average before sampling)
        wind_speed_raw, n_records = match_wind_speed(datetime_sample, weather_2024, window_hours=24)
        
        if pd.isna(wind_speed_raw) or n_records == 0:
            print(f"  ⚠ No wind speed data available - skipping station")
            continue
        
        print(f"  Wind speed (raw, ~6.75m height Narsaq): {wind_speed_raw:.2f} m/s (avg of {n_records} records)")
        
        # Correct wind speed to 10m height using power law (alpha=0.20)
        wind_speed_10m = wind_speed_correction(wind_speed_raw, z_measured=6.75, z_target=10.0, alpha=0.20)
        print(f"  Wind speed (corrected to 10m): {wind_speed_10m:.2f} m/s")
        print(f"  Atmospheric CH4: {ATM_CH4_2024_PPB:.2f} ppb")
        
        # Calculate flux
        flux, C_sat, delta_C, k, Sc, atm_ch4_output = calculate_methane_flux(
            ch4_nM, temp_C, salinity_psu, wind_speed_10m, ATM_CH4_2024_ATM, ATM_CH4_2024_PPB
        )
        
        print(f"\n  FLUX CALCULATION RESULTS:")
        print(f"  -------------------------")
        print(f"  Schmidt number: {Sc:.1f}")
        print(f"  Gas transfer velocity (k): {k:.2f} cm/hr")
        print(f"  Saturation concentration (C_sat): {C_sat:.2f} nM")
        print(f"  Concentration gradient (ΔC): {delta_C:.2f} nM")
        print(f"  METHANE FLUX: {flux:.2f} μmol/m²/day")
        
        # Store results
        results.append({
            'Station': station,
            'Datetime': datetime_sample,
            'Depth_m': depth,
            'CH4_nM': ch4_nM,
            'CH4_saturation_pct': ch4_sat_pct,
            'CH4_air_ppb': atm_ch4_output,
            'Temperature_C': temp_C,
            'Salinity_PSU': salinity_psu,
            'WindSpeed_raw_ms': wind_speed_raw,
            'WindSpeed_10m_ms': wind_speed_10m,
            'Schmidt_number': Sc,
            'k_cm_hr': k,
            'C_sat_nM': C_sat,
            'Delta_C_nM': delta_C,
            'Flux_umol_m2_day': flux,
            'N_wind_records': n_records
        })
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS - 2024")
    print("="*70)
    print(f"\nNumber of stations with flux calculations: {len(results_df)}")
    print(f"\nMethane flux statistics (μmol/m²/day):")
    print(f"  Mean: {results_df['Flux_umol_m2_day'].mean():.2f}")
    print(f"  Median: {results_df['Flux_umol_m2_day'].median():.2f}")
    print(f"  Std: {results_df['Flux_umol_m2_day'].std():.2f}")
    print(f"  Min: {results_df['Flux_umol_m2_day'].min():.2f}")
    print(f"  Max: {results_df['Flux_umol_m2_day'].max():.2f}")
    
    # Save results
    results_df.to_csv('methane_flux_2024.csv', index=False)
    print(f"\nResults saved to: methane_flux_2024.csv")
    
    return results_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("="*70)
    print(" METHANE FLUX CALCULATION FOR GREENFJORD STATIONS")
    print(" 2023 and 2024 Summer Data")
    print("="*70)
    print("\nMethodology: Wanninkhof (2014) gas transfer velocity")
    print("Wind speed: Power law correction U10 = U_z * (10/z)^0.20")
    print("Atmospheric CH4: Measured at Storhofdi, Iceland")
    print("  - 2023: 1986.65 ppb")
    print("  - 2024: 1995.85 ppb")
    print("24-hour average wind speed before each station sampling")
    print("Schmidt number with salinity correction (Vogt et al. 2023)")
    print("="*70)
    
    # Calculate fluxes for 2023
    results_2023 = calculate_fluxes_2023()


    # Calculate fluxes for 2024
    results_2024 = calculate_fluxes_2024()

    
    # Final summary
    print("\n" + "="*70)
    print("CALCULATION COMPLETE")
    print("="*70)
    if results_2023 is not None:
        print(f"✓ 2023: {len(results_2023)} stations processed")
    if results_2024 is not None:
        print(f"✓ 2024: {len(results_2024)} stations processed")
    print("\nOutput files created:")
    print("  - methane_flux_2023.csv")
    print("  - methane_flux_2024.csv")
    print("="*70)
