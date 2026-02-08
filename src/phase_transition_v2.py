import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
Om = 0.315
Ol = 1.0 - Om
Or = 8e-5
H0 = 67.4
C_LIGHT = 3e5

def hubble(a):
    return np.sqrt(Or/a**4 + Om/a**3 + Ol)

def sound_speed_relativistic_transition(a, z_c):
    """
    Models the transition from Relativistic Plasma (Early) to Superfluid Condensate (Late).
    """
    if z_c <= -1.0: return 30.0 # Baseline fail-safe
    
    a_c = 1.0 / (1.0 + z_c)
    
    # PHASE 1: Relativistic/Hot (Required for S8)
    # Based on Inverse Solver success: c_s_eff ~ 300 km/s at z=0 extrapolated back
    c_s_hot = 300.0 / a 
    # Cap at speed of light to be physically safe
    c_s_hot = min(c_s_hot, C_LIGHT / np.sqrt(3)) 
    
    # PHASE 2: Superfluid/Cold (Required for Galaxies)
    c_s_cold = 30.0 
    
    # Transition Logic (Sigmoid)
    # width controls sharpness. 0.2 means transition spans ~20% of the scale factor epoch
    width = 0.2 * a_c 
    try:
        arg = (a - a_c) / width
        arg = np.clip(arg, -50, 50)
        weight = 1.0 / (1.0 + np.exp(-arg)) # 0 at early times, 1 at late times
    except:
        weight = 0.5
        
    c_s = c_s_hot * (1 - weight) + c_s_cold * weight
    return c_s

def growth_equation(y, a, z_c):
    d, dd = y
    H = hubble(a)
    dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)
    k = 1.0 # h/Mpc scale for S8
    
    c_s = sound_speed_relativistic_transition(a, z_c)
    
    # Pressure Term (Jeans Suppression)
    pressure = (c_s / C_LIGHT)**2 * k**2 * d * 5e3 
    
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * Om / (a**3 * H**2) * d
    
    return [dd, gravity - friction - pressure]

def run_transition_sweep_v2():
    print('Phase 2b (V2): Relativistic-to-Superfluid Transition Solver')
    print('Searching for the Phase Transition Epoch (z_c)...')
    
    a_range = np.logspace(-3, 0, 500)
    y0 = [1e-3, 1e-3]

    # 1. Baseline CDM
    def cdm_eq(y, a):
        d, dd = y
        H = hubble(a)
        dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)
        return [dd, 1.5 * Om / (a**3 * H**2) * d - (3/a + dH/H) * dd]
    
    sol_base = odeint(cdm_eq, y0, a_range)
    growth_cdm = sol_base[-1, 0]
    print(f'CDM Baseline Amplitude: {growth_cdm:.4f}')

    # 2. Sweep
    # We test high z (Matter-Radiation Equality) down to low z (Cluster formation)
    z_transitions = [3000.0, 1000.0, 500.0, 100.0, 50.0, 10.0, 3.0, 1.0]
    
    print(f'{"z_crit":<10} | {"S8 Suppression":<15} | {"Status"}')
    print('-'*45)
    
    results = []
    
    for z_c in z_transitions:
        sol = odeint(growth_equation, y0, a_range, args=(z_c,))
        growth_sdh = sol[-1, 0]
        suppression = growth_sdh / growth_cdm
        
        status = "FAIL"
        if 0.90 <= suppression <= 0.96: status = "OPTIMAL (GOLDEN)"
        elif suppression < 0.90: status = "TOO STRONG (ERASED)"
        elif suppression > 0.98: status = "INEFFECTIVE (CDM)"
        
        print(f'{z_c:<10.1f} | {suppression:<15.4f} | {status}')
        results.append((z_c, suppression))

    # Plot
    z_vals, s_vals = zip(*results)
    plt.figure(figsize=(10,6))
    plt.semilogx(z_vals, s_vals, marker='o', lw=2, color='red')
    plt.axhspan(0.90, 0.96, color='green', alpha=0.2, label='Solution Zone')
    plt.axhline(1.0, color='black', linestyle='--', label='CDM')
    plt.xlabel('Transition Redshift (z_c)')
    plt.ylabel('S8 Suppression Factor')
    plt.title('The Epoch of Condensation')
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase2b_result.png')
    print('Plot saved to output/phase2b_result.png')

if __name__ == '__main__':
    run_transition_sweep_v2()
