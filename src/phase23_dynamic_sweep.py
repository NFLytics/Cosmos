import numpy as np
import pandas as pd
import os

def run_dynamic_sweep():
    print("Phase 23: USDM Dynamic Coupling Sweep (The RAR Bridge)")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Physics: Dynamic Superfluid Coupling
    # alpha scales with the inverse of the baryonic acceleration
    # This mimics the 'Mondian' behavior where the dark force dominates at low g
    def g_usdm_dynamic(r, cs, g_bar):
        # Universal scale for transition (a0 in raw units)
        a0_raw = 3700.0 
        # Non-linear coupling: alpha increases as g_bar drops
        alpha_dyn = 0.08 * (a0_raw / (g_bar + 1.0))**0.15
        return (cs**2 / (r + 0.1)) * alpha_dyn

    ups_disk = 0.50
    ups_bulge = 0.70
    
    gal_results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        group = group.sort_values('r_kpc')
        g_bar = (group['v_gas']**2 + ups_disk*group['v_disk']**2 + ups_bulge*group['v_bulge']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Apply Dynamic Physics
        g_pred = g_bar + g_usdm_dynamic(group['r_kpc'], 80.0, g_bar)
        
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        gal_results.append(resid)

    mean_res = np.mean(gal_results)
    print("\n[ DYNAMIC-SWEEP SCORECARD ]")
    print(f"Verified Sample:   {len(gal_results)} Galaxies")
    print(f"Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence: {(1.0 - mean_res)*100:.2f}%")

if __name__ == '__main__':
    run_dynamic_sweep()
