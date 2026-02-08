import numpy as np
import pandas as pd
import os

def run_tensor_integration():
    print("Phase 31: Simultaneous Multi-Layer Feedback Integration")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'v_gas'])
    
    # Locked Particle Physics
    M_EV = 2.8349
    CS = 80.0
    A0_RAW = 3700.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        # Vector 1: Kinematic Anchor
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Vector 2: Simultaneous Feedback (Self-Limiting)
        # We replace linear coupling with a Sigmoid Saturation function
        # This ensures that as g_usdm/g_bar (Xi) grows, the efficiency drops.
        def g_usdm_feedback(r, g_b):
            # Base superfluid term
            base = (CS**2 / (r + 0.2)) * 0.12 * np.log1p(A0_RAW / (g_b + 0.1))
            # Self-Limiting Feedback Tensor: Depletion factor
            # As g_b becomes small (LSBs), depletion increases to prevent 'Overload'
            depletion = 1.0 / (1.0 + np.exp(2.0 * (0.5 - g_b/A0_RAW)))
            return base * depletion

        g_usdm = g_usdm_feedback(group['r_kpc'], g_bar)
        
        # Vector 3: Global Resultancy
        prediction = g_bar + g_usdm
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm / (g_bar + 1e-5)
        
        results.append({
            'galaxy': name,
            'resid': resid,
            'max_xi': xi.max(),
            'mean_xi': xi.mean()
        })

    final_df = pd.DataFrame(results)
    print("\n[ TENSOR INTEGRATION SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Mean Ensemble Residual: {final_df['resid'].mean():.6f}")
    
    # Check if the Overload galaxies are contained
    overloads = final_df[final_df['mean_xi'] > 5.0]
    print(f"Residual Overload Systems: {len(overloads)}")

if __name__ == '__main__':
    run_tensor_integration()
