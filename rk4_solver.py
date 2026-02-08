import numpy as np
def growth_ode(y, a, kJ):
    # y[0] = delta, y[1] = d(delta)/da
    # Simplified LCDM + Superfluid Pressure: d2_delta/da2 + (3/2a)d_delta/da - (3/2a^2)(1 - k^2/kJ^2)delta = 0
    k = 1.0e-24 # Targeted k-mode
    term2 = (3.0 / (2.0 * a)) * y[1]
    term3 = (3.0 / (2.0 * a**2)) * (1.0 - (k**2 / kJ**2)) * y[0]
    return np.array([y[1], term3 - term2])

# RK4 Step
a = 0.001; delta = a; d_delta = 1.0; kJ = 3.337e-23; h = 0.001
for _ in range(1000):
    k1 = h * growth_ode([delta, d_delta], a, kJ)
    k2 = h * growth_ode([delta + 0.5*k1[0], d_delta + 0.5*k1[1]], a + 0.5*h, kJ)
    delta += k2[0]; d_delta += k2[1]; a += h
print(f"True_Growth|{delta/a}")
