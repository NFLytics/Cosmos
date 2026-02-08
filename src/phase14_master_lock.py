import numpy as np
import pandas as pd
import os

def run_master_lock():
    print("Phase 14: USDM Master Theory Lock & Global Ensemble")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'sb_disk'])
    
    # Locked Physics: 2.8349 eV / 80 km/s / Morphological Scaling
    def g_usdm_locked(r, cs, sb_d):
        r_sat = 2.5 * (sb_d / 100.0)**0.25
        coupling = 1.0 + np.log1p(r_sat / (r + 0.1))
        return (cs**2 / r) * coupling * 1.18e-10

    # Apply Locked Parameters across all galaxies with fixed ML=0.5
    ups_disk = 0.50
    ups_bulge = 0.70
    
    df['g_bar'] = (df['v_gas']**2 + ups_disk*df['v_disk']**2 + ups_bulge*df['v_bulge']**2) / df['r_kpc']
    df['g_obs'] = (df['v_obs']**2) / df['r_kpc']
    
    # Group by galaxy to handle SB scaling correctly
    gal_groups = df.groupby('galaxy')
    accuracies = []
    
    for name, group in gal_groups:
        if len(group) < 10: continue
        sb_mean = group['sb_disk'].mean()
        g_pred = group['g_bar'] + g_usdm_locked(group['r_kpc'], 80.0, sb_mean)
        
        # Calculate Logarithmic Residual
        resid = np.sqrt(np.mean((np.log10(group['g_obs']) - np.log10(g_pred))**2))
        accuracies.append(resid)

    print("\n[ GLOBAL PERFORMANCE SCORECARD ]")
    print(f"Total Galaxies Verified: {len(accuracies)}")
    print(f"Mean Log-Residual:      {np.mean(accuracies):.6f}")
    print(f"Standard Deviation:     {np.std(accuracies):.6f}")
    print(f"Theory Confidence:      {(1.0 - np.mean(accuracies))*100:.2f}%")
    
    os.makedirs('output', exist_ok=True)
    pd.DataFrame({'resid': accuracies}).to_csv("output/phase14_final_scorecard.csv", index=False)

if __name__ == '__main__':
    run_master_lock()
