"""
RAR (Radial Acceleration Relation) Fitting

Implements McGaugh MOND formula:
g_obs = g_bar / (1 - exp(-sqrt(g_bar / a0)))

Provides fitting utilities and statistical tests.
"""

import numpy as np
import logging
from scipy.optimize import minimize, brentq
from scipy.stats import chi2, norm
from typing import Tuple, Dict, Optional

# Optional GPU support
try:
    from .onnx_engine import ONNXComputeEngine
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

logger = logging.getLogger(__name__)

class RARFormula:
    """McGaugh MOND Radial Acceleration Relation"""
    
    @staticmethod
    def g_obs_from_g_bar(g_bar: np.ndarray, a0: float, engine: Optional['ONNXComputeEngine'] = None) -> np.ndarray:
        """
        Compute observed acceleration from baryonic acceleration.
        
        g_obs = g_bar / (1 - exp(-sqrt(g_bar / a0)))
        
        Args:
            g_bar: Baryonic acceleration (m/s²)
            a0: MOND scale (m/s²)
            engine: Optional ONNXComputeEngine for GPU acceleration
        
        Returns:
            Observed acceleration (m/s²)
        """
        if engine is not None:
            return engine.compute_rar(g_bar, a0)

        # CPU implementation (fallback)
        # Prevent numerical issues
        sqrt_term = np.sqrt(np.clip(g_bar / a0, 0, 1e3))
        
        # Compute RAR
        denominator = 1 - np.exp(-sqrt_term)
        
        # Handle edge cases
        with np.errstate(divide='ignore', invalid='ignore'):
            g_obs = g_bar / denominator
        
        # Replace invalid with original
        g_obs = np.where(np.isfinite(g_obs), g_obs, g_bar)
        
        return g_obs
    
    @staticmethod
    def mond_regime(g_bar: np.ndarray, a0: float) -> np.ndarray:
        """
        Check if points are in MOND regime (g_bar << a0).
        
        Returns:
            Boolean array indicating MOND regime
        """
        return g_bar < (0.1 * a0)  # Deep MOND: g_bar < 0.1 * a0


class RARFitter:
    """Fit RAR formula to rotation curve data"""
    
    def __init__(self, a0_bounds: Tuple[float, float] = (1e-12, 1e-8), use_gpu: bool = False):
        """
        Initialize RAR fitter.
        
        Args:
            a0_bounds: Bounds on a0 parameter (m/s²)
            use_gpu: Whether to use ONNX-CUDA acceleration
        """
        self.a0_bounds = a0_bounds
        self.a0_ref = 1.2e-10  # McGaugh reference value
        self.engine = None
        
        if use_gpu and HAS_ONNX:
            try:
                self.engine = ONNXComputeEngine()
                logger.info("RARFitter initialized with ONNX-CUDA acceleration.")
            except Exception as e:
                logger.warning(f"Failed to initialize GPU engine: {e}. Falling back to CPU.")
    
    def fit_to_data(self, g_bar: np.ndarray, g_obs: np.ndarray, 
                    g_obs_error: Optional[np.ndarray] = None,
                    a0_initial: Optional[float] = None) -> Dict:
        """
        Fit RAR formula to data points.
        
        Args:
            g_bar: Baryonic acceleration (m/s²)
            g_obs: Observed acceleration (m/s²)
            g_obs_error: Uncertainty in g_obs (optional, default 5%)
            a0_initial: Initial guess for a0
        
        Returns:
            Dictionary with keys:
            - a0: Best-fit MOND scale
            - a0_error: Uncertainty in a0
            - chi2_reduced: Reduced chi-squared
            - n_points: Number of fitted points
            - success: Convergence flag
        """
        # Handle errors
        if g_obs_error is None:
            g_obs_error = 0.05 * g_obs
        
        # Ensure arrays
        g_bar = np.atleast_1d(g_bar)
        g_obs = np.atleast_1d(g_obs)
        g_obs_error = np.atleast_1d(g_obs_error)
        
        # Remove invalid points
        valid = np.isfinite(g_obs) & np.isfinite(g_bar) & (g_obs > 0) & (g_bar > 0)
        if np.sum(valid) < 3:
            return {
                'success': False,
                'reason': 'Insufficient valid data points'
            }
        
        g_bar = g_bar[valid]
        g_obs = g_obs[valid]
        g_obs_error = g_obs_error[valid]
        
        # Define chi-squared function in log-space
        def chi2_func_log(log_a0):
            a0 = 10**log_a0
            g_pred = RARFormula.g_obs_from_g_bar(g_bar, a0, engine=self.engine)
            chi2 = np.sum((g_obs - g_pred) ** 2 / g_obs_error ** 2)
            return chi2
        
        # Initial guess in log-space
        if a0_initial is None:
            a0_initial = self.a0_ref
        log_a0_initial = np.log10(a0_initial)
        
        # Bounds in log-space
        log_a0_bounds = (np.log10(self.a0_bounds[0]), np.log10(self.a0_bounds[1]))
        
        # Use a small grid search to find a better initial guess
        logger.debug(f"Starting grid search for {len(g_bar)} points...")
        best_chi2_grid = np.inf
        best_log_a0_grid = log_a0_initial
        
        for trial_log_a0 in np.linspace(log_a0_bounds[0], log_a0_bounds[1], 20):
            c = chi2_func_log(trial_log_a0)
            if c < best_chi2_grid:
                best_chi2_grid = c
                best_log_a0_grid = trial_log_a0
        
        # Minimize from best grid point
        try:
            result = minimize(chi2_func_log, x0=best_log_a0_grid,
                            bounds=[log_a0_bounds],
                            method='L-BFGS-B',
                            options={'ftol': 1e-15, 'gtol': 1e-15})
            
            log_a0_best = result.x[0]
            a0_best = 10**log_a0_best
            chi2_best = result.fun
            
        except Exception as e:
            logger.error(f"Fitting failed: {e}")
            return {'success': False, 'reason': str(e)}
        
        # Estimate error (in log-space first, then convert)
        try:
            # Hessian approximation in log-space
            # Increased h from 1e-4 to 1e-2 for stability with float32 ONNX
            h = 1e-2 if self.engine else 1e-4
            c1 = chi2_func_log(log_a0_best + h)
            c0 = chi2_func_log(log_a0_best)
            cm1 = chi2_func_log(log_a0_best - h)
            d2chi2_log = (c1 - 2*c0 + cm1) / (h**2)
            
            if d2chi2_log > 0:
                log_a0_error = 1.0 / np.sqrt(d2chi2_log)
                # Convert log error to linear error: Δa0 ≈ a0 * ln(10) * Δlog_a0
                a0_error = a0_best * np.log(10) * log_a0_error
            else:
                a0_error = np.inf
            
            logger.debug(f"Fit result: a0={a0_best:.3e}, chi2={chi2_best:.2f}, log_a0_err={log_a0_error if 'log_a0_error' in locals() else 'inf'}")
        except Exception as e:
            logger.debug(f"Error estimation failed: {e}")
            a0_error = np.inf
        
        # Reduced chi-squared
        dof = len(g_bar) - 1
        chi2_reduced = chi2_best / dof if dof > 0 else chi2_best
        
        return {
            'a0': a0_best,
            'a0_error': a0_error,
            'chi2_reduced': chi2_reduced,
            'chi2': chi2_best,
            'n_points': len(g_bar),
            'dof': dof,
            'success': result.success,
        }
    
    def fit_with_bootstrap(self, g_bar: np.ndarray, g_obs: np.ndarray,
                          g_obs_error: np.ndarray,
                          n_bootstrap: int = 100) -> Dict:
        """
        Fit RAR with bootstrap resampling for robust error estimation.
        
        Args:
            g_bar, g_obs, g_obs_error: Data
            n_bootstrap: Number of bootstrap samples
        
        Returns:
            Dictionary with bootstrap statistics
        """
        a0_samples = []
        
        np.random.seed(42)
        for i in range(n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(len(g_bar), size=len(g_bar), replace=True)
            g_bar_boot = g_bar[indices]
            g_obs_boot = g_obs[indices]
            err_boot = g_obs_error[indices]
            
            # Fit
            result = self.fit_to_data(g_bar_boot, g_obs_boot, err_boot)
            if result['success']:
                a0_samples.append(result['a0'])
        
        if len(a0_samples) == 0:
            return {'success': False, 'reason': 'All bootstrap fits failed'}
        
        a0_samples = np.array(a0_samples)
        
        return {
            'a0_mean': np.mean(a0_samples),
            'a0_median': np.median(a0_samples),
            'a0_std': np.std(a0_samples),
            'a0_lower': np.percentile(a0_samples, 16),
            'a0_upper': np.percentile(a0_samples, 84),
            'n_successful': len(a0_samples),
            'success': True,
        }


def compute_scale_dependence_statistic(a0_inner: float, a0_inner_err: float,


                                      a0_outer: float, a0_outer_err: float) -> Dict:


    """


    Compute significance of a0 difference between inner and outer regions.


    """


    # Handle edge cases


    if a0_outer <= 0 or a0_inner <= 0:


        return {'success': False, 'reason': 'Non-positive a0 values'}


    


    # Compute ratio


    ratio = a0_inner / a0_outer


    


    # Error propagation: Δ(a/b) = (a/b) * sqrt((Δa/a)² + (Δb/b)²)


    if np.isfinite(a0_inner_err) and np.isfinite(a0_outer_err) and a0_inner_err > 0 and a0_outer_err > 0:


        rel_err_inner = a0_inner_err / a0_inner


        rel_err_outer = a0_outer_err / a0_outer


        ratio_err = ratio * np.sqrt(rel_err_inner**2 + rel_err_outer**2)


        z_score = (ratio - 1.0) / ratio_err if ratio_err > 0 else 0


    else:


        ratio_err = np.inf


        z_score = 0


    


    # P-value (one-tailed test for ratio > 1)


    p_value = 1 - norm.cdf(z_score) if np.isfinite(z_score) else 1.0


    


    # Interpretation


    if z_score > 3.0:


        interpretation = "STRONG EVIDENCE (>3σ) for a0_inner > a0_outer [SDH+]"


    elif z_score > 2.0:


        interpretation = "SIGNIFICANT (>2σ) evidence for a0_inner > a0_outer [SDH+]"


    elif z_score > 1.0:


        interpretation = "MARGINAL (>1σ) evidence for a0_inner > a0_outer"


    elif z_score > 0:


        interpretation = "Slight excess of a0_inner > a0_outer (not significant)"


    else:


        interpretation = "Consistent with ΛCDM (a0_inner ≈ a0_outer)"


    


    return {


        'ratio': ratio,


        'ratio_err': ratio_err,


        'z_score': z_score,


        'p_value': p_value,


        'interpretation': interpretation,


        'success': True,


    }

