import numpy as np
import pandas as pd

def run_gl_integration():
    print("Phase 35: Ginzburg-Landau Simultaneous Feedback Integration")
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
        
        # 2. Ginzburg-Landau Order Parameter Feedback
        # The 'Superfluid Fraction' (f_sf) depends on the Mach Number and local potential
        mach_sq = (v_obs / CS)**2
        # Density suppression: High local acceleration suppresses the condensate order parameter
        order_param = np.exp(-mach_sq) * (1.0 / (1.0 + g_bar/A0_RAW))
        
        # 3. Simultaneous Interaction Vector
        # The lift is proportional to the order parameter and the sound speed
        g_usdm_raw = (CS**2 / (group['r_kpc'] + 0.2)) * 0.45 * order_param
        
        # 4. Self-Correction Feedback (Back-Reaction)
        # Xi control: Ensuring g_usdm does not exceed 1.5 * g_bar in HSB cores
        g_usdm_final = np.minimum(g_usdm_raw, 1.5 * g_bar + (0.5 * A0_RAW * order_param))
        
        prediction = g_bar + g_usdm_final
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm_final / (g_bar + 1e-5)
        
        results.append({'galaxy': name, 'resid': resid, 'mean_xi': xi.mean(), 'max_xi': xi.max()})

    final_df = pd.DataFrame(results)
    print(f"\n[ GINZBURG-LANDAU SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Ensemble Residual: {final_df['resid'].mean():.6f}")
    print(f"Integrity Rate (Non-Contradictory): {len(final_df[final_df['max_xi'] < 2.5]) / len(final_df) * 100:.2f}%")
    
if __name__ == '__main__':
    run_gl_integration()
