"""
Radial-Dependent RAR Analysis v2 - With Galaxy Type Splitting

Extends original analysis to support:
- Flexible quality criteria
- Galaxy type splitting (dwarf vs spiral)
- Comparison of results across samples
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
from .rar_fitting import RARFitter, compute_scale_dependence_statistic

logger = logging.getLogger(__name__)

class RadialDependenceAnalyzerV2:
    """Enhanced analyzer with galaxy type splitting"""
    
    def __init__(self, n_radial_bins: int = 2, use_gpu: bool = False):
        """
        Initialize analyzer.
        
        Args:
            n_radial_bins: Number of radial bins (default 2: inner/outer)
            use_gpu: Whether to use ONNX-CUDA acceleration
        """
        self.n_bins = n_radial_bins
        self.fitter = RARFitter(use_gpu=use_gpu)
    
    def analyze_galaxy(self, galaxy_data: Dict, galaxy_name: str = "Unknown",
                      morphology: str = "unknown") -> Optional[Dict]:
        """
        Analyze radial dependence for single galaxy.
        
        Args:
            galaxy_data: Dictionary with keys r, v_circ, g_bar, g_obs, errors
            galaxy_name: Galaxy identifier
            morphology: Galaxy type ('dwarf', 'spiral', or 'unknown')
        
        Returns:
            Dictionary with radial bins and a0 fits
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
            'morphology': morphology,
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
        
        # Compute scale dependence statistic
        if len(bin_results['bins']) >= 2:
            sd = self._compute_scale_dependence(
                bin_results['bins'][0],
                bin_results['bins'][-1]
            )
            bin_results['scale_dependence'] = sd
            if not sd.get('success'):
                logger.debug(f"Scale dependence failed for {galaxy_name}: {sd.get('reason')}")
        
        return bin_results
    
    def _fit_radial_bin(self, r: np.ndarray, g_bar: np.ndarray, g_obs: np.ndarray,
                       errors: Dict, r_lower: float, r_upper: float,
                       bin_index: int = 0) -> Dict:
        """Fit RAR to single radial bin"""
        
        # Include upper bound for the last bin or all bins to be safe
        if bin_index == self.n_bins - 1:
            mask = (r >= r_lower) & (r <= r_upper)
        else:
            mask = (r >= r_lower) & (r < r_upper)
        
        if np.sum(mask) < 2:
            return {
                'bin_index': bin_index,
                'r_range': (r_lower, r_upper),
                'n_points': np.sum(mask),
                'success': False,
                'reason': f'Insufficient points in bin ({np.sum(mask)})'
            }
        
        g_bar_bin = g_bar[mask]
        g_obs_bin = g_obs[mask]
        
        if 'g_obs' in errors:
            err_bin = errors['g_obs'][mask]
        else:
            v_circ = np.sqrt(g_obs * r)
            v_err = errors['v_circ'][mask]
            err_bin = 2 * np.sqrt(g_obs_bin) * v_err / np.sqrt(r[mask])
        
        fit_result = self.fitter.fit_to_data(g_bar_bin, g_obs_bin, err_bin)
        
        if not fit_result.get('success', False):
            logger.warning(f"Fit failed for bin {bin_index}: {fit_result.get('reason', 'Converge error')}")
            return {
                'bin_index': bin_index,
                'r_range': (r_lower, r_upper),
                'n_points': np.sum(mask),
                'success': False,
                'reason': fit_result.get('reason', 'Unknown error')
            }
        
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
        """Compute scale dependence statistic between two bins"""
        
        if not inner_bin.get('success') or not outer_bin.get('success'):
            return {'success': False, 'reason': 'One or both bins failed to fit'}
        
        return compute_scale_dependence_statistic(
            inner_bin['a0'], inner_bin['a0_error'],
            outer_bin['a0'], outer_bin['a0_error']
        )
    
    def analyze_ensemble(self, galaxy_list: List[Tuple[str, Dict, str]]) -> pd.DataFrame:
        """
        Analyze scale dependence for ensemble of galaxies.
        
        Args:
            galaxy_list: List of (name, data_dict, morphology) tuples
        
        Returns:
            DataFrame with results for each galaxy
        """
        results = []
        
        for gal_name, gal_data, morphology in galaxy_list:
            analysis = self.analyze_galaxy(gal_data, gal_name, morphology)
            
            if analysis is None:
                results.append({
                    'galaxy': gal_name,
                    'morphology': morphology,
                    'success': False,
                    'reason': 'Analysis failed'
                })
                continue
            
            if 'scale_dependence' in analysis and analysis['scale_dependence'].get('success'):
                sd = analysis['scale_dependence']
                
                results.append({
                    'galaxy': gal_name,
                    'morphology': morphology,
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
                    'morphology': morphology,
                    'success': False,
                    'reason': 'Scale dependence failed'
                })
        
        df_results = pd.DataFrame(results)
        
        return df_results
    
    def summarize_by_morphology(self, df_results: pd.DataFrame) -> Dict:
        """
        Summarize results separately by galaxy morphology.
        
        Args:
            df_results: Results DataFrame from analyze_ensemble
        
        Returns:
            Dictionary with summary for each morphology
        """
        summary = {}
        
        for morph in df_results['morphology'].unique():
            if pd.isna(morph) or morph == 'unknown':
                continue
            
            df_morph = df_results[df_results['morphology'] == morph]
            df_success = df_morph[df_morph['success'] == True]
            
            if len(df_success) == 0:
                summary[morph] = {
                    'n_total': len(df_morph),
                    'n_success': 0,
                    'reason': 'No successful analyses'
                }
                continue
            
            ratios = df_success['ratio'].values
            z_scores = df_success['z_score'].values
            
            mean_ratio = np.mean(ratios)
            std_ratio = np.std(ratios)
            sem_ratio = std_ratio / np.sqrt(len(ratios))
            
            mean_z = np.mean(z_scores)
            combined_z = mean_z * np.sqrt(len(ratios))
            
            summary[morph] = {
                'n_total': len(df_morph),
                'n_success': len(df_success),
                'mean_ratio': mean_ratio,
                'std_ratio': std_ratio,
                'sem_ratio': sem_ratio,
                'mean_z': mean_z,
                'combined_z': combined_z,
                'n_2sigma': np.sum(z_scores > 2.0),
                'n_3sigma': np.sum(z_scores > 3.0),
            }
        
        return summary