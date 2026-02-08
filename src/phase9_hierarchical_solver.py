import numpy as np
import pandas as pd
from scipy.optimize import minimize
import os

def run_hierarchical_fit():
    print("Phase 9: Hierarchical Ensemble Refinement")
    df = pd.read_csv("data/standardized_cosmos_v2.csv")
    
    # Filter for galaxies with full vector sets
    df = df.dropna(subset=['r_kpc', 'v_obs', 'v_gas', 'v_disk'])
    galaxies = df['galaxy'].unique()
    
    results = []
    
    # Global Constant for Superfluid coupling
    # We will now allow the sound speed to have a slight radial dependence: cs(r)
    def calculate_g_usdm_dynamic(r, cs, rho_ratio):
        # USDM core pressure scaled by local density ratio
        return (cs**2 / r) * (1.0 + np.exp(-r/5.0)) * 1e-10

    def obj_func(params, r, v_obs, v_gas, v_disk, v_bul):
        # params = [ups_d, ups_b, local_cs_mod]
        v_bar_sq = v_gas**2 + params[0]*v_disk**2 + params[1]*v_bul**2
        g_bar = v_bar_sq / r
        g_obs = v_obs**2 / r
        
        # Enhanced USDM term
        g_pred = g_bar + calculate_g_usdm_dynamic(r, 80.0 * params[2], 0.05)
        return np.sum((np.log10(g_obs) - np.log10(g_pred))**2)

    for gal in galaxies:
        sub = df[df['galaxy'] == gal]
        if len(sub) < 8: continue
        
        # We allow a local 10% variance in effective sound speed (local thermal variations)
        res = minimize(obj_func, [0.5, 0.7, 1.0], 
                       args=(sub['r_kpc'], sub['v_obs'], sub['v_gas'], sub['v_disk'], sub['v_bulge']),
                       bounds=[(0.3, 0.7), (0.5, 1.2), (0.9, 1.1)])
        
        if res.success:
            results.append({
                'galaxy': gal,
                'ups_d': res.x[0],
                'resid': res.fun / len(sub) # Normalized residual
            })

    final_df = pd.DataFrame(results)
    print(f"\nREFINED METRICS:")
    print(f"Target ML_Disk:    0.500")
    print(f"Achieved ML_Disk:  {final_df['ups_d'].mean():.4f}")
    print(f"Reduced Residual:  {final_df['resid'].mean():.6f}")
    
    os.makedirs('output', exist_ok=True)
    final_df.to_csv("output/phase9_refined_ensemble.csv", index=False)

if __name__ == '__main__':
    run_hierarchical_fit()
