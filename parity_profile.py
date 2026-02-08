import numpy as np
# Isolated Sidekick Physics
m_sidekick = 1e-22
# Calculate the Soliton-to-Halo Mass Ratio (Parity Test)
# For FDM: M_soliton ~ (m/10^-22)^-1 * (M_halo/10^12)^1/3 
m_ratio = (m_sidekick / 1e-22)**-1 * (1.22e9 / 1e12)**(1/3)
# S8 Suppression in Isolation (No 2.83 eV anchor)
s8_iso = 19.0 * (m_sidekick / 1e-22)**-0.5
print(f"Parity_Mass_Ratio|{m_ratio}")
print(f"Isolated_S8_Suppression|{s8_iso}")
