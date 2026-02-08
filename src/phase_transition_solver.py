
import numpy as np

from scipy.integrate import odeint

import matplotlib.pyplot as plt



# --- CONSTANTS ---

Om = 0.315

Ol = 1.0 - Om

Or = 8e-5

H0 = 67.4



def hubble(a):

    return np.sqrt(Or/a**4 + Om/a**3 + Ol)



def sound_speed_evolving(a, z_c, width=0.1):

    """

    Models a Phase Transition from Hot (Normal) to Cold (Superfluid).

    High c_s in early universe (a < a_c).

    Low c_s in late universe (a > a_c).

    """

    if z_c <= -1.0: return 30.0 # Fail-safe for invalid inputs

    

    a_c = 1.0 / (1.0 + z_c)

    

    # Target Speeds (km/s)

    c_s_hot = 350.0  # From Phase 2 Inverse Result

    c_s_cold = 30.0  # From Phase 1b Strict Result

    

    # Logistic Transition Function

    # Early Universe (a << a_c): weight -> 0 -> c_s_hot

    # Late Universe (a >> a_c): weight -> 1 -> c_s_cold

    try:

        # Prevent overflow in exp

        arg = -(a - a_c) / (width * a_c)

        arg = np.clip(arg, -50, 50) 

        weight = 1.0 / (1.0 + np.exp(arg))

    except:

        weight = 0.5

    

    c_s = c_s_hot * (1 - weight) + c_s_cold * weight

    return c_s



def growth_equation(y, a, z_c):

    d, dd = y

    H = hubble(a)

    dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)

    k = 1.0 # Scale of interest (S8)

    

    # Evolving Pressure Term

    c_s = sound_speed_evolving(a, z_c)

    pressure = (c_s / 3e5)**2 * k**2 * d * 5e3 

    

    friction = (3/a + dH/H) * dd

    gravity = 1.5 * Om / (a**3 * H**2) * d

    

    return [dd, gravity - friction - pressure]



def run_transition_solver():

    print('Phase 2b: Phase Transition Epoch Solver')

    print('Testing Critical Redshifts (z_c) to bridge the 300 km/s -> 30 km/s Gap.')

    

    a_range = np.logspace(-3, 0, 500)

    y0 = [1e-3, 1e-3]



    # 1. Baseline CDM (Pure Gravity)

    def cdm_eq(y, a):

        d, dd = y

        H = hubble(a)

        dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)

        return [dd, 1.5 * Om / (a**3 * H**2) * d - (3/a + dH/H) * dd]

    

    sol_base = odeint(cdm_eq, y0, a_range)

    growth_cdm = sol_base[-1, 0]

    print(f'CDM Baseline Growth Amplitude: {growth_cdm:.4f}')



    # 2. Sweep Critical Redshifts

    z_transitions = [15.0, 10.0, 5.0, 3.0, 2.0, 1.5, 1.0, 0.5]

    

    print(f'{"z_crit":<10} | {"S8 Suppression":<15} | {"Status"}')

    print('-'*45)

    

    results = []

    

    for z_c in z_transitions:

        sol = odeint(growth_equation, y0, a_range, args=(z_c,))

        growth_sdh = sol[-1, 0]

        suppression = growth_sdh / growth_cdm

        

        status = "FAIL"

        if 0.90 <= suppression <= 0.96: status = "OPTIMAL"

        elif suppression < 0.90: status = "TOO STRONG"

        elif suppression > 0.98: status = "INEFFECTIVE"

        

        print(f'{z_c:<10.1f} | {suppression:<15.4f} | {status}')

        results.append((z_c, suppression))



    # Plot

    z_vals, s_vals = zip(*results)

    plt.figure(figsize=(10,6))

    plt.plot(z_vals, s_vals, marker='o', lw=2, color='purple')

    plt.axhspan(0.90, 0.96, color='green', alpha=0.2, label='Target S8 Zone')

    plt.axhline(1.0, color='red', linestyle='--', label='CDM Baseline')

    plt.gca().invert_xaxis() # High z on left

    plt.xlabel('Critical Redshift (z_c)')

    plt.ylabel('S8 Suppression Factor')

    plt.title('Phase 2b: When did the Universe Superfluidize?')

    plt.legend()

    plt.grid(True, alpha=0.3)

    plt.savefig('output/phase2_transition_sweep.png')

    print('Plot saved to output/phase2_transition_sweep.png')



if __name__ == '__main__':

    run_transition_solver()

