import sys
from pathlib import Path
sys.path.insert(0, '')
from src.sparc_loader import SPARCRotationCurves
from src.rar_fitting import RARFitter, RARFormula
import numpy as np

sparc = SPARCRotationCurves('data/raw_sparc')
gal_data = sparc.extract_galaxy_profile('CamB')
fitter = RARFitter()

g_bar = gal_data['g_bar']
g_obs = gal_data['g_obs']
g_obs_err = gal_data['errors']['g_obs']

print(f"Galaxy CamB: {len(g_bar)} points")
print(f"g_bar range: {g_bar.min():.2e} to {g_bar.max():.2e}")
print(f"g_obs range: {g_obs.min():.2e} to {g_obs.max():.2e}")

a0_vals = np.logspace(-12, -8, 20)
for a0 in a0_vals:
    g_pred = RARFormula.g_obs_from_g_bar(g_bar, a0)
    chi2 = np.sum((g_obs - g_pred)**2 / g_obs_err**2)
    print(f"a0={a0:.2e}, chi2={chi2:.2f}")

fit = fitter.fit_to_data(g_bar, g_obs, g_obs_err)
print(f"Fit result: a0={fit['a0']:.2e}, success={fit['success']}")
