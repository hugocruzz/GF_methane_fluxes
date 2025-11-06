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

# Reference Schmidt number for CO2 at 20°C (used for normalization)
SC_660 = 660

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
        # k660 = 0.251 * u10^2 * (Sc/660)^-0.5  [cm/hr]
        k660 = 0.251 * u10**2
    elif method == 'wanninkhof1992':
        # k660 = 0.31 * u10^2 * (Sc/660)^-0.5  [cm/hr]
        k660 = 0.31 * u10**2
    else:
        raise ValueError("Method must be 'wanninkhof2014' or 'wanninkhof1992'")
    
    # Normalize to actual Schmidt number
    k = k660 * (Sc / SC_660)**(-0.5)
    
    return k


def henry_law_ch4(temperature_celsius, salinity_psu):
    """
    Calculate CH4 solubility in seawater using Wiesenburg & Guinasso (1979) formulation.
    
    This function implements the Bunsen solubility coefficient for methane in seawater,
    accounting for temperature and salinity effects.
    
    Parameters:
    -----------
    temperature_celsius : float or array
        Water temperature [°C]
    salinity_psu : float or array
        Practical salinity [PSU or ppt]
        
    Returns:
    --------
    KH : float or array
        Henry's law constant [mol/(L·atm)]
        Represents the equilibrium concentration of CH4 in water per unit partial pressure
        
    Reference:
    ----------
    Wiesenburg, D.A. and Guinasso, N.L. (1979). Equilibrium solubilities of methane, 
    carbon monoxide, and hydrogen in water and sea water. J. Chem. Eng. Data, 24(4), 356-360.
    
    Physical Validity:
    ------------------
    - Temperature dependence: KH increases with decreasing temperature (higher solubility in cold water)
    - Salinity dependence: KH decreases with increasing salinity (salting-out effect)
    - Typical values at 20°C, S=35 PSU: KH ≈ 1.3 × 10⁻³ mol/(L·atm)
    
    Notes:
    ------
    - Original Wiesenburg & Guinasso equation gives ln(C) where C is in ml(STP) gas / L solution / atm
    - Conversion factor: 1 mole of ideal gas at STP = 22.414 L = 22,414 ml
    - Unit conversion: C [ml(STP)/L/atm] ÷ 22.414 [L/mol] = KH [mol/L/atm]
    - Final units: mol/L/atm (equivalent to M/atm or mol·L⁻¹·atm⁻¹)
    """
    T = temperature_celsius + 273.15  # Convert to Kelvin [K]

    # Coefficients from Wiesenburg & Guinasso (1979), Table IV
    # These apply to ln(C) where C is in ml(STP)/L/atm
    A1, A2, A3 = -68.8862, 101.4956, 28.7314
    B1, B2, B3 = -0.076146, 0.043970, -0.0068672

    # Calculate ln(C) using the empirical formulation
    # Result: ln(C) in units of ml(STP) gas / L solution / atm
    lnC_ml = (A1 +
              A2 * (100.0 / T) +
              A3 * np.log(T / 100.0) +
              salinity_psu *
              (B1 + B2 * (T / 100.0) + B3 * (T / 100.0) ** 2))

    # Convert from ml(STP)/L/atm to mol/L/atm
    # C [ml(STP)/L/atm] × (1000 ml/L) / (22414 ml(STP)/mol) = KH [mol/L/atm]
    # Simplified: C / 22.414 = KH
    KH = np.exp(lnC_ml) * 1000.0 / 22_414.0  # [mol/(L·atm)]
    
    return KH


def calculate_ch4_saturation_concentration(temperature_celsius, salinity_psu, atm_ch4_atm):
    """
    Calculate CH4 equilibrium (saturation) concentration in seawater based on 
    atmospheric partial pressure using Henry's Law.
    
    Henry's Law: C_aq = KH × P_gas
    where C_aq is the dissolved concentration and P_gas is the partial pressure.
    
    Parameters:
    -----------
    temperature_celsius : float or array
        Water temperature [°C]
    salinity_psu : float or array
        Practical salinity [PSU or ppt]
    atm_ch4_atm : float
        Atmospheric CH4 partial pressure [atm]
        (e.g., 1986 ppb = 1986×10⁻⁹ atm)
        
    Returns:
    --------
    C_sat_nM : float or array
        CH4 equilibrium concentration in seawater [nM]
        (nanomolar = nmol/L)
        
    Notes:
    ------
    Unit conversion chain:
    - KH [mol/L/atm] × P [atm] = C [mol/L] 
    - C [mol/L] × 10⁹ [nmol/mol] = C [nmol/L] = C [nM]
    """
    if salinity_psu<0:
        return np.nan
    KH = henry_law_ch4(temperature_celsius, salinity_psu)  # [mol/L/atm]
    C_sat_nM = KH * atm_ch4_atm * 1e9  # [mol/L] → [nM]
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
    # Unit analysis:
    #   k [m/day] × ΔC [nM] = k [m/day] × ΔC [nmol/L]
    #   
    #   Convert: k [m/day] × ΔC [nmol/L] × (1000 L/m³) = nmol/m²/day × 1000
    #          = nmol/m²/day × (L to m³ conversion)
    #   
    #   Result: nmol/m²/day (numerically) = μmol/m²/day (same value!)
    #   
    #   Why? Because 1 nM = 1 nmol/L and the volume conversion (×1000 L/m³)
    #   exactly cancels the unit prefix conversion from nmol to μmol (÷1000)
    #
    # CORRECTED: No division needed - the units work out directly!
    flux_umol_m2_day = k_m_day * delta_C_nM  # [μmol/m²/day]
    
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
    
    # Try different encodings to find the right one
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(filepath, sep=';', decimal=',', encoding=encoding)
            # Check if we got reasonable column names (no � characters)
            if not any('�' in col for col in df.columns):
                print(f"Successfully loaded with {encoding} encoding")
                break
        except:
            continue
    
    # If still not loaded, use latin-1 as fallback
    if df is None:
        df = pd.read_csv(filepath, sep=';', decimal=',', encoding='latin-1')
    
    # Clean up any remaining encoding issues in column names
    df.columns = df.columns.str.replace('�', 'μ')
    df.columns = df.columns.str.replace('ï¿½', 'μ')
    df.columns = df.columns.str.replace('Âµ', 'μ')
    df.columns = df.columns.str.replace('Âº', '°')
    
    # Parse datetime
    df['datetime'] = pd.to_datetime(
        df['dd/mm/yyyy'] + ' ' + df['hh:mm'],
        format='%d/%m/%Y %H:%M:%S'
    )
    
    # Convert numeric columns to proper types (handle comma decimal separator)
    numeric_columns = ['Depth (m)', 'CH4 (nM)', 'CH4 saturation', 'Temperature (μC)', 
                       'Salinity (PSU)', 'NO3NO2 (μM)', 'NO2 (μM)']
    # Also try with ° symbol
    if 'Temperature (°C)' in df.columns:
        numeric_columns.append('Temperature (°C)')
    if 'NO3NO2 (µM)' in df.columns:
        numeric_columns.append('NO3NO2 (µM)')
    if 'NO2 (µM)' in df.columns:
        numeric_columns.append('NO2 (µM)')
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Standardize column names for easier access
    # Map common variations to standard names
    column_mapping = {
        'Temperature (μC)': 'Temperature (°C)',
        'Temperature (Âº C)': 'Temperature (°C)',
        'NO3NO2 (μM)': 'NO3NO2 (µM)',
        'NO2 (μM)': 'NO2 (µM)'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Filter for minimum depth at each station (closest to 2m)
    # Group by station and get row with minimum depth
    df_surface = df.loc[df.groupby('Station')['Depth (m)'].idxmin()]
    
    print(f"\nTotal stations: {len(df_surface)}")
    print(f"Date range: {df_surface['datetime'].min()} to {df_surface['datetime'].max()}")
    print(f"\nSurface depths (m): {df_surface['Depth (m)'].values}")
    print(f"\nColumn names: {list(df_surface.columns)}")
    
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
    
    # Try different encodings to find the right one
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(filepath, sep=';', decimal=',', encoding=encoding)
            # Check if we got reasonable column names (no � characters)
            if not any('�' in col for col in df.columns):
                print(f"Successfully loaded with {encoding} encoding")
                break
        except:
            continue
    
    # If still not loaded, use latin-1 as fallback
    if df is None:
        df = pd.read_csv(filepath, sep=';', decimal=',', encoding='latin-1')
    
    # Clean up any remaining encoding issues in column names
    df.columns = df.columns.str.replace('�', 'μ')
    df.columns = df.columns.str.replace('ï¿½', 'μ')
    df.columns = df.columns.str.replace('Âµ', 'μ')
    df.columns = df.columns.str.replace('Âº', '°')
    
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
    
    # Standardize column names for easier access
    # Map common variations to standard names
    column_mapping = {
        'Temperature (μC)': 'Temperature',
        'Temperature (Âº C)': 'Temperature',
        'NO3+NO2 (μM)': 'NO3+NO2 ',
        'NO2 (μM)': 'NO2 '
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Filter for minimum depth at each station (closest to 2m)
    df_surface = df.loc[df.groupby('Station')['depth '].idxmin()]
    
    print(f"\nTotal stations: {len(df_surface)}")
    print(f"Date range: {df_surface['datetime'].min()} to {df_surface['datetime'].max()}")
    print(f"\nSurface depths (m): {df_surface['depth '].values}")
    print(f"\nColumn names: {list(df_surface.columns)}")
    
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
    
    # Try different encodings to find the right one
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding=encoding)
            # Check if we got reasonable column names (no � characters)
            if not any('�' in col for col in df.columns):
                print(f"Successfully loaded with {encoding} encoding")
                break
        except:
            continue
    
    # If still not loaded, use latin-1 as fallback
    if df is None:
        df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding='latin-1')
    
    # Clean up any remaining encoding issues in column names
    df.columns = df.columns.str.replace('�', 'μ')
    df.columns = df.columns.str.replace('ï¿½', 'μ')
    df.columns = df.columns.str.replace('Âµ', 'μ')
    df.columns = df.columns.str.replace('Âº', '°')
    
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
    
    # Try different encodings to find the right one
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding=encoding)
            # Check if we got reasonable column names (no � characters)
            if not any('�' in col for col in df.columns):
                print(f"Successfully loaded with {encoding} encoding")
                break
        except:
            continue
    
    # If still not loaded, use latin-1 as fallback
    if df is None:
        df = pd.read_csv(filepath, sep=';', skiprows=2, decimal=',', encoding='latin-1')
    
    # Clean up any remaining encoding issues in column names
    df.columns = df.columns.str.replace('�', 'μ')
    df.columns = df.columns.str.replace('ï¿½', 'μ')
    df.columns = df.columns.str.replace('Âµ', 'μ')
    df.columns = df.columns.str.replace('Âº', '°')
    
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
        
        # Skip if depth is too deep (>5m) - not representative of air-sea interface
        if depth > 5.0:
            print(f"  ⚠ Depth ({depth:.2f} m) exceeds 5m threshold - skipping station")
            continue
        
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
        
        # Skip if depth is too deep (>5m) - not representative of air-sea interface
        if depth > 5.0:
            print(f"  ⚠ Depth ({depth:.2f} m) exceeds 5m threshold - skipping station")
            continue
        
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
            'Flux_umol_m2_day': flux.astype(float),
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
