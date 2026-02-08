import numpy as np
import pandas as pd

def run_eos_saturation():
    print("Phase 36: USDM EoS Saturation & Simultaneous Feedback")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    CS = 80.0
    A0_RAW = 3700.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        # 1. Primary Kinematic Vectors
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        v_obs = group['v_obs']
        
        # 2. Simultaneous Interaction Vector (The EoS Ceiling)
        # Pressure P_q limits the density rho_sf.
        # We calculate the 'Quantum Saturation' based on the sound speed
        g_limit = (CS**2 / (group['r_kpc'] + 0.1))
        
        # 3. Non-Linear Coupling with High-G Suppression
        # The lift is strong at low-g (MOND-like) but capped by CS^2/r
        alpha = 0.15 * np.log1p(A0_RAW / (g_bar + 0.5))
        g_usdm_ideal = g_limit * alpha
        
        # 4. Simultaneous Feedback (Self-Interacting Limitation)
        # This is the 'Back-Reaction' that keeps Xi near 1.0
        # Formula: 1 / sqrt(1 + (g_usdm/g_bar)^2)
        feedback_damp = 1.0 / np.sqrt(1.0 + (g_usdm_ideal / (g_bar + 1e-2))**2)
        g_usdm_final = g_usdm_ideal * feedback_damp
        
        prediction = g_bar + g_usdm_final
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm_final / (g_bar + 1e-5)
        
        results.append({'galaxy': name, 'resid': resid, 'mean_xi': xi.mean(), 'max_xi': xi.max()})

    final_df = pd.DataFrame(results)
    print(f"\n[ EoS SATURATION SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Ensemble Residual: {final_df['resid'].mean():.6f}")
    print(f"Integrity Rate (Non-Contradictory): {len(final_df[final_df['max_xi'] < 2.0]) / len(final_df) * 100:.2f}%")
    
if __name__ == '__main__':
    run_eos_saturation()
