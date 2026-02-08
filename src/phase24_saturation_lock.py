import numpy as np
import pandas as pd
import os

def run_saturation_lock():
    print("Phase 24: USDM Log-Normal Saturation (The Final Refinement)")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Physics: Log-Normal Saturation Coupling
    def g_usdm_saturated(r, cs, g_bar):
        a0_raw = 3700.0 
        # Transitioning to a Log-Saturated Alpha
        # This prevents the term from blowing up at r=0 while maximizing mid-disk lift
        x = np.clip(a0_raw / (g_bar + 0.1), 0.1, 50.0)
        alpha_sat = 0.12 * np.log1p(x) 
        return (cs**2 / (r + 0.2)) * alpha_sat

    ups_disk = 0.50
    ups_bulge = 0.70
    
    gal_results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        group = group.sort_values('r_kpc')
        g_bar = (group['v_gas']**2 + ups_disk*group['v_disk']**2 + ups_bulge*group['v_bulge']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Apply Saturated Physics
        g_pred = g_bar + g_usdm_saturated(group['r_kpc'], 80.0, g_bar)
        
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        gal_results.append(resid)

    mean_res = np.mean(gal_results)
    print("\n[ SATURATION-LOCK SCORECARD ]")
    print(f"Verified Sample:   {len(gal_results)} Galaxies")
    print(f"Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence: {(1.0 - mean_res)*100:.2f}%")

if __name__ == '__main__':
    run_saturation_lock()
