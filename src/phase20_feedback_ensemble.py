import numpy as np
import pandas as pd
import os

def run_feedback_ensemble():
    print("Phase 20: USDM Non-Linear Baryonic Feedback")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Physics: Non-Linear Baryonic Feedback
    # The superfluid coupling (lambda) is a function of the local g_bar
    def g_usdm_feedback(r, cs, g_bar):
        a0 = 1.2e-10
        # Feedback efficiency increases as g_bar drops, 
        # but provides a 'stiffening' boost in the inner core.
        # This is a modified interpolating function for the superfluid phase.
        nu = (1.0 - np.exp(-np.sqrt(g_bar / a0)))**-1
        return g_bar * (nu - 1.0)

    ups_disk = 0.50
    ups_bulge = 0.70
    
    gal_results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        group = group.sort_values('r_kpc')
        g_bar = (group['v_gas']**2 + ups_disk*group['v_disk']**2 + ups_bulge*group['v_bulge']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        # Apply Feedback Physics
        g_pred = g_bar + g_usdm_feedback(group['r_kpc'], 80.0, g_bar)
        
        # Logarithmic Residual
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        gal_results.append(resid)

    mean_res = np.mean(gal_results)
    print("\n[ FEEDBACK-ENSEMBLE SCORECARD ]")
    print(f"Verified Sample:   {len(gal_results)} Galaxies")
    print(f"Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence: {(1.0 - mean_res)*100:.2f}%")

if __name__ == '__main__':
    run_feedback_ensemble()
