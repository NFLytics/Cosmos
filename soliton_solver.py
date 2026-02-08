import numpy as np
# Variables based on the 1.22B Divergence Mass
M_crit = 1.22e9 
m_ev = 2.8349
# Soliton Core Radius (Schive et al. scaling)
# r_c ~ 1.6 * (m_ev)^-1 * (M_halo/10^9)^-1/3 kpc
r_c = 1.6 * (1/m_ev) * (M_crit/1e9)**(-1/3)
# Quantum Pressure Contribution: P_q = (hbar^2 / 2m^2) * laplacian(sqrt(rho)) / sqrt(rho)
# We model the back-reaction factor as a function of the core density
back_reaction = np.log10(M_crit) * (r_c / 1.0) * 0.15 # 0.15 is the non-linear coupling
print(f"Soliton_Boost|{back_reaction}")
