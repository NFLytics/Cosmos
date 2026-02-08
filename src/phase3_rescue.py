import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
H0 = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5
Z_CRIT = 1.0         # Fixed Transition

# --- PHYSICS ENGINE (CORRECTED) ---
def get_eos(a, c_s_early):
    # Transition Logic
    a_c = 1.0 / (1.0 + Z_CRIT)
    width = 0.1 * a_c
    try:
        weight = 1.0 / (1.0 + np.exp(-(a - a_c)/width))
    except:
        weight = 1.0 if a > a_c else 0.0
    
    # Sound Speed Profile
    c_s_late = 30.0 # Galactic fits
    c_s = c_s_early * (1 - weight) + c_s_late * weight
    
    # Equation of State w ~ (c_s/c)^2
    w = (c_s / C_LIGHT)**2
    return w, c_s

def physics_engine(y, a, k_mode, c_s_early):
    rho, d, dd = y
    w, c_s = get_eos(a, c_s_early)
    
    drho_da = -3 * (rho / a) * (1 + w)
    
    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK
    H = H0 * np.sqrt(E_sq)
    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)
    
    # CORRECTED PRESSURE TERM
    # (c_s/H)^2 * (k/a)^2 * delta
    pressure = (c_s / H)**2 * (k_mode**2 / a**2) * d
    
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * rho * (H0 / H)**2 / a**2 * d
    
    d_dd = gravity - friction - pressure
    return [drho_da, dd, d_dd]

def run_rescue_sweep():
    print('Phase 3b: The Rescue Sweep (Corrected Physics)')
    print('Searching for viable Sound Speed c_s...')
    print('-'*65)
    print(f'{"c_s (km/s)":<12} | {"S8 (k=0.7)":<12} | {"Dwarf (k=10)":<12} | {"Verdict"}')
    print('-'*65)
    
    # Log-space sweep of sound speeds
    # From 3000 km/s (Failed) down to 10 km/s
    cs_sweep = [2000, 1000, 500, 300, 200, 150, 100, 50, 20]
    
    a_range = np.logspace(-3, 0, 400)
    rho_init = OM_PLANCK * (a_range[0])**-3 
    y0 = [rho_init, 1e-3, 1e-3]
    
    # CDM Reference (c_s = 0)
    # We simulate effectively c_s=0 by using extremely low value or different func
    # Re-using engine with c_s=0 for consistency
    sol_cdm = odeint(physics_engine, y0, a_range, args=(1.0, 0.0))
    growth_cdm = sol_cdm[-1, 1]
    
    results = []
    
    for c_s in cs_sweep:
        # Run S8 Scale
        sol_s8 = odeint(physics_engine, y0, a_range, args=(0.7, c_s))
        r_s8 = sol_s8[-1, 1] / growth_cdm
        
        # Run Dwarf Scale
        sol_dwarf = odeint(physics_engine, y0, a_range, args=(10.0, c_s))
        r_dwarf = sol_dwarf[-1, 1] / growth_cdm
        
        status = "FAIL"
        if 0.90 <= r_s8 <= 0.99 and r_dwarf > 0.5:
            status = "VIABLE"
        elif r_s8 < 0.90:
            status = "TOO HOT"
        elif r_s8 > 0.99:
            status = "TOO COLD"
            
        print(f'{c_s:<12} | {r_s8:<12.4f} | {r_dwarf:<12.4f} | {status}')
        results.append((c_s, r_s8, r_dwarf))
        
    # Plot
    cs_vals, s8s, dwarfs = zip(*results)
    
    plt.figure(figsize=(10,6))
    plt.semilogx(cs_vals, s8s, 'o-', label='S8 Scale (k=0.7)')
    plt.semilogx(cs_vals, dwarfs, 's-', label='Dwarf Scale (k=10)')
    
    plt.axhspan(0.90, 0.98, color='green', alpha=0.1, label='S8 Target')
    plt.axhline(0.5, color='red', linestyle='--', label='Dwarf Survival Line')
    
    plt.xlabel('Early Sound Speed c_s (km/s)')
    plt.ylabel('Power Suppression Ratio')
    plt.title('The "Goldilocks" Sound Speed')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase3_rescue.png')
    print('Rescue plot saved to output/phase3_rescue.png')

if __name__ == '__main__':
    run_rescue_sweep()
