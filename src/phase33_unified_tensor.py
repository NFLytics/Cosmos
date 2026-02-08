import numpy as np
import pandas as pd
import os

def run_unified_tensor():
    print("Phase 33: Unified NS-GP Feedback Tensor Integration")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Fundamental Properties
    M_EV = 2.8349
    CS = 80.0
    A0_RAW = 3700.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        # 1. Baryonic Input
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        v_obs = group['v_obs']
        
        # 2. Simultaneous Feedback Layers
        # a. Healing Length Constraint (Scale-dependency)
        healing_limit = 1.0 - np.exp(-group['r_kpc'] / 0.5) 
        
        # b. Vortex Lattice Repulsion (Rotational Feedback)
        v_crit = 15.0 # km/s - typical superfluid critical velocity
        vortex_factor = np.exp(-(v_obs / CS)**2)
        
        # c. Acoustic Saturation (The Hard Ceiling)
        # The USDM force cannot exceed the acoustic pressure of the condensate
        g_acoustic_limit = (CS**2 / (group['r_kpc'] + 0.1))
        
        # d. The Coupled Coupling (Alpha)
        alpha_base = 0.12 * np.log1p(A0_RAW / (g_bar + 0.1))
        
        # 3. Simultaneous Interaction Logic
        g_usdm_raw = g_acoustic_limit * alpha_base * healing_limit * vortex_factor
        
        # Apply the 'Back-Reaction' Feedback: The force limits its own growth
        g_usdm_final = g_usdm_raw / (1.0 + (g_usdm_raw / (g_bar + 1e-3))**0.5)
        
        prediction = g_bar + g_usdm_final
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        xi = g_usdm_final / (g_bar + 1e-5)
        
        results.append({'galaxy': name, 'resid': resid, 'mean_xi': xi.mean(), 'max_xi': xi.max()})

    final_df = pd.DataFrame(results)
    print(f"\n[ UNIFIED TENSOR SCORECARD ]")
    print(f"Systemic Balance (Mean Xi): {final_df['mean_xi'].mean():.4f}")
    print(f"Ensemble Residual: {final_df['resid'].mean():.6f}")
    print(f"Verified Integrity Rate: {len(final_df[final_df['max_xi'] < 3.0]) / len(final_df) * 100:.2f}%")
    
    # Identify stubborn outliers
    overloads = final_df[final_df['mean_xi'] > 2.0]
    if not overloads.empty:
        print(f"Remaining Overload Systems: {len(overloads)}")

if __name__ == '__main__':
    run_unified_tensor()
