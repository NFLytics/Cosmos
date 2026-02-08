import numpy as np
import pandas as pd

def run_bogoliubov_sync():
    print("Phase 41: Non-Local Quantum Stress & Bogoliubov Sync")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    CS_BASAL = 80.0
    M_EV = 2.8349
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        group = group.sort_values('r_kpc')
        
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # 1. Non-Local Stress Factor (The 'Stiffness' Vector)
        # Calculated from the curvature of the baryonic potential
        potential = -np.cumsum(g_bar * np.gradient(group['r_kpc']))
        curvature = np.abs(np.gradient(np.gradient(potential)))
        stiffness = np.log1p(curvature) # Non-local resistance to change
        
        # 2. Bogoliubov Scaling (Momentum-dependent sound speed)
        # Effective CS increases with the local density gradient
        cs_eff = CS_BASAL * (1.0 + 0.15 * stiffness)
        
        # 3. Simultaneous Interaction with Acoustic Saturation
        g_limit = (cs_eff**2 / (group['r_kpc'] + 0.1))
        alpha = 0.12 * np.log1p(3700.0 / (g_bar + 0.5))
        
        # Feedback-limited final acceleration
        g_pred = g_bar + (g_limit * alpha / (1.0 + (g_limit*alpha / (g_bar + 1e-2))**0.5))
        
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        results.append({'galaxy': name, 'stiffness': stiffness.mean(), 'resid': resid})

    final_df = pd.DataFrame(results)
    print("\n[ NON-LOCAL INTERACTION SCORECARD ]")
    print(f"Mean Quantum Stiffness (Non-Locality): {final_df['stiffness'].mean():.4f}")
    print(f"Global Ensemble Residual:              {final_df['resid'].mean():.6f}")
    print(f"HSB/LSB Stability (Stiffness Std):     {final_df['stiffness'].std():.4f}")

if __name__ == '__main__':
    run_bogoliubov_sync()
