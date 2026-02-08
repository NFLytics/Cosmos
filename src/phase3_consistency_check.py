import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
H0 = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5

def get_eos_freezing(a, peak_cs):
    # Freezing transition at z=3
    z = (1.0/a) - 1.0
    z_c = 3.0
    weight = 1.0 / (1.0 + np.exp(2.0 * (z - z_c)))
    c_s = peak_cs * weight
    w = (c_s / C_LIGHT)**2
    return w, c_s

def physics_engine(y, a, k_mode, peak_cs):
    rho, d, dd = y
    w, c_s = get_eos_freezing(a, peak_cs)
    
    drho_da = -3 * (rho / a) * (1 + w)
    
    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK
    H = H0 * np.sqrt(E_sq)
    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)
    
    # Corrected Jeans Pressure
    pressure = (c_s / H)**2 * (k_mode**2 / a**2) * d
    
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * rho * (H0 / H)**2 / a**2 * d
    
    d_dd = gravity - friction - pressure
    return [drho_da, dd, d_dd]

def run_consistency_check():
    print('Phase 3d: Galactic Consistency Check (Low-Velocity Regime)')
    print('Testing if Galactic Rotation speeds (30 km/s) break Cosmology')
    print('-'*65)
    print(f'{"c_s (km/s)":<12} | {"S8 (k=0.7)":<12} | {"Dwarf (k=10)":<12} | {"Verdict"}')
    print('-'*65)
    
    # The Galactic Range + S8 Candidates
    cs_sweep = [200, 150, 120, 100, 80, 50, 30, 10]
    
    a_range = np.logspace(-3, 0, 400)
    rho_init = OM_PLANCK * (a_range[0])**-3 
    y0 = [rho_init, 1e-3, 1e-3]
    
    # CDM Baseline
    sol_cdm = odeint(physics_engine, y0, a_range, args=(1.0, 0.0))
    growth_cdm = sol_cdm[-1, 1]
    
    results = []
    
    for c_s in cs_sweep:
        # S8 Scale
        sol_s8 = odeint(physics_engine, y0, a_range, args=(0.7, c_s))
        r_s8 = sol_s8[-1, 1] / growth_cdm
        
        # Dwarf Scale
        sol_dwarf = odeint(physics_engine, y0, a_range, args=(10.0, c_s))
        r_dwarf = sol_dwarf[-1, 1] / growth_cdm
        
        status = "..."
        if 0.90 <= r_s8 <= 0.98:
            if r_dwarf > 0.5: status = "GOLDEN"
            else: status = "S8 SOLVED (Dwarf Risk)"
        elif r_s8 > 0.98:
            status = "SAFE (No S8 Fix)"
        else:
            status = "TOO STRONG"
            
        print(f'{c_s:<12} | {r_s8:<12.4f} | {r_dwarf:<12.4f} | {status}')
        results.append((c_s, r_s8, r_dwarf))
        
    # Plot
    cs_vals, s8s, dwarfs = zip(*results)
    plt.figure(figsize=(10,6))
    plt.plot(cs_vals, s8s, 'o-', label='S8 (k=0.7)')
    plt.plot(cs_vals, dwarfs, 's-', label='Dwarfs (k=10)')
    plt.axhspan(0.92, 0.96, color='green', alpha=0.1, label='S8 Target')
    plt.axhline(1.0, linestyle='--', color='black')
    
    plt.xlabel('Late-Time Sound Speed (km/s)')
    plt.ylabel('Growth Suppression Ratio')
    plt.title('Low-Velocity Regime: Finding the Cross-Over')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase3_consistency.png')
    print('Plot saved to output/phase3_consistency.png')

if __name__ == '__main__':
    run_consistency_check()
