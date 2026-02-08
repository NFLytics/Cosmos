import numpy as np
import pandas as pd
import os

def run_feedback_vectors():
    print("Phase 30: Multi-Vector Feedback & Interaction Audit")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'v_gas'])
    
    # Constituent Constants
    CS = 80.0
    A0_RAW = 3700.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        # 1. Kinematic Vector (The Observational Data)
        g_obs = (group['v_obs']**2) / group['r_kpc']
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        
        # 2. Quantum Vector (The Theoretical Push)
        # Saturated Log-Normal coupling from Phase 24
        g_usdm = (CS**2 / (group['r_kpc'] + 0.2)) * 0.12 * np.log1p(A0_RAW / (g_bar + 0.1))
        
        # 3. Feedback Vector (The Interaction Ratio Xi)
        # Xi = g_usdm / g_bar. 
        # If Xi is too high in the core, it contradicts 'Maximum Disk' observations.
        xi = g_usdm / g_bar
        
        # 4. Integrity Check: Contradiction Search
        # A contradiction occurs if the total predicted acceleration significantly
        # overshoots g_obs while Xi is high (Pressure Overload).
        prediction = g_bar + g_usdm
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(prediction))**2))
        
        results.append({
            'galaxy': name,
            'mean_xi': xi.mean(),
            'core_xi': xi.iloc[0],
            'resid': resid,
            'contradiction': (resid > 0.6) and (xi.mean() > 2.0)
        })

    audit_df = pd.DataFrame(results)
    print("\n[ INTERACTION VECTOR SUMMARY ]")
    print(f"Total Galaxies Audited: {len(audit_df)}")
    print(f"Systemic Balance (Mean Xi): {audit_df['mean_xi'].mean():.4f}")
    print(f"Verifiable Integrity (Non-Contradictory): {len(audit_df[audit_df['contradiction'] == False])}")
    
    # Report extreme outliers
    outliers = audit_df[audit_df['contradiction'] == True]
    if not outliers.empty:
        print(f"\n[!] WARNING: {len(outliers)} systems show Superfluid Pressure Overload.")
        print(outliers[['galaxy', 'resid', 'mean_xi']])

if __name__ == '__main__':
    run_feedback_vectors()
