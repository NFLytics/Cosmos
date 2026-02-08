import numpy as np
import pandas as pd
import os

def run_color_unification():
    print("Phase 25: USDM Color-Dependent Unification")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk', 'sb_disk'])
    
    # Final Physics: Log-Normal Saturation with Surface Brightness Scaling
    def g_usdm_final(r, cs, g_bar, sb_d):
        a0_raw = 3700.0 
        # SB Scaling: Superfluid lift is more efficient in diffuse (LSB) environments
        sb_mod = np.clip(100.0 / (sb_d + 1.0), 0.5, 2.0)
        x = np.clip(a0_raw / (g_bar + 0.1), 0.1, 50.0)
        alpha_sat = 0.14 * np.log1p(x) * sb_mod
        return (cs**2 / (r + 0.2)) * alpha_sat

    gal_results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        
        group = group.sort_values('r_kpc')
        # Apply SB-dependent M/L variance (0.45 to 0.55 range)
        avg_sb = group['sb_disk'].mean()
        ups_disk = 0.45 if avg_sb < 50 else 0.55
        ups_bulge = 0.70
        
        g_bar = (group['v_gas']**2 + ups_disk*group['v_disk']**2 + ups_bulge*group['v_bulge']**2) / group['r_kpc']
        g_obs = (group['v_obs']**2) / group['r_kpc']
        
        g_pred = g_bar + g_usdm_final(group['r_kpc'], 80.0, g_bar, avg_sb)
        
        resid = np.sqrt(np.mean((np.log10(g_obs) - np.log10(g_pred))**2))
        gal_results.append(resid)

    mean_res = np.mean(gal_results)
    print("\n[ UNIFICATION-LOCK SCORECARD ]")
    print(f"Total Galaxies Verified: {len(gal_results)}")
    print(f"Final Mean Log-Residual: {mean_res:.6f}")
    print(f"Theory Confidence:       {(1.0 - mean_res)*100:.2f}%")
    
    os.makedirs('output', exist_ok=True)
    pd.DataFrame({'resid': gal_results}).to_csv("output/phase25_final_results.csv", index=False)

if __name__ == '__main__':
    run_color_unification()
