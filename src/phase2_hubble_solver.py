import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONSTANTS ---
# Standard LambdaCDM (Planck 2018)
H0_PLANCK = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5 # Radiation

# Local Measurement (SH0ES)
H0_SHOES = 73.0

def equation_of_state(a, z_c):
    """
    If DM is 'Hot' (High Sound Speed), it likely has non-zero pressure.
    w = P / rho. 
    Relativistic: w = 1/3
    Cold: w = 0
    Transition at z_c (a_c).
    """
    a_c = 1.0 / (1.0 + z_c)
    
    # Sigmoid transition centered at a_c
    width = 0.1 * a_c
    try:
        x = (a - a_c) / width
        weight = 1.0 / (1.0 + np.exp(-x)) # 0 at early, 1 at late
    except:
        weight = 1.0 if a > a_c else 0.0
        
    # Early Universe: w ~ 1/3 (Hot)
    # Late Universe: w = 0 (Cold)
    # Note: We scale the early w to be conservative. w=1/3 is full radiation. 
    # Let's test a 'Warm' EOS (w=0.05) vs 'Hot' (w=0.33)
    w_early = 0.10 # Conservative 'Warm' fluid approximation
    
    return w_early * (1 - weight)

def rho_evolution(y, a, z_c):
    """
    Solves conservation equation: d(rho)/da = -3 * (rho/a) * (1 + w)
    """
    rho = y[0]
    w = equation_of_state(a, z_c)
    drho_da = -3 * (rho / a) * (1 + w)
    return drho_da

def run_hubble_check():
    print('Phase 2c: Hubble Tension Consistency Check')
    print(f'Testing Global Phase Transition at z_c = 1.0')
    
    z_c = 1.0
    a_range = np.linspace(1e-4, 1.0, 1000)
    
    # 1. Integrate Density Evolution
    # Start matching Planck density at z=1000 (recombination anchor)
    rho_init = OM_PLANCK * (1e-4)**-3 
    
    sol = odeint(rho_evolution, [rho_init], a_range, args=(z_c,))
    rho_dm_evolved = sol[:, 0]
    
    # Standard CDM density for comparison
    rho_cdm_std = OM_PLANCK * a_range**-3
    
    # 2. Calculate H(z)
    # H(a) = H0 * sqrt( rho_rad + rho_m + rho_lambda )
    # We normalize such that E(a) = H(a)/H0
    
    # Note: If rho_dm decays faster (w>0), we need MORE of it early on 
    # to match CMB, or we end up with LESS of it today.
    # Let's assume we match the observed density TODAY (rho_0) and work backward.
    
    # RE-RUN Integrating BACKWARDS from a=1
    a_range_rev = np.linspace(1.0, 1e-4, 1000)
    rho_0 = OM_PLANCK
    sol_rev = odeint(rho_evolution, [rho_0], a_range_rev, args=(z_c,))
    rho_dm_backward = sol_rev[:, 0]
    
    # Flip back
    a_vals = a_range_rev[::-1]
    rho_vals = rho_dm_backward[::-1]
    
    # Calculate Hubble Parameter H(z)
    # E^2 = Or/a^4 + Rho_DM(a) + Ol
    E_sq = (OR_PLANCK / a_vals**4) + rho_vals + OL_PLANCK
    H_vals = H0_PLANCK * np.sqrt(E_sq)
    
    # 3. Calculate Age of Universe
    # t = Integral ( da / (a * H(a)) )
    integrand = 1.0 / (a_vals * H_vals)
    # Simple trapz integration
    age_seconds = np.trapz(integrand, x=a_vals) * 3.086e19 # Mpc to km conversion approx
    age_gyr = age_seconds / (365*24*3600*1e9) 
    # Correction for units (1/H0 is in Mpc/(km/s))
    # 1/H0 ~ 977.8 / h Gyr. 
    # We sum E_inv * da/a. 
    # Let's use simpler metric: H0_derived
    
    # CHECK: Does this change the Sound Horizon scale? 
    # If expansion was faster early on (because w>0 implies more density needed back then?), 
    # H0 today might need to shift to match CMB angular scale.
    
    print('-' * 40)
    print(f'Model: Transition at z={z_c} (Warm EOS w=0.1)')
    print(f'Impact on Late-Time Density: {rho_vals[-1] / OM_PLANCK:.4f} (Should be 1.0)')
    print(f'Impact on Early-Time Density: {rho_vals[0] / (OM_PLANCK*1e12):.4f}')
    
    if rho_vals[0] > (OM_PLANCK * a_vals[0]**-3) * 1.5:
        print('CRITICAL WARNING: Early universe density is too high.')
        print('To match z=0 density, you need massive amounts of DM early on.')
        print('This breaks the CMB peaks.')
        status = 'BROKEN'
    elif rho_vals[0] < (OM_PLANCK * a_vals[0]**-3) * 0.8:
        print('CRITICAL WARNING: Early universe density is too low.')
        status = 'BROKEN'
    else:
        print('STATUS: Density evolution is plausible.')
        status = 'PLAUSIBLE'

    print(f'Verdict: {status}')
    print('-' * 40)
    
    # Plot
    plt.figure(figsize=(10,6))
    plt.loglog(a_vals, rho_vals, label='SDH+ Density')
    plt.loglog(a_vals, OM_PLANCK * a_vals**-3, '--', label='Standard CDM')
    plt.xlabel('Scale Factor a')
    plt.ylabel('Density rho')
    plt.title(f'Phase 2c: Does a z={z_c} Transition Break the Universe?')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase2_hubble_check.png')
    print('Plot saved to output/phase2_hubble_check.png')

if __name__ == '__main__':
    run_hubble_check()
