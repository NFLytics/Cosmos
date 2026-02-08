import numpy as np
import pandas as pd
from scipy.optimize import minimize
import os

def run_unified_ensemble():
    print("Phase 10: Final Unified Ensemble Synthesis")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    galaxies = df['galaxy'].unique()
    
    results = []
    
    # USDM Final Theory: g_sf scaled by local baryonic surface brightness
    def calculate_g_usdm_final(r, cs, sb_ratio):
        # We introduce a non-linear coupling (beta) to baryonic density
        beta = 1.2 
        return (cs**2 / r) * (sb_ratio**beta) * 1e-10

    def obj_func(params, r, v_obs, v_gas, v_disk, v_bul, sb_d):
        # params = [ups_d, ups_b]
        # We lock sound speed at 80 km/s and solve for ML
        v_bar_sq = v_gas**2 + params[0]*v_disk**2 + params[1]*v_bul**2
        g_bar = v_bar_sq / r
        g_obs = v_obs**2 / r
        
        # Scaling superfluid pressure by disk surface brightness proxy
        sb_proxy = np.clip(sb_d / 100.0, 0.1, 2.0)
        g_pred = g_bar + calculate_g_usdm_final(r, 80.0, sb_proxy)
        return np.sum((np.log10(g_obs) - np.log10(g_pred))**2)

    for gal in galaxies:
        sub = df[df['galaxy'] == gal]
        if len(sub) < 10: continue
        
        # Solving for individual ML with locked 80 km/s USDM pressure
        res = minimize(obj_func, [0.5, 0.7], 
                       args=(sub['r_kpc'], sub['v_obs'], sub['v_gas'], sub['v_disk'], sub['v_bulge'], sub['sb_disk']),
                       bounds=[(0.35, 0.65), (0.5, 1.0)])
        
        if res.success:
            results.append({'galaxy': gal, 'ups_d': res.x[0], 'resid': res.fun / len(sub)})

    final_df = pd.DataFrame(results)
    print(f"\nUNIFIED ENSEMBLE RESULTS:")
    print(f"Final ML_Disk Mean: {final_df['ups_d'].mean():.4f}")
    print(f"Final RMS Residual: {final_df['resid'].mean():.6f}")
    print(f"Galaxies Fitted:    {len(final_df)}")
    
    os.makedirs('output', exist_ok=True)
    final_df.to_csv("output/phase10_unified_results.csv", index=False)

if __name__ == '__main__':
    run_unified_ensemble()
