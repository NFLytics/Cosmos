import numpy as np
import pandas as pd

def run_vortex_integration():
    print("Phase 32: Quantized Vortex Lattice Feedback")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Physics: Critical Velocity & Vortex Dissipation
    # cs = 80 km/s (The global sound speed limit)
    def calculate_vortex_damping(v_obs, cs):
        # Once v_obs approaches cs, the superfluid forms vortices
        # and its coherent pressure (the dark force) drops.
        v_ratio = np.clip(v_obs / cs, 0, 2.0)
        # Dissipation factor (Lorentzian-style drop-off)
        return 1.0 / (1.0 + v_ratio**4)

    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Apply Simultaneous Layers + Vortex Damping
        base_usdm = (80.0**2 / (group['r_kpc'] + 0.2)) * 0.12 * np.log1p(3700.0 / (g_bar + 0.1))
        
        # New Layer: Vortex Feedback Vector
        damping = calculate_vortex_damping(group['v_obs'], 80.0)
        g_usdm_final = base_usdm * damping
        
        prediction = g_bar + g_usdm_final
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm_final / (g_bar + 1e-5)
        
        results.append({'galaxy': name, 'resid': resid, 'mean_xi': xi.mean()})

    final_df = pd.DataFrame(results)
    print(f"\n[ VORTEX INTEGRATION SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Final Ensemble Residual: {final_df['resid'].mean():.6f}")
    print(f"Extreme Overloads (>5.0): {len(final_df[final_df['mean_xi'] > 5.0])}")

if __name__ == '__main__':
    run_vortex_integration()
