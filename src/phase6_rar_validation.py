import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- LOCKED PARAMETERS (PHASE 4) ---
M_EV = 2.8349
CS_KMS = 80.0
G_CONST = 4.302e-6 # kpc (km/s)^2 / M_sun

def run_validation():
    print("Phase 6: USDM Radial Acceleration Validation")
    df = pd.read_csv("data/standardized_cosmos_v2.csv")
    
    # 1. Calculate Observed and Baryonic Acceleration (m/s^2 conversion factor not needed for ratio)
    # g = V^2 / R
    df['g_obs'] = (df['v_obs']**2) / df['r_kpc']
    
    # Standard M/L Ratios (Upsilon)
    ups_disk = 0.5
    ups_bulge = 0.7
    v_bar_sq = (df['v_gas']**2) + (ups_disk * df['v_disk']**2) + (ups_bulge * df['v_bulge']**2)
    df['g_bar'] = v_bar_sq / df['r_kpc']
    
    # 2. USDM Theoretical Prediction
    # The superfluid acceleration g_sf is proportional to the gradient of the condensate density.
    # In the high-density limit (Core), it mimics a constant acceleration a_0.
    a_0_m_s2 = 1.2e-10 # MOND scale for reference
    
    # We estimate the USDM contribution based on the 80 km/s sound speed.
    # Theoretical g_sf ~ (cs^2 / R) * (rho_condensate / rho_total)
    df['g_usdm_pred'] = (CS_KMS**2 / df['r_kpc']) * 0.05 # 5% Coupling factor from Phase 3
    
    # 3. Filtering for High-Quality Plots
    # Focus on galaxies with at least 10 radial points
    valid_galaxies = df.groupby('galaxy').filter(lambda x: len(x) > 10)['galaxy'].unique()
    
    plt.figure(figsize=(10, 8))
    
    # Plot RAR (Radial Acceleration Relation)
    # Log(g_obs) vs Log(g_bar)
    plt.scatter(np.log10(df['g_bar']), np.log10(df['g_obs']), s=1, alpha=0.1, color='gray', label='SPARC Data')
    
    # Theoretical Line (Standard MOND for comparison)
    g_bar_test = np.logspace(-13, -8, 100)
    g_mond = g_bar_test / (1 - np.exp(-np.sqrt(g_bar_test / 1.2e-10)))
    plt.plot(np.log10(g_bar_test), np.log10(g_mond), color='red', lw=2, label='Standard MOND')
    
    # USDM Line (80 km/s Sound Speed effect)
    g_usdm = g_bar_test + (CS_KMS**2 / 10.0) * 1e-10 # Simplified scaling for visual check
    plt.plot(np.log10(g_bar_test), np.log10(g_usdm), '--', color='blue', lw=2, label='USDM (2.83 eV / 80 km/s)')

    plt.xlabel('log10(g_bar) [Baryonic Acceleration]')
    plt.ylabel('log10(g_obs) [Observed Acceleration]')
    plt.title('USDM Radial Acceleration Relation (RAR) Fit')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('output/phase6_rar_fit.png')
    print("Validation Plot saved to output/phase6_rar_fit.png")
    
    # Calculate Residuals
    rms_usdm = np.sqrt(np.mean((np.log10(df['g_obs']) - np.log10(df['g_bar'] + df['g_usdm_pred']))**2))
    print(f"USDM Global RMS Residual: {rms_usdm:.4f}")

if __name__ == '__main__':
    run_validation()
