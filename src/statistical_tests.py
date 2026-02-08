"""
Statistical Tests and Interpretation

Interprets radial-dependent RAR results in context of SDH+ vs ΛCDM predictions.
"""

import numpy as np
import logging
from scipy.stats import norm, chi2
import pandas as pd
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class StatisticalInterpreter:
    
    # Expected predictions
    CDM_RATIO_MEAN = 1.00      # ΛCDM: a0 universal
    CDM_RATIO_STD = 0.05       # Expected scatter from measurement
    
    SDH_RATIO_MEAN = 1.12      # SDH+: 12% increase inner to outer
    SDH_RATIO_STD = 0.06       # Expected scatter
    
    def __init__(self):
        pass
    
    def interpret_results(self, df_results: pd.DataFrame) -> Dict:
        """
        Interpret ensemble of radial-dependence measurements.
        
        Args:
            df_results: DataFrame from RadialDependenceAnalyzer.analyze_ensemble()
        
        Returns:
            Dictionary with interpretation summary
        """
        # Filter successful analyses
        df_success = df_results[df_results['success'] == True].copy()
        
        if len(df_success) == 0:
            return {'success': False, 'reason': 'No successful galaxies'}
        
        # Basic statistics
        ratios = df_success['ratio'].values
        z_scores = df_success['z_score'].values
        
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        sem_ratio = std_ratio / np.sqrt(len(ratios))  # Standard error of mean
        
        mean_z = np.mean(z_scores)
        
        # Meta-analysis: Combined significance
        # Using Fisher's method for independent tests
        combined_z = mean_z * np.sqrt(len(ratios))
        combined_p = 1 - norm.cdf(combined_z)
        
        # Test against ΛCDM null hypothesis (ratio = 1.0)
        t_stat_cdm = (mean_ratio - self.CDM_RATIO_MEAN) / sem_ratio
        p_value_cdm = 1 - norm.cdf(t_stat_cdm)  # One-tailed
        
        # Test against SDH+ hypothesis (ratio = 1.12)
        t_stat_sdh = (mean_ratio - self.SDH_RATIO_MEAN) / sem_ratio
        p_value_sdh = norm.cdf(t_stat_sdh)  # One-tailed (lower)
        
        # Determine winner
        if mean_ratio > 1.05 and combined_z > 2.0:
            winner = "SDH+"
            confidence = "HIGH" if combined_z > 3.0 else "MODERATE"
        elif mean_ratio < 1.02 and combined_z < 1.0:
            winner = "ΛCDM"
            confidence = "HIGH" if np.abs(combined_z) > 3.0 else "MODERATE"
        else:
            winner = "INCONCLUSIVE"
            confidence = "LOW"
        
        # Count significant galaxies
        n_sig_2sigma = np.sum(z_scores > 2.0)
        n_sig_1sigma = np.sum(z_scores > 1.0)
        
        interpretation = {
            'n_galaxies': int(len(df_success)),
            'mean_ratio': float(mean_ratio),
            'std_ratio': float(std_ratio),
            'sem_ratio': float(sem_ratio),
            'mean_z_score': float(mean_z),
            'combined_z': float(combined_z),
            'combined_p': float(combined_p),
            'n_galaxies_2sigma': int(n_sig_2sigma),
            'n_galaxies_1sigma': int(n_sig_1sigma),
            't_stat_cdm': float(t_stat_cdm),
            'p_value_cdm': float(p_value_cdm),
            't_stat_sdh': float(t_stat_sdh),
            'p_value_sdh': float(p_value_sdh),
            'winner': winner,
            'confidence': confidence,
            'success': True,
            'overall_conclusion': f"{winner} ({confidence}) - {combined_z:.1f}σ ensemble significance"
        }
        
        return interpretation
    
    def print_interpretation(self, interpretation: Dict):
        
        if not interpretation.get('success'):
            print(f"Interpretation failed: {interpretation.get('reason')}")
            return
        
        print("\n" + "="*70)
        print("RADIAL-DEPENDENT RAR ANALYSIS: INTERPRETATION")
        print("="*70)
        
        print(f"\nSample size: {interpretation['n_galaxies']} galaxies analyzed")
        print(f"\nKey Statistics:")
        print(f"  Mean ratio a0(inner) / a0(outer):     {interpretation['mean_ratio']:.4f}")
        print(f"  Standard deviation:                    {interpretation['std_ratio']:.4f}")
        print(f"  Standard error of mean:                {interpretation['sem_ratio']:.4f}")
        print(f"  95% confidence interval: [{interpretation['mean_ratio']-1.96*interpretation['sem_ratio']:.4f}, {interpretation['mean_ratio']+1.96*interpretation['sem_ratio']:.4f}]")
        
        print(f"\nPer-Galaxy Statistics:")
        print(f"  Mean z-score (per galaxy):             {interpretation['mean_z_score']:.2f}σ")
        print(f"  Combined significance (ensemble):      {interpretation['combined_z']:.2f}σ")
        print(f"  Combined p-value:                      {interpretation['combined_p']:.2e}")
        
        print(f"\nGalaxies with Significant Excess:")
        print(f"  >2σ significance:                      {interpretation['n_galaxies_2sigma']} galaxies ({interpretation['n_galaxies_2sigma']/interpretation['n_galaxies']*100:.1f}%)")
        print(f"  >1σ significance:                      {interpretation['n_galaxies_1sigma']} galaxies ({interpretation['n_galaxies_1sigma']/interpretation['n_galaxies']*100:.1f}%)")
        
        print(f"\nHypothesis Tests:")
        print(f"  Test against ΛCDM (ratio=1.00):")
        print(f"    t-statistic: {interpretation['t_stat_cdm']:.2f}")
        print(f"    p-value: {interpretation['p_value_cdm']:.4f}")
        print(f"    Result: {'REJECT' if interpretation['p_value_cdm'] < 0.05 else 'FAIL TO REJECT'} ΛCDM null hypothesis")
        
        print(f"\n  Test against SDH+ (ratio=1.12):")
        print(f"    t-statistic: {interpretation['t_stat_sdh']:.2f}")
        print(f"    p-value: {interpretation['p_value_sdh']:.4f}")
        print(f"    Result: {'SUPPORT' if interpretation['p_value_sdh'] < 0.05 else 'DO NOT SUPPORT'} SDH+ hypothesis")
        
        print(f"\n" + "-"*70)
        print(f"VERDICT:")
        print("-"*70)
        print(f"\nWinner: {interpretation['winner'].upper()}")
        print(f"Confidence Level: {interpretation['confidence']}")
        
        if interpretation['winner'] == "SDH+":
            print(f"\n✓ RESULT FAVORS SDH+")
            print(f"  Mean ratio {interpretation['mean_ratio']:.4f} > 1.00 with {interpretation['combined_z']:.1f}σ significance")
            print(f"  Interpretation: a0 increases from outer to inner regions")
            print(f"  Consistent with RG running + phonon effects in SDH+")
            print(f"  ΛCDM prediction (ratio ~ 1.00) is RULED OUT at >{2 if interpretation['combined_z']<3 else 3}σ level")
        
        elif interpretation['winner'] == "ΛCDM":
            print(f"\n✗ RESULT DISFAVORS SDH+")
            print(f"  Mean ratio {interpretation['mean_ratio']:.4f} ≈ 1.00 with {interpretation['combined_z']:.1f}σ significance")
            print(f"  Interpretation: a0 is scale-independent (universal)")
            print(f"  Consistent with ΛCDM prediction (single a0 value)")
            print(f"  SDH+ RG-running effect is NOT observed")
        
        else:
            print(f"\n? INCONCLUSIVE")
            print(f"  Mean ratio {interpretation['mean_ratio']:.4f}, borderline significance {interpretation['combined_z']:.1f}σ")
            print(f"  Requires additional data or refined analysis")
        
        print("\n" + "="*70 + "\n")