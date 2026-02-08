import numpy as np
# Natural Constants
H0 = 67.4 / 3.086e19 # s^-1
rho_c = 8.5e-27 # kg/m^3
m_boson = 2.8349 * 1.782e-36 # kg
# Standardized Sound Speed (no scaling)
cs = 80000 # m/s 
# Re-calculating Jeans scale k_J = (a/cs) * sqrt(4 * pi * G * rho)
k_J = (1.0 / cs) * np.sqrt(4 * np.pi * 6.674e-11 * rho_c)
print(f"Standardized_kJ|{k_J}")
