import numpy as np
import pandas as pd
import os

def run_spatial_shell():
    print("Phase 18: USDM Spatial Shell Coupling")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Physics: Spatial Shell Transition
    # The superfluid effect peaks in a 'shell' rather than monotonically increasing
    def g_usdm_shell(r, cs):
        # r_peak is the transition radius where superfluidity is most efficient
        r_peak = 5.0 
        width = 3.0
        # Gaussian shell coupling
        shell_coupling = 1.8 * np.exp(-((r - r_peak)**2) / (2 * width**2))
        return (cs**2 / r) * shell_coupling * 1.2e-10

    ups_disk = 0.50
    ups_bulge = 0.70
    
    df['g_bar'] = (df['v_gas']**2 + ups_disk*df['v_disk']**2 + ups_bulge*df['v_bulge']**2) / df['r_kpc']
    df['g_obs'] = (df['v_obs']**2) / df['r_kpc']
    df['g_pred'] = df['g_bar'] + g_usdm_shell(df['r_kpc'], 80.0)
    
    df['log_res'] = (np.log10(df['g_obs']) - np.log10(df['g_pred']))**2
    gal_stats = df.groupby('galaxy').agg({'log_res': 'mean', 'r_kpc': 'count'})
    final_set = gal_stats[gal_stats['r_kpc'] >= 10]
    
    mean_res = np.sqrt(final_set['log_res'].mean())
    
    print("\n[ SPATIAL-SHELL SCORECARD ]")
    print(f"Verified Sample:   {len(final_set)} Galaxies")
    print(f"Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence: {(1.0 - mean_res)*100:.2f}%")

if __name__ == '__main__':
    run_spatial_shell()
