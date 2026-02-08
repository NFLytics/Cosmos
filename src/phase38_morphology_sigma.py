import numpy as np
import pandas as pd

def run_morphology_sigma():
    print("Phase 38: Morphological σ-Recalibration (HSB vs LSB)")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'v_gas'])
    
    CS, A0_RAW = 80.0, 3700.0
    results = []
    
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        # Calculate Baryonic Density for morphological tagging
        # HSB (High Surface Brightness) vs LSB (Low Surface Brightness)
        v_total_sq = group['v_gas']**2 + 0.5*group['v_disk']**2
        is_hsb = v_total_sq.mean() > 5000 # Velocity-based density proxy
        
        g_bar = v_total_sq / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        g_limit = (CS**2 / (group['r_kpc'] + 0.1))
        alpha = 0.15 * np.log1p(A0_RAW / (g_bar + 0.5))
        g_pred = g_bar + (g_limit * alpha * (1.0 / np.sqrt(1.0 + ( (g_limit*alpha) / (g_bar + 1e-2))**2)))
        
        res = (np.log10(g_obs) - np.log10(g_pred)).values
        results.append({'hsb': is_hsb, 'res': res})

    hsb_res = np.concatenate([r['res'] for r in results if r['hsb']])
    lsb_res = np.concatenate([r['res'] for r in results if not r['hsb']])
    
    print("\n[ MORPHOLOGICAL SIGMA SPLIT ]")
    print(f"HSB Dispersion (σ): {np.std(hsb_res):.6f} dex (Stability in Density)")
    print(f"LSB Dispersion (σ): {np.std(lsb_res):.6f} dex (Quantum Turbulence)")
    print(f"Differential:       {np.abs(np.std(hsb_res) - np.std(lsb_res)):.6f}")

if __name__ == '__main__':
    run_morphology_sigma()
