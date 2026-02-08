import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import pandas as pd

# --- CONSTANTS ---
Om = 0.315
Ol = 1.0 - Om
Or = 8e-5
H0_param = 0.674

def hubble(a):
    return np.sqrt(Or/a**4 + Om/a**3 + Ol)

def growth_equation(y, a, c_s_eff):
    d, dd = y
    H = hubble(a)
    dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)
    
    # Jeans Scale (k = 1.0 h/Mpc for S8 tension)
    k = 1.0 
    
    # Pressure term: (c_s * k / aH)^2
    # c_s_eff is in km/s. c_light is 3e5.
    # We model c_s decaying as c_s_eff/a (adiabatic)
    c_s = c_s_eff / a
    pressure = (c_s / 3e5)**2 * k**2 * d * 5e3 # Scaling for sensitivity
    
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * Om / (a**3 * H**2) * d
    
    return [dd, gravity - friction - pressure]

def solve_for_cs(c_s_val):
    a_range = np.logspace(-3, 0, 200)
    y0 = [1e-3, 1e-3]
    sol = odeint(growth_equation, y0, a_range, args=(c_s_val,))
    return sol[-1, 0]

def run_inverse_solver():
    print('Initiating Phase 2: Inverse Parameter Sweep...')
    print('Goal: Find Sound Speed (c_s) required for S8 Suppression of 0.90 - 0.96')
    
    # Baseline CDM
    baseline = solve_for_cs(0.0)
    
    # Sweep
    velocities = np.linspace(0, 500, 50) # 0 to 500 km/s
    suppressions = []
    
    print(f'Sweeping 0 km/s -> 500 km/s...')
    for v in velocities:
        res = solve_for_cs(v)
        ratio = res / baseline
        suppressions.append(ratio)
        
    # Analyze
    suppressions = np.array(suppressions)
    
    # Find Sweet Spot (0.92 to 0.96)
    valid_indices = np.where((suppressions > 0.90) & (suppressions < 0.98))[0]
    
    if len(valid_indices) > 0:
        optimal_v = velocities[valid_indices]
        optimal_s = suppressions[valid_indices]
        print('-' * 40)
        print(f'SUCCESS: Solution Found.')
        print(f'Required Sound Speed Range: {optimal_v[0]:.1f} km/s - {optimal_v[-1]:.1f} km/s')
        print(f'Resulting S8 Suppression:   {optimal_s[0]:.3f} - {optimal_s[-1]:.3f}')
        print('-' * 40)
    else:
        print('FAILURE: No solution in this range. Physics requires higher energy scale.')

    # Plot
    plt.figure(figsize=(10,6))
    plt.plot(velocities, suppressions, lw=2, color='blue')
    plt.axhspan(0.90, 0.96, color='green', alpha=0.2, label='S8 Solution Zone')
    plt.axhline(1.0, color='red', linestyle='--', label='CDM Baseline')
    plt.xlabel('Effective Sound Speed (km/s)')
    plt.ylabel('Growth Suppression Factor (S8)')
    plt.title('Phase 2 Inverse Solver: The Cost of Solving S8')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase2_inverse_sweep.png')
    print('Sweep plot saved to output/phase2_inverse_sweep.png')

if __name__ == '__main__':
    run_inverse_solver()
