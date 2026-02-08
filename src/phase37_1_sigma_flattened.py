import numpy as np
import pandas as pd
import os

def run_sigma_flattened():
    print("Phase 37.1: Flattened Multi-Vector Sigma (σ) Recalibration")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    CS = 80.0
    A0_RAW = 3700.0
    
    all_residuals = []
    
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Physics: Simultaneous EoS + Feedback
        g_limit = (CS**2 / (group['r_kpc'] + 0.1))
        alpha = 0.15 * np.log1p(A0_RAW / (g_bar + 0.5))
        g_usdm_ideal = g_limit * alpha
        feedback_damp = 1.0 / np.sqrt(1.0 + (g_usdm_ideal / (g_bar + 1e-2))**2)
        g_pred = g_bar + (g_usdm_ideal * feedback_damp)
        
        # Flattened Data Extraction
        res = (np.log10(g_obs) - np.log10(g_pred)).values
        all_residuals.extend(res)

    all_residuals = np.array(all_residuals)
    sigma_galactic = np.std(all_residuals)
    
    # Recalibrating Sigma for Cosmic Structure (S8)
    # The variance in galactic Sloshing scales the S8 suppression uncertainty
    sigma_s8 = 0.07 * (sigma_galactic / 0.15) 
    
    print("\n[ FINAL RECALIBRATION SCORECARD ]")
    print(f"Total Points Sampled:   {len(all_residuals)}")
    print(f"Galactic Dispersion (σ): {sigma_galactic:.6f} dex")
    print(f"Structure Variance (σ): {sigma_s8:.6f}")
    print(f"Model Global Accuracy:  {(1.0 - sigma_galactic)*100:.2f}%")
    
    # Save State
    with open("output/sigma_state.json", "w") as f:
        f.write(f'{{"sigma_rar": {sigma_galactic}, "sigma_s8": {sigma_s8}}}')

if __name__ == '__main__':
    run_sigma_flattened()
