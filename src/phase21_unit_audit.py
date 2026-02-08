import numpy as np
import pandas as pd

def run_unit_audit():
    print("Phase 21: Data Scale & Unit Integrity Audit")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Check first galaxy
    sample = df[df['galaxy'] == df['galaxy'].unique()[0]].head(5)
    
    # Constants
    ups_disk = 0.5
    # Conversion: (km/s)^2 / kpc to m/s^2 is approx 3.24e-14, 
    # but often kept in natural units. Let's see the raw magnitudes.
    
    r = sample['r_kpc'].values
    v_obs = sample['v_obs'].values
    v_bar_sq = (sample['v_gas']**2 + ups_disk*sample['v_disk']**2).values
    
    g_obs = (v_obs**2) / r
    g_bar = v_bar_sq / r
    
    print(f"\nGalaxy: {sample['galaxy'].iloc[0]}")
    print(f"Radius (kpc): {r}")
    print(f"V_obs (km/s): {v_obs}")
    print(f"g_obs (raw):  {g_obs}")
    print(f"g_bar (raw):  {g_bar}")
    print(f"Ratio (obs/bar): {g_obs/g_bar}")
    
    # Test a standard USDM term magnitude
    g_usdm_test = (80.0**2 / r) * 1e-10
    print(f"g_usdm (test): {g_usdm_test}")

if __name__ == '__main__':
    run_unit_audit()
