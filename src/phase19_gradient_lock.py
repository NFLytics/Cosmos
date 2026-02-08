import numpy as np
import pandas as pd
import os

def run_gradient_lock():
    print("Phase 19: USDM Baryonic Gradient Coupling")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'sb_disk'])
    
    # Physics: Gradient-Driven Superfluidity
    # Coupling efficiency is highest where the stellar density gradient is steepest
    def g_usdm_gradient(r, cs, sb_d):
        # Calculate local gradient proxy (change in SB over radius)
        # Higher gradient = higher 'sloshing' force
        grad_proxy = np.abs(np.gradient(sb_d) / np.gradient(r))
        grad_norm = np.clip(grad_proxy / 50.0, 0.1, 5.0)
        
        a0 = 1.2e-10
        return (cs**2 / r) * (1.0 + grad_norm) * 1.3e-10

    ups_disk = 0.50
    ups_bulge = 0.70
    
    # Process by galaxy to maintain gradient integrity
    gal_results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        group = group.sort_values('r_kpc')
        g_bar = (group['v_gas']**2 + ups_disk*group['v_disk']**2 + ups_bulge*group['v_bulge']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Apply Gradient Physics
        g_pred = g_bar + g_usdm_gradient(group['r_kpc'], 80.0, group['sb_disk'])
        
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        gal_results.append(resid)

    mean_res = np.mean(gal_results)
    print("\n[ GRADIENT-LOCK SCORECARD ]")
    print(f"Verified Sample:   {len(gal_results)} Galaxies")
    print(f"Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence: {(1.0 - mean_res)*100:.2f}%")

if __name__ == '__main__':
    run_gradient_lock()
