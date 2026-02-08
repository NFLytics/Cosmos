import numpy as np
from scipy.optimize import minimize

# The Objective Function: Total System Loss
def objective(params):
    m_s, fraction = params # mass exponent, mass fraction
    # 1. Cosmological Loss (Targeting 8.5% suppression)
    # FDM suppression scales roughly as fraction * (m/10^-22)^-0.5
    suppression = (2.81 * (1-fraction)) + (19.0 * fraction * (10**m_s / 1e-22)**-0.5)
    l_cosmo = (suppression - 8.5)**2
    
    # 2. Galactic Loss (Targeting 1.0 Ratio at 1.22B M_sun)
    # Soliton stiffness vs Baryonic pressure
    l_galaxy = ( (fraction * (10**m_s / 1e-22)**-1) - 0.106)**2
    
    return l_cosmo + l_galaxy

# Initial Guess: [log10(mass), fraction]
res = minimize(objective, x0=[-22, 0.3], bounds=[(-25, -18), (0.01, 0.99)], method='L-BFGS-B')
print(f"Optimal_Mass_Exp|{res.x[0]}")
print(f"Optimal_Fraction|{res.x[1]}")
print(f"Convergence_Loss|{res.fun}")
