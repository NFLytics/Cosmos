import numpy as np
import pandas as pd

def run_bogoliubov_sync():
    print("Phase 34: Bogoliubov Curvature-Sync Integration")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    CS = 80.0
    A0_RAW = 3700.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        group = group.sort_values('r_kpc')
        
        # 1. Primary Kinematic Vectors
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # 2. Curvature Feedback (Second Derivative of Potential)
        # This represents the 'Quantum Surface Tension'
        potential = -np.cumsum(g_bar * np.gradient(group['r_kpc']))
        curvature = np.abs(np.gradient(np.gradient(potential)))
        curvature_mod = 1.0 + np.log1p(curvature / np.median(curvature + 1e-5))
        
        # 3. Simultaneous Interaction: The Bogoliubov Limit
        # We couple the sound speed to the local curvature mod
        # Ensuring the pressure is 'smart'—high where potential is complex
        g_usdm_raw = (CS**2 / (group['r_kpc'] + 0.2)) * 0.12 * np.log1p(A0_RAW / (g_bar + 0.1))
        
        # Apply the Curvature-Sync Feedback
        g_usdm_final = g_usdm_raw * (curvature_mod / (1.0 + g_usdm_raw/A0_RAW))
        
        prediction = g_bar + g_usdm_final
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm_final / (g_bar + 1e-5)
        
        results.append({'galaxy': name, 'resid': resid, 'mean_xi': xi.mean(), 'max_xi': xi.max()})

    final_df = pd.DataFrame(results)
    print(f"\n[ BOGOLIUBOV-SYNC SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Ensemble Residual: {final_df['resid'].mean():.6f}")
    print(f"Integrity Rate (Non-Contradictory): {len(final_df[final_df['max_xi'] < 4.0]) / len(final_df) * 100:.2f}%")
    
if __name__ == '__main__':
    run_bogoliubov_sync()
