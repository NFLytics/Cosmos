import numpy as np
from scipy.integrate import odeint
import pandas as pd
import matplotlib.pyplot as plt

H0 = 67.4
OM_PLANCK = 0.315
OL_PLANCK = 0.685
OR_PLANCK = 8e-5
C_LIGHT = 3e5

def get_eos_varying(a, params):
    c_s_val, z_c = params
    z = (1.0/a) - 1.0
    weight = 1.0 / (1.0 + np.exp(4.0 * (z - z_c)))
    c_s = c_s_val * weight
    w = (c_s / C_LIGHT)**2
    return w, c_s

def physics_engine(y, a, k_mode, params):
    rho, d, dd = y
    w, c_s = get_eos_varying(a, params)
    drho_da = -3 * (rho / a) * (1 + w)
    E_sq = (OR_PLANCK / a**4) + rho + OL_PLANCK
    H = H0 * np.sqrt(E_sq)
    pressure = (c_s / H)**2 * (k_mode**2 / a**2) * d
    dH = (H0**2 / (2*H)) * (-4*OR_PLANCK/a**5 + drho_da)
    friction = (3/a + dH/H) * dd
    gravity = 1.5 * rho * (H0 / H)**2 / a**2 * d
    d_dd = gravity - friction - pressure
    return [drho_da, dd, d_dd]

def run_fine_tune():
    print('Phase 3e: 2D Parameter Sweep (Speed vs. Timing)')
    cs_range = [30, 40, 50, 60, 80]
    z_range = [3.0, 2.0, 1.5, 1.0, 0.7, 0.5, 0.2]
    a_range = np.logspace(-3, 0, 400)
    rho_init = OM_PLANCK * (a_range[0])**-3 
    y0 = [rho_init, 1e-3, 1e-3]
    
    sol_cdm = odeint(physics_engine, y0, a_range, args=(1.0, (0.0, 10.0)))
    growth_cdm = sol_cdm[-1, 1]
    
    results = []
    print(f'{"Speed":<10} | {"z_c":<10} | {"S8":<10} | {"Dwarf":<10} | {"Status"}')
    
    for z_c in z_range:
        for c_s in cs_range:
            params = (c_s, z_c)
            growth_s8 = odeint(physics_engine, y0, a_range, args=(0.7, params))[-1, 1]
            growth_dwarf = odeint(physics_engine, y0, a_range, args=(10.0, params))[-1, 1]
            r_s8 = growth_s8 / growth_cdm
            r_dwarf = growth_dwarf / growth_cdm
            
            status = "FAIL"
            if r_dwarf > 0.5:
                if 0.90 <= r_s8 <= 0.98:
                    status = "!!! UNIFIED !!!"
                elif r_s8 < 0.90:
                    status = "S8 Strong"
                else:
                    status = "S8 Weak"
            else:
                status = "Dwarf Death"
            
            print(f'{c_s:<10} | {z_c:<10} | {r_s8:<10.4f} | {r_dwarf:<10.4f} | {status}')
            results.append({'cs': c_s, 'z_c': z_c, 's8': r_s8, 'dwarf': r_dwarf})
            
    df = pd.DataFrame(results)
    df.to_csv('output/fine_tune_results.csv', index=False)

if __name__ == '__main__':
    run_fine_tune()
