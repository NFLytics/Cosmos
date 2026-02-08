import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
H0 = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5

# Fixed Transition Epoch (from previous success)
Z_CRIT = 1.0 

def get_eos(a, z_c, w_early):
    """
    Returns w(a) and c_s(a).
    Transition from w_early -> 0 at z_c.
    """
    a_c = 1.0 / (1.0 + z_c)
    width = 0.1 * a_c
    
    # Sigmoid Switch
    try:
        x = (a - a_c) / width
        # Clip to prevent overflow
        x = np.clip(x, -100, 100)
        weight = 1.0 / (1.0 + np.exp(-x))
    except:
        weight = 1.0 if a > a_c else 0.0
        
    w = w_early * (1 - weight)
    
    # Sound speed c_s = c * sqrt(w_eff) approx
    # (Adiabatic sound speed for constant w is c * sqrt(w))
    c_s_early = C_LIGHT * np.sqrt(max(w_early, 0))
    c_s_late = 30.0 # Superfluid phase
    
    c_s = c_s_early * (1 - weight) + c_s_late * weight
    return w, c_s

def density_solver(y, a, z_c, w_early):
    rho = y[0]
    w, _ = get_eos(a, z_c, w_early)
    return -3 * (rho / a) * (1 + w)

def find_initial_density(w_early, z_c):
    """
    Iteratively finds the required initial density at z=10000 
    to land exactly on OM_PLANCK at z=0.
    """
    a_start = 1e-4
    a_end = 1.0
    a_range = np.linspace(a_start, a_end, 500)
    
    # First guess: Standard CDM extrapolation
    rho_guess = OM_PLANCK * (a_start)**-3
    
    # We just run it once and measure the ratio, then scale.
    # Since the ODE is linear in rho (if w doesn't depend on rho),
    # scaling rho_init scales rho_final proportionally.
    
    sol = odeint(density_solver, [rho_guess], a_range, args=(z_c, w_early))
    rho_final = sol[-1, 0]
    
    correction_factor = OM_PLANCK / rho_final
    rho_corrected = rho_guess * correction_factor
    
    return rho_corrected

def perturbation_engine(y, a, z_c, w_early):
    rho, d, dd = y
    w, c_s = get_eos(a, z_c, w_early)
    
    # Density Evolution
    drho_da = -3 * (rho / a) * (1 + w)
    
    # Hubble
    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK
    H = H0 * np.sqrt(E_sq)
    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)
    
    # Perturbation
    k = 1.0 # Scale for S8
    pressure = (c_s / C_LIGHT)**2 * k**2 * d * 5e3
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * rho / (H/H0)**2 * d / a**2 
    
    d_dd = gravity - friction - pressure
    return [drho_da, dd, d_dd]

def run_optimizer():
    print('Phase 2e: Luke-Warm Parameter Optimizer')
    print('Target: S8 Suppression of 0.92 - 0.96')
    print('Constraint: Final Density = Planck (Auto-Corrected)')
    print('-'*65)
    print(f'{"w_early":<10} | {"c_s (km/s)":<12} | {"S8 Factor":<10} | {"Status"}')
    print('-'*65)
    
    # We sweep low-w values
    w_sweep = [0.0, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3]
    
    a_range = np.logspace(-4, 0, 1000)
    
    # Baseline CDM (w=0)
    rho_init_cdm = OM_PLANCK * (1e-4)**-3
    y0_cdm = [rho_init_cdm, 1e-4, 1e-4]
    
    # CDM Solver (Simplified)
    def cdm_solver(y, a):
        rho, d, dd = y
        drho = -3 * rho / a
        E_sq = (OR_PLANCK/a**4) + rho + OL_PLANCK
        H = H0 * np.sqrt(E_sq)
        dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho)
        grav = 1.5 * rho / (H/H0)**2 * d / a**2
        fric = (3/a + dH/H) * dd
        return [drho, dd, grav - fric]

    sol_cdm = odeint(cdm_solver, y0_cdm, a_range)
    growth_cdm = sol_cdm[-1, 1]
    
    results = []
    
    for w in w_sweep:
        # 1. Calculate correct initial density
        rho_init = find_initial_density(w, Z_CRIT)
        
        # 2. Run Simulation
        y0 = [rho_init, 1e-4, 1e-4]
        sol = odeint(perturbation_engine, y0, a_range, args=(Z_CRIT, w))
        growth_sdh = sol[-1, 1]
        
        s8_factor = growth_sdh / growth_cdm
        c_s = C_LIGHT * np.sqrt(w)
        
        status = "FAIL"
        if 0.90 <= s8_factor <= 0.98: status = "OPTIMAL"
        elif s8_factor < 0.90: status = "TOO STRONG"
        elif s8_factor > 0.98: status = "WEAK"
        
        print(f'{w:<10.2e} | {c_s:<12.0f} | {s8_factor:<10.4f} | {status}')
        results.append((w, s8_factor))
        
    # Plot
    ws, s8s = zip(*results)
    plt.figure(figsize=(10,6))
    plt.semilogx(ws, s8s, marker='o', lw=2)
    plt.axhspan(0.92, 0.96, color='green', alpha=0.2, label='Target Zone')
    plt.axhline(1.0, linestyle='--', color='red', label='CDM')
    plt.xlabel('Equation of State w')
    plt.ylabel('S8 Suppression Factor')
    plt.title('Finding the "Luke-Warm" Goldilocks Zone')
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase2_optimization.png')
    print('Optimization plot saved to output/phase2_optimization.png')

if __name__ == '__main__':
    run_optimizer()
