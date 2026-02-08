import numpy as np
import pandas as pd
import os

def run_potential_sync():
    print("Phase 15: USDM Gravitational Potential Deep-Sync")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'sb_disk'])
    
    # Enhanced Physics: Power-law coupling to the local baryonic acceleration scale
    # This ensures the superfluid 'lift' is strongest where the M/L tension is highest.
    def g_usdm_sync(r, cs, g_bar):
        # lambda scales with the local potential depth relative to the a0 scale
        a0 = 1.2e-10
        lambda_coupling = 1.45 * (np.clip(g_bar / a0, 0.1, 10.0))**0.25
        r_sat = 3.0 
        coupling = 1.0 + np.log1p(r_sat / (r + 0.1))
        return (cs**2 / r) * coupling * lambda_coupling * a0

    ups_disk = 0.50
    ups_bulge = 0.70
    
    df['g_bar'] = (df['v_gas']**2 + ups_disk*df['v_disk']**2 + ups_bulge*df['v_bulge']**2) / df['r_kpc']
    df['g_obs'] = (df['v_obs']**2) / df['r_kpc']
    
    gal_groups = df.groupby('galaxy')
    accuracies = []
    
    for name, group in gal_groups:
        if len(group) < 10: continue
        # Apply the potential-sync coupling
        g_pred = group['g_bar'] + g_usdm_sync(group['r_kpc'], 80.0, group['g_bar'])
        
        # Calculate Logarithmic Residual
        resid = np.sqrt(np.mean((np.log10(group['g_obs']) - np.log10(g_pred))**2))
        accuracies.append(resid)

    print("\n[ DEEP-SYNC PERFORMANCE SCORECARD ]")
    print(f"Total Galaxies Verified: {len(accuracies)}")
    print(f"Mean Log-Residual:      {np.mean(accuracies):.6f}")
    print(f"Theory Confidence:      {(1.0 - np.mean(accuracies))*100:.2f}%")
    
    os.makedirs('output', exist_ok=True)
    pd.DataFrame({'resid': accuracies}).to_csv("output/phase15_sync_results.csv", index=False)

if __name__ == '__main__':
    run_potential_sync()
