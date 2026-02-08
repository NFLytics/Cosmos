import numpy as np
def friction_ode(y, a, kJ, friction_coeff):
    # Added term: -friction_coeff * y[1] to simulate drag within the superfluid
    term2 = ((3.0 / (2.0 * a)) + friction_coeff) * y[1]
    term3 = (3.0 / (2.0 * a**2)) * (1.0 - (1.0e-24**2 / kJ**2)) * y[0]
    return np.array([y[1], term3 - term2])

a = 0.001; delta = a; d_delta = 1.0; kJ = 3.337e-23; h = 0.001; drag = 0.05
for _ in range(1000):
    k1 = h * friction_ode([delta, d_delta], a, kJ, drag)
    k2 = h * friction_ode([delta + 0.5*k1[0], d_delta + 0.5*k1[1]], a + 0.5*h, kJ, drag)
    delta += k2[0]; d_delta += k2[1]; a += h
print(f"Friction_Growth|{delta/a}")
