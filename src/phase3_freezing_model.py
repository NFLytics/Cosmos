
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

    """

    Model: Cold Gas -> Superfluid Condensate

    Physics: Pressure turns ON only at late times (Low z).

    """

    z = (1.0/a) - 1.0

    

    # Phase Transition centered at Cosmic Noon (z=3.0)

    z_c = 3.0

    

    # Sigmoid Activation

    # High z (early) -> weight = 0 (CDM)

    # Low z (late)  -> weight = 1 (Superfluid)

    weight = 1.0 / (1.0 + np.exp(2.0 * (z - z_c)))

    

    # Sound Speed Profile

    # It pulses to 'peak_cs' then settles.

    # We model the 'Condensate Fraction' determines the effective sound speed.

    c_s = peak_cs * weight

    

    # Equation of State w ~ (c_s/c)^2

    w = (c_s / C_LIGHT)**2

    return w, c_s



def physics_engine(y, a, k_mode, peak_cs):

    rho, d, dd = y

    w, c_s = get_eos_freezing(a, peak_cs)

    

    drho_da = -3 * (rho / a) * (1 + w)

    

    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK

    H = H0 * np.sqrt(E_sq)

    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)

    

    # CORRECTED JEANS PRESSURE

    # (c_s/H)^2 * (k/a)^2 * delta

    # Pressure only exists when c_s > 0 (Late times)

    pressure = (c_s / H)**2 * (k_mode**2 / a**2) * d

    

    friction = (3/a + dH/H) * dd

    gravity = 1.5 * rho * (H0 / H)**2 / a**2 * d

    

    d_dd = gravity - friction - pressure

    return [drho_da, dd, d_dd]



def run_cold_start_test():

    print('Phase 3c: The Freezing Dark Matter Test')

    print('Hypothesis: Late-Time Condensation (z < 3)')

    print('Goal: Preserves Dwarfs (k=10) while suppressing S8 (k=0.7)')

    print('-'*65)

    print(f'{"Peak c_s":<12} | {"S8 (k=0.7)":<12} | {"Dwarf (k=10)":<12} | {"Verdict"}')

    print('-'*65)

    

    # Sweep through high sound speeds since they act for a shorter duration

    cs_sweep = [10000, 7000, 5000, 3000, 1500, 1000, 500]

    

    a_range = np.logspace(-3, 0, 400)

    rho_init = OM_PLANCK * (a_range[0])**-3 

    y0 = [rho_init, 1e-3, 1e-3]

    

    # CDM Baseline (c_s = 0)

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

        

        status = "FAIL"

        if 0.90 <= r_s8 <= 0.99 and r_dwarf > 0.5:

            status = "SOLUTION"

        elif r_s8 < 0.90: status = "TOO STRONG"

        elif r_s8 > 0.99: status = "TOO WEAK"

        

        print(f'{c_s:<12} | {r_s8:<12.4f} | {r_dwarf:<12.4f} | {status}')

        results.append((c_s, r_s8, r_dwarf))

        

    # Plot

    cs_vals, s8s, dwarfs = zip(*results)

    plt.figure(figsize=(10,6))

    plt.semilogx(cs_vals, s8s, 'o-', color='purple', label='S8 (k=0.7) [Target: 0.95]')

    plt.semilogx(cs_vals, dwarfs, 's-', color='orange', label='Dwarfs (k=10) [Target: >0.5]')

    

    plt.axhspan(0.90, 0.98, color='green', alpha=0.1)

    plt.axhline(0.5, color='red', linestyle='--', label='Dwarf Survival Line')

    plt.axhline(1.0, color='black', linestyle=':')

    

    plt.xlabel('Late-Time Sound Speed (km/s)')

    plt.ylabel('Power Suppression Ratio (USDM/CDM)')

    plt.title('Freezing Model: Late Condensation at z=3')

    plt.legend()

    plt.grid(True, alpha=0.3)

    plt.savefig('output/phase3_freezing.png')

    print('Plot saved to output/phase3_freezing.png')



if __name__ == '__main__':

    run_cold_start_test()

