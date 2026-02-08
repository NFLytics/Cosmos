
import numpy as np

from scipy.integrate import odeint

import matplotlib.pyplot as plt

import pandas as pd



# --- COSMOLOGY CONSTANTS (Planck 2018) ---

H0 = 67.4       # km/s/Mpc

Om = 0.315      # Matter density

Ol = 1.0 - Om   # Dark Energy density

Or = 8e-5       # Radiation density (approx)

c_light = 3e5   # km/s



def hubble(a):

    """Hubble parameter H(a) normalized to H0"""

    return np.sqrt(Or/a**4 + Om/a**3 + Ol)



def sound_speed_sdh(a, strength_parameter):

    """

    Calculate sound speed c_s for SDH+ model.

    Phase 1b results suggest a 'pressure' that correlates with sigma.

    We model this as a decaying sound speed: c_s(a) ~ sigma / a

    """

    # Base sound speed in km/s derived from Phase 1b velocity dispersion

    c_s_0 = strength_parameter 

    return c_s_0 / a 



def growth_equation(y, a, model_type='CDM', strength=0.0):

    """

    Solves the Meszaros Equation for structure growth:

    delta'' + (2+H'/H)*delta' - (4*pi*G*rho/H^2)*delta = 0

    Modified with Sound Speed term for SDH+: - (k*cs/aH)^2 * delta

    """

    delta, d_delta = y

    

    # Hubble terms

    H = hubble(a)

    dH = (1/(2*H)) * (-4*Or/a**5 - 3*Om/a**4)

    

    # Friction term

    friction = (3/a + dH/H) * d_delta

    

    # Source term (Gravity)

    # 1.5 * Om / (a^3 * H^2) is the standard gravity driving term

    gravity = 1.5 * Om / (a**3 * H**2) * delta

    

    # Pressure term (The SDH+ Modification)

    pressure = 0

    if model_type == 'SDH':

        # We test a specific scale k (e.g., k=1 h/Mpc, relevant for S8)

        k = 1.0  # h/Mpc

        # Convert k to compatible units

        c_s = sound_speed_sdh(a, strength)

        # Jeans suppression term: -(c_s * k / (a * H * H0))^2 * delta

        # Simplified approximation for the scout script

        pressure = (c_s / (3e5))**2 * k**2 * delta * 1e4 # Scaling factor for visibility

        

    return [d_delta, gravity - friction - pressure]



def run_phase2_scout():

    print('Initializing Phase 2: Cosmological Structure Solver...')

    

    # 1. Load Phase 1b Signal Strength

    try:

        summary = pd.read_csv('output/quality_strict/tables/radial_fits_results_all.csv')

        # Use the mean velocity dispersion (sigma) from the Strict set as the physics anchor

        avg_sigma = summary['v_obs'].mean() * 0.1 # Approximate dispersion component

        print(f'Phase 1b Anchor: Using mean velocity dispersion {avg_sigma:.2f} km/s')

    except:

        avg_sigma = 20.0 # Fallback

        print('Phase 1b Anchor: Defaulting to 20 km/s (Data not found)')



    # 2. Integrate from z=1000 to z=0

    a_range = np.logspace(-3, 0, 500) # Scale factor 0.001 to 1.0

    y0 = [1e-3, 1e-3] # Initial perturbation

    

    # Solve for CDM

    sol_cdm = odeint(growth_equation, y0, a_range, args=('CDM', 0))

    growth_cdm = sol_cdm[:, 0]

    

    # Solve for SDH+

    sol_sdh = odeint(growth_equation, y0, a_range, args=('SDH', avg_sigma))

    growth_sdh = sol_sdh[:, 0]

    

    # 3. Calculate S8 Suppression

    # Normalize to z=1000 match

    ratio = growth_sdh / growth_cdm

    suppression = ratio[-1]

    

    print('-' * 40)

    print(f'RESULTS: Structure Growth (z=0)')

    print(f'CDM Amplitude: {growth_cdm[-1]:.4f}')

    print(f'SDH Amplitude: {growth_sdh[-1]:.4f}')

    print(f'S8 Suppression Factor: {suppression:.4f}')

    print('-' * 40)

    

    if suppression < 0.8:

        print('Implication: STRONG suppression. Solves S8, risks erasing galaxies.')

    elif suppression < 0.98:

        print('Implication: IDEAL suppression. Likely resolves S8 tension.')

    else:

        print('Implication: NEGLIGIBLE suppression. Indistinguishable from CDM.')



    # Plot

    plt.figure(figsize=(10, 6))

    plt.plot(a_range, growth_cdm, label='Standard CDM', linestyle='--')

    plt.plot(a_range, growth_sdh, label=f'SDH+ (sigma={avg_sigma:.1f})')

    plt.title(f'Phase 2 Scout: Linear Structure Growth\nS8 Suppression = {suppression:.3f}')

    plt.xlabel('Scale Factor (a)')

    plt.ylabel('Growth Factor D(a)')

    plt.legend()

    plt.grid(True, alpha=0.3)

    plt.savefig('output/phase2_scout_plot.png')

    print('Plot saved to output/phase2_scout_plot.png')



if __name__ == '__main__':

    run_phase2_scout()

