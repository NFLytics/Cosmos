import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_comparison():
    print("Phase 7: Final Theoretical Comparison (USDM vs CDM vs MOND)")
    df = pd.read_csv("data/standardized_cosmos_v2.csv")
    
    # Unit Normalization
    df['g_obs'] = (df['v_obs']**2) / df['r_kpc']
    ups_disk = 0.5
    v_bar_sq = (df['v_gas']**2) + (ups_disk * df['v_disk']**2)
    df['g_bar'] = v_bar_sq / df['r_kpc']
    
    # Filters
    df = df.dropna(subset=['g_obs', 'g_bar'])
    df = df[df['g_bar'] > 0]

    plt.figure(figsize=(12, 8))
    
    # 1. SPARC Scatter
    plt.hexbin(np.log10(df['g_bar']), np.log10(df['g_obs']), gridsize=50, cmap='Greys', mincnt=1, alpha=0.3)
    
    # 2. Theoretical Tracks
    g_range = np.logspace(-13, -8, 100)
    
    # MOND
    a0 = 1.2e-10
    g_mond = g_range / (1 - np.exp(-np.sqrt(g_range / a0)))
    plt.plot(np.log10(g_range), np.log10(g_mond), color='red', label='MOND (a0=1.2e-10)', lw=2)
    
    # USDM (2.83 eV / 80 km/s)
    # Effective acceleration includes the superfluid phonon term
    g_usdm = g_range + (80.0**2 / 10.0) * 1e-10 
    plt.plot(np.log10(g_range), np.log10(g_usdm), '--', color='blue', label='USDM (80 km/s)', lw=3)
    
    # CDM (Average NFW Fit)
    g_cdm = g_range + 0.5*g_range**0.5 * 1e-5 # Approximation of Halo-to-Baryon ratio
    plt.plot(np.log10(g_range), np.log10(g_cdm), ':', color='green', label='Standard CDM (NFW)', lw=2)

    plt.xlabel('log10(g_baryon)')
    plt.ylabel('log10(g_observed)')
    plt.title('Final Unified Theory Comparison')
    plt.legend()
    plt.savefig('output/phase7_comparison.png')
    print("Final comparison plot generated: output/phase7_comparison.png")

if __name__ == '__main__':
    run_comparison()
