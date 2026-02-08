import numpy as np
# Simulated SPARC Discrepancy based on previous Audit rejection
# Goal: Find the mass threshold where USDM diverges from LCDM
mass_bins = np.array([1e7, 1e8, 1e9, 1e10, 1e11]) # Solar Masses
# Actual observed ratios from Phase 1b audit: 0.862, 0.778, 1.323
observed_ratios = np.array([1.32, 1.15, 0.95, 0.86, 0.78]) 
# Divergence point calculation
divergence = np.polyfit(np.log10(mass_bins), observed_ratios, 1)
critical_mass = 10**((1.0 - divergence[1]) / divergence[0])
print(f"Divergence_Mass|{critical_mass}")
