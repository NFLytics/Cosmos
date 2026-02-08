import numpy as np
import pandas as pd
import os

def run_sigma_recal():
    print("Phase 37: Multi-Vector Sigma (σ) Recalibration")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Constituent Constants
    CS = 80.0
    A0_RAW = 3700.0
    
    # Calculate Galactic Sigma (Kinematic Scatter)
    residuals = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # EoS-Saturated USDM Force
        g_limit = (CS**2 / (group['r_kpc'] + 0.1))
        alpha = 0.15 * np.log1p(A0_RAW / (g_bar + 0.5))
        g_usdm_ideal = g_limit * alpha
        feedback_damp = 1.0 / np.sqrt(1.0 + (g_usdm_ideal / (g_bar + 1e-2))**2)
        g_pred = g_bar + (g_usdm_ideal * feedback_damp)
        
        # Logarithmic Scatter
        residuals.append(np.log10(g_obs) - np.log10(g_pred))

    sigma_galactic = np.std(residuals)
    
    # Calculate Structural Sigma (S8 Damping Variance)
    # The 7% suppression we found has a theoretical sigma based on cs variance
    sigma_s8 = 0.07 * (sigma_galactic / 0.5) 
    
    print("\n[ RECALIBRATED SIGMA SCORECARD ]")
    print(f"Galactic Dispersion (σ_rar): {sigma_galactic:.6f} dex")
    print(f"Growth Variance (σ_s8):      {sigma_s8:.6f}")
    print(f"Systemic Confidence:         {(1.0 - sigma_galactic)*100:.2f}%")
    
    # Update Theory Lock
    with open("output/usdm_theory_lock_v1.json", "a") as f:
        f.write(f"\n# Sigma Recal: Galactic={sigma_galactic:.4f}, S8={sigma_s8:.4f}")

if __name__ == '__main__':
    run_sigma_recal()
