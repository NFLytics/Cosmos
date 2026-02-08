import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import json

# --- LOAD CONFIG ---
with open('config/unified_model.json', 'r') as f:
    config = json.load(f)
    params = config['parameters']

# --- CONSTANTS ---
H0 = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5

# Model Params
W_OPTIMAL = params['w_early']
Z_CRIT = params['z_transition']
C_S_LATE = params['c_s_late']

def get_eos(a):
    """Reconstruct the Unified EOS"""
    a_c = 1.0 / (1.0 + Z_CRIT)
    width = 0.1 * a_c
    try:
        x = (a - a_c) / width
        x = np.clip(x, -100, 100)
        weight = 1.0 / (1.0 + np.exp(-x))
    except:
        weight = 1.0 if a > a_c else 0.0
        
    w = W_OPTIMAL * (1 - weight)
    # Sound speed: early is Luke-Warm, late is Superfluid
    c_s_early = C_LIGHT * np.sqrt(W_OPTIMAL)
    c_s = c_s_early * (1 - weight) + C_S_LATE * weight
    return w, c_s

def physics_engine_k_dependent(y, a, k_mode):
    """
    Solves growth for a specific spatial scale k (h/Mpc).
    Using Corrected Jeans Physics.
    """
    rho, d, dd = y
    w, c_s = get_eos(a)
    
    drho_da = -3 * (rho / a) * (1 + w)
    
    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK
    H = H0 * np.sqrt(E_sq)
    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)
    
    # --- CORRECTED JEANS PRESSURE ---
    # Term: (c_s / H)^2 * (k / a)^2 * delta
    # Units: c_s [km/s], H [km/s/Mpc], k [1/Mpc]
    # c_s/H -> Mpc. k -> 1/Mpc. Product is dimensionless.
    # 1/a^2 comes from physical laplacian.
    
    # We use k_mode directly (assuming h=0.7 approx for units or k is 1/Mpc)
    # If k is h/Mpc, and H is km/s/Mpc... 
    # Let's keep consistent: k_mode in code is treated as effective physical wavenumber.
    
    pressure = (c_s / H)**2 * (k_mode**2 / a**2) * d
    
    friction = (3/a + dH/H) * dd
    
    # Source: 1.5 * Omega_m * H0^2 / H^2 / a^5 ??
    # Standard derivation: 4 pi G rho / H^2 * d.
    # 4 pi G rho = 1.5 * H0^2 * Omega_m / a^3
    # So Gravity = 1.5 * (rho_code * H0^2) / H^2 / a^2 * d
    # rho_code is actual density (roughly Omega_m / a^3)
    # We use evolved rho.
    
    gravity = 1.5 * rho * (H0 / H)**2 / a**2 * d
    
    d_dd = gravity - friction - pressure
    return [drho_da, dd, d_dd]

def run_spectral_analysis():
    print('Phase 3: Generating Matter Power Spectrum P(k)')
    print(f'Using Mass: {params["particle_mass_ev"]:.4f} eV')
    print('------------------------------------------------')
    
    # Log-spaced k modes
    k_modes = np.logspace(-2, 1.5, 30) # 0.01 to 30 h/Mpc
    
    a_range = np.logspace(-3, 0, 500)
    rho_init = OM_PLANCK * (a_range[0])**-3 
    y0 = [rho_init, 1e-3, 1e-3]
    
    ratios = []
    
    print(f'{"k (h/Mpc)":<12} | {"Suppression":<12} | {"Structure Status"}')
    print('-'*45)

    # 1. Baseline CDM
    def cdm_engine(y, a):
        rho, d, dd = y
        drho = -3 * rho / a
        H = H0 * np.sqrt(OR_PLANCK/a**4 + rho + OL_PLANCK)
        dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho)
        grav = 1.5 * rho * (H0/H)**2 / a**2 * d
        fric = (3/a + dH/H) * dd
        return [drho, dd, grav - fric]
        
    sol_cdm = odeint(cdm_engine, y0, a_range)
    growth_cdm = sol_cdm[-1, 1]

    # 2. Unified Model Sweep
    for k in k_modes:
        sol = odeint(physics_engine_k_dependent, y0, a_range, args=(k,))
        growth_usdm = sol[-1, 1]
        
        ratio = growth_usdm / growth_cdm
        ratios.append(ratio)
        
        status = "Normal"
        if ratio < 0.99: status = "Suppressed"
        if ratio < 0.10: status = "Erased"
        
        if k in [k_modes[0], k_modes[10], k_modes[20], k_modes[-1]]:
             print(f'{k:<12.2f} | {ratio:<12.4f} | {status}')

    # --- ANALYSIS ---
    val_s8 = np.interp(0.7, k_modes, ratios)
    val_dwarf = np.interp(10.0, k_modes, ratios)
    
    print('-'*45)
    print(f'S8 Scale (k=0.7):     {val_s8:.4f}  (Target: ~0.95)')
    print(f'Dwarf Scale (k=10):   {val_dwarf:.4f}  (Target: >0.10)')
    
    if 0.90 < val_s8 < 0.99 and val_dwarf > 0.1:
        print('VERDICT: SPECTRAL MATCH. Solves S8, Preserves Galaxies.')
    elif val_dwarf < 0.1:
        print('VERDICT: OVER-COOLING. Dwarf galaxies erased.')
    else:
        print('VERDICT: MISMATCH.')

    # Plot
    plt.figure(figsize=(10,6))
    plt.semilogx(k_modes, ratios, lw=3, color='blue', label='USDM / CDM Ratio')
    plt.axvspan(0.3, 1.0, color='green', alpha=0.1, label='S8 Tension Zone')
    plt.axvspan(5.0, 30.0, color='orange', alpha=0.1, label='Dwarf Galaxy Zone')
    plt.axhline(1.0, linestyle='--', color='black')
    plt.xlabel('Wavenumber k (h/Mpc)')
    plt.ylabel('Power Suppression P(k) Ratio')
    plt.title(f'Phase 3: Corrected Spectral Fingerprint (m={params["particle_mass_ev"]:.3f} eV)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase3_power_spectrum.png')
    print('Spectrum saved to output/phase3_power_spectrum.png')

if __name__ == '__main__':
    run_spectral_analysis()
