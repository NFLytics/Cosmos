"""
Radial-Dependent RAR Analysis

Fits RAR separately to inner and outer regions of each galaxy.
Tests SDH+ vs ΛCDM hypotheses.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
from .rar_fitting import RARFitter, compute_scale_dependence_statistic

logger = logging.getLogger(__name__)

class RadialDependenceAnalyzer:
    """Analyze scale-dependence of RAR within galaxies"""
    
    def __init__(self, n_radial_bins: int = 2):
        """
        Initialize analyzer.
        
        Args:
            n_radial_bins: Number of radial bins (default 2: inner/outer)
        """
        self.n_bins = n_radial_bins
        self.fitter = RARFitter()
    
    def analyze_galaxy(self, galaxy_data: Dict, galaxy_name: str = "Unknown") -> Optional[Dict]:
        """
        Analyze radial dependence for single galaxy.
        
        Args:
            galaxy_data: Dictionary with keys r, v_circ, g_bar, g_obs, errors
            galaxy_name: Galaxy identifier (for logging)
        
        Returns:
            Dictionary with radial bins and a0 fits, or None if analysis fails
        """
        r = galaxy_data['r']
        g_bar = galaxy_data['g_bar']
        g_obs = galaxy_data['g_obs']
        errors = galaxy_data['errors']
        
        # Determine radial bin edges
        r_min, r_max = r.min(), r.max()
        r_edges = np.linspace(r_min, r_max, self.n_bins + 1)
        
        bin_results = {
            'galaxy': galaxy_name,
            'r_min': r_min,
            'r_max': r_max,
            'n_points_total': len(r),
            'bins': []
        }
        
        # Fit each bin
        for i in range(self.n_bins):
            bin_info = self._fit_radial_bin(
                r, g_bar, g_obs, errors,
                r_edges[i], r_edges[i+1], bin_index=i
            )
            bin_results['bins'].append(bin_info)
            if not bin_info.get('success'):
                logger.debug(f"Galaxy {galaxy_name} bin {i} failed: {bin_info.get('reason')}")
        
        # Compute scale dependence statistic
        if len(bin_results['bins']) >= 2:
            bin_results['scale_dependence'] = self._compute_scale_dependence(
                bin_results['bins'][0],   # Inner bin
                bin_results['bins'][-1]   # Outer bin
            )
            if not bin_results['scale_dependence'].get('success'):
                logger.info(f"Galaxy {galaxy_name} scale dependence failed: {bin_results['scale_dependence'].get('reason')}")
        
        return bin_results
    
    def _fit_radial_bin(self, r: np.ndarray, g_bar: np.ndarray, g_obs: np.ndarray,
                       errors: Dict, r_lower: float, r_upper: float,
                       bin_index: int = 0) -> Dict:
        """Fit RAR to single radial bin."""
        
        # Select points in radial range
        mask = (r >= r_lower) & (r < r_upper)
        
        if np.sum(mask) < 3:
            return {
                'bin_index': bin_index,
                'r_range': (r_lower, r_upper),
                'n_points': np.sum(mask),
                'success': False,
                'reason': 'Insufficient points in bin'
            }
        
        g_bar_bin = g_bar[mask]
        g_obs_bin = g_obs[mask]
        
        # Extract or compute errors
        if 'g_obs' in errors:
            err_bin = errors['g_obs'][mask]
        else:
            # Compute from velocity errors
            v_circ = np.sqrt(g_obs * r)
            v_err = errors['v_circ'][mask]
            # Δg ≈ 2 v Δv / r
            err_bin = 2 * np.sqrt(g_obs_bin) * v_err / np.sqrt(r[mask])
        
        # Fit RAR
        fit_result = self.fitter.fit_to_data(g_bar_bin, g_obs_bin, err_bin)
        
        if not fit_result.get('success', False):
            return {
                'bin_index': bin_index,
                'r_range': (r_lower, r_upper),
                'n_points': np.sum(mask),
                'success': False,
                'reason': fit_result.get('reason', 'Unknown error')
            }
        
        # Return successful fit
        return {
            'bin_index': bin_index,
            'r_range': (r_lower, r_upper),
            'r_center': (r_lower + r_upper) / 2,
            'n_points': np.sum(mask),
            'a0': fit_result['a0'],
            'a0_error': fit_result['a0_error'],
            'chi2_reduced': fit_result['chi2_reduced'],
            'success': True,
        }
    
    def _compute_scale_dependence(self, inner_bin: Dict, outer_bin: Dict) -> Dict:
        """Compute scale dependence statistic between two bins."""
        
        if not inner_bin.get('success') or not outer_bin.get('success'):
            return {'success': False, 'reason': 'One or both bins failed to fit'}
        
        return compute_scale_dependence_statistic(
            inner_bin['a0'], inner_bin['a0_error'],
            outer_bin['a0'], outer_bin['a0_error']
        )
    
    def analyze_ensemble(self, galaxy_list: List[Tuple[str, Dict]]) -> pd.DataFrame:
        """
        Analyze scale dependence for ensemble of galaxies.
        
        Args:
            galaxy_list: List of (name, data_dict) tuples
        
        Returns:
            DataFrame with results for each galaxy
        """
        results = []
        
        for gal_name, gal_data in galaxy_list:
            analysis = self.analyze_galaxy(gal_data, gal_name)
            
            if analysis is None:
                results.append({
                    'galaxy': gal_name,
                    'success': False,
                    'reason': 'Analysis failed'
                })
                continue
            
            # Extract scale dependence info
            if 'scale_dependence' in analysis and analysis['scale_dependence'].get('success'):
                sd = analysis['scale_dependence']
                
                results.append({
                    'galaxy': gal_name,
                    'n_points': analysis['n_points_total'],
                    'r_min': analysis['r_min'],
                    'r_max': analysis['r_max'],
                    'a0_inner': analysis['bins'][0]['a0'],
                    'a0_inner_err': analysis['bins'][0]['a0_error'],
                    'a0_outer': analysis['bins'][-1]['a0'],
                    'a0_outer_err': analysis['bins'][-1]['a0_error'],
                    'ratio': sd['ratio'],
                    'ratio_err': sd['ratio_err'],
                    'z_score': sd['z_score'],
                    'p_value': sd['p_value'],
                    'interpretation': sd['interpretation'],
                    'success': True,
                })
            else:
                results.append({
                    'galaxy': gal_name,
                    'success': False,
                    'reason': 'Scale dependence failed'
                })
        
        df_results = pd.DataFrame(results)
        
        # Summary statistics
        if len(df_results[df_results['success']]) > 0:
            df_success = df_results[df_results['success']]
            
            logger.info(f"\n{'='*70}")
            logger.info(f"ENSEMBLE ANALYSIS RESULTS ({len(df_success)}/{len(df_results)} galaxies)")
            logger.info(f"{'='*70}")
            logger.info(f"Mean ratio a0(inner) / a0(outer): {df_success['ratio'].mean():.4f}")
            logger.info(f"Std of ratios: {df_success['ratio'].std():.4f}")
            logger.info(f"Mean z-score: {df_success['z_score'].mean():.2f}σ")
            logger.info(f"Combined significance: {df_success['z_score'].mean() * np.sqrt(len(df_success)):.1f}σ")
            logger.info(f"{'='*70}\n")
        
        return df_results