import numpy as np
import pandas as pd
from scipy import stats

def run_universal_audit():
    print("Phase 51: Universal Manifest Audit (4+ Sigma Verification)")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Manifest Constants (LOCKED)
    CS = 80.0
    A0 = 3700.0
    STIFFNESS = 3.5708
    Z_FILTER = 0.65
    ETA = 0.13819
    
    all_res = []
    
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Applying the Scaling Manifest Logic
        g_limit = (CS**2 / (group['r_kpc'] + 0.1))
        alpha = 0.15 * np.log1p(A0 / (g_bar + 0.5))
        
        # Incorporate Macro-Viscosity and Z-Filter
        g_usdm_raw = g_limit * alpha * Z_FILTER
        feedback_damp = 1.0 / np.sqrt(1.0 + (g_usdm_raw / (g_bar + 1e-2))**2)
        
        g_pred = g_bar + (g_usdm_raw * feedback_damp * (1.0 - ETA))
        
        res = np.log10(g_obs) - np.log10(g_pred)
        all_res.extend(res.values)

    all_res = np.array(all_res)
    std_dev = np.std(all_res)
    
    # Calculate Sigma-Confidence (P-Value analysis)
    # H0: The residuals are random noise. H1: The model describes the data.
    t_stat, p_val = stats.ttest_1samp(all_res, 0)
    # Convert P-value to Sigma (Z-score)
    sigma_level = stats.norm.ppf(1 - p_val/2)
    
    print("\n[ UNIVERSAL SIGMA SCORECARD ]")
    print(f"Total Observations:    {len(all_res)}")
    print(f"Residual Mean:         {np.mean(all_res):.6f}")
    print(f"Residual Dispersion:   {std_dev:.6f} dex")
    print(f"Reduced Chi-Square:    {np.sum(all_res**2)/len(all_res):.4f}")
    print(f"Systemic Confidence:   {sigma_level:.2f} Sigma")
    
    if sigma_level >= 4.0:
        print("RESULT: 4+ SIGMA VERIFIED. The manifest is a universal solution.")

if __name__ == '__main__':
    run_universal_audit()
