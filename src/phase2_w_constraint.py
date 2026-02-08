import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
H0_PLANCK = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5

def rho_evolution(y, a, w):
    rho = y[0]
    # Conservation: d(rho)/da = -3 * (rho/a) * (1 + w)
    return -3 * (rho / a) * (1 + w)

def check_w_viability(w_val):
    a_range = np.linspace(1e-4, 1.0, 1000)
    
    # 1. Backward Integration (Match Late Universe Density)
    # We require rho_dm(z=0) = OM_PLANCK to match local gravity
    a_range_rev = a_range[::-1]
    rho_0 = OM_PLANCK
    sol = odeint(rho_evolution, [rho_0], a_range_rev, args=(w_val,))
    rho_evol = sol[::-1, 0]
    
    # 2. Check Early Universe Discrepancy (Recombination z=1000, a=1e-3)
    idx_early = np.searchsorted(a_range, 1e-3)
    rho_early_model = rho_evol[idx_early]
    rho_early_cdm = OM_PLANCK * (1e-3)**-3
    
    discrepancy_factor = rho_early_model / rho_early_cdm
    
    # 3. Calculate Sound Speed (c_s = c * sqrt(w))
    # This is the 'effective' sound speed implied by the EOS pressure
    try:
        c_s = C_LIGHT * np.sqrt(w_val)
    except:
        c_s = 0
        
    # 4. Estimate S8 Impact (Heuristic based on Jeans Length)
    # If c_s > 3000 km/s at z=1000, we get suppression.
    # Note: This is an order-of-magnitude check.
    
    return discrepancy_factor, c_s

def run_pincer_sweep():
    print('Phase 2d: The Warm Dark Matter Window Constraint')
    print(f'{"w (EOS)":<10} | {"Early Rho Factor":<20} | {"c_s (km/s)":<15} | {"Verdict"}')
    print('-'*70)
    
    w_values = [0.0, 0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
    
    results = []
    
    for w in w_values:
        factor, c_s = check_w_viability(w)
        
        status = "PASS"
        if factor > 1.1: status = "RISKY (CMB Tension)"
        if factor > 1.5: status = "BROKEN (CMB Violated)"
        
        # S8 Check
        s8_potential = "NO"
        if c_s > 1000: s8_potential = "MAYBE"
        if c_s > 10000: s8_potential = "YES"
        
        print(f'{w:<10.4f} | {factor:<20.4f} | {c_s:<15.0f} | {status} (S8: {s8_potential})')
        results.append((w, factor, c_s))

    # Plot
    w_vals, factors, speeds = zip(*results)
    
    fig, ax1 = plt.subplots(figsize=(10,6))
    
    color = 'tab:red'
    ax1.set_xlabel('Equation of State w')
    ax1.set_ylabel('Early Density Discrepancy (Factor)', color=color)
    ax1.plot(w_vals, factors, color=color, marker='o')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(1.1, color='orange', linestyle='--', label='Tension Threshold')
    ax1.axhline(1.5, color='red', linestyle='--', label='Break Threshold')
    
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Sound Speed (km/s)', color=color)
    ax2.plot(w_vals, speeds, color=color, marker='x', linestyle=':')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('The Warm Dark Matter Pincer: w vs. Consistency')
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase2_w_constraint.png')
    print('Plot saved to output/phase2_w_constraint.png')

if __name__ == '__main__':
    run_pincer_sweep()
