import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# --- USDM GLOBALS ---
M_EV = 2.8349
CS_KMS = 80.0

def calculate_g_usdm(r, cs):
    # Pressure term: g_sf ~ cs^2 / R * f(r)
    # where f(r) is the condensate density profile
    return (cs**2 / r) * 1e-10 

def objective_function(ups, rad, v_obs, v_gas, v_disk, v_bul):
    # ups = [ups_disk, ups_bul]
    v_bar_sq = v_gas**2 + ups[0]*v_disk**2 + ups[1]*v_bul**2
    g_bar = v_bar_sq / rad
    g_obs = v_obs**2 / rad
    g_pred = g_bar + calculate_g_usdm(rad, CS_KMS)
    return np.sum((np.log10(g_obs) - np.log10(g_pred))**2)

def run_ensemble():
    df = pd.read_csv("data/standardized_cosmos_v2.csv")
    galaxies = df['galaxy'].unique()
    ensemble_results = []

    print(f"{'Galaxy':<15} | {'ML_Disk':<10} | {'ML_Bul':<10} | {'Resid':<10}")
    print("-" * 55)

    for gal in galaxies:
        sub = df[df['galaxy'] == gal].dropna(subset=['v_obs', 'v_disk'])
        if len(sub) < 5: continue
        
        # Individual Fit (Tier 1)
        res = minimize(objective_function, [0.5, 0.7], 
                       args=(sub['r_kpc'], sub['v_obs'], sub['v_gas'], sub['v_disk'], sub['v_bulge']),
                       bounds=[(0.3, 0.8), (0.5, 1.5)])
        
        ensemble_results.append({
            'galaxy': gal,
            'ups_d': res.x[0],
            'ups_b': res.x[1],
            'resid': res.fun
        })
        
    final_df = pd.DataFrame(ensemble_results)
    print(f"Ensemble Average ML_Disk: {final_df['ups_d'].mean():.3f}")
    print(f"Ensemble Global Residual:  {final_df['resid'].mean():.4f}")
    final_df.to_csv("output/ensemble_ml_fits.csv", index=False)

if __name__ == '__main__':
    run_ensemble()
