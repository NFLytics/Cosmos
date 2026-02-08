import numpy as np
m1 = 2.8349 # Superfluid
m2 = 1e-22 # Fuzzy Component
ratio = 0.3 # 30% Fuzzy, 70% Superfluid
# Combined Suppression Calculation
suppression = (2.81 * (1-ratio)) + (19.0 * ratio) 
print(f"Hybrid_Suppression|{suppression}")
