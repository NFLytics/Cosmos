"""
Phase 1B Comparison Analyzer

Compares results across quality levels and morphologies.
Identifies trends and creates summary visualizations.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

logger = __import__('logging').getLogger(__name__)

class Phase1BComparator:
    """Compare Phase 1B results across quality levels"""
    
    def __init__(self):
        """Initialize comparator"""
        self.quality_levels = ['strict', 'relaxed', 'minimal']
        self.results = {}
    
    def load_results(self, output_base: str = 'output'):
        """Load all results from Phase 1B output"""
        
        for quality in self.quality_levels:
            quality_dir = Path(output_base) / f'quality_{quality}' / 'tables'
            
            # Load all interpretation files
            try:
                with open(quality_dir / 'interpretation_all.json', 'r') as f:
                    interp_all = json.load(f)
            except:
                interp_all = None
            
            try:
                with open(quality_dir / 'interpretation_spirals.json', 'r') as f:
                    interp_spirals = json.load(f)
            except:
                interp_spirals = None
            
            try:
                with open(quality_dir / 'interpretation_dwarfs.json', 'r') as f:
                    interp_dwarfs = json.load(f)
            except:
                interp_dwarfs = None
            
            self.results[quality] = {
                'all': interp_all,
                'spirals': interp_spirals,
                'dwarfs': interp_dwarfs,
            }
    
    def create_comparison_table(self) -> pd.DataFrame:
        """Create main comparison table"""
        
        rows = []
        
        for quality in self.quality_levels:
            qual_results = self.results.get(quality, {})
            
            all_res = qual_results.get('all')
            sp_res = qual_results.get('spirals')
            dw_res = qual_results.get('dwarfs')
            
            rows.append({
                'Quality': quality.upper(),
                'All Galaxies': int(all_res['n_galaxies']) if all_res else 'N/A',
                'All Ratio': f"{all_res['mean_ratio']:.3f}±{all_res['std_ratio']:.3f}" if all_res else 'N/A',
                'All Z-score': f"{all_res['combined_z']:.2f}σ" if all_res else 'N/A',
                'All Verdict': all_res['winner'] if all_res else 'N/A',
                'Spirals': int(sp_res['n_galaxies']) if sp_res else 'N/A',
                'Spiral Ratio': f"{sp_res['mean_ratio']:.3f}" if sp_res else 'N/A',
                'Spiral Z': f"{sp_res['combined_z']:.2f}σ" if sp_res else 'N/A',
                'Dwarfs': int(dw_res['n_galaxies']) if dw_res else 'N/A',
                'Dwarf Ratio': f"{dw_res['mean_ratio']:.3f}" if dw_res else 'N/A',
                'Dwarf Z': f"{dw_res['combined_z']:.2f}σ" if dw_res else 'N/A',
            })
        
        return pd.DataFrame(rows)
    
    def plot_comparison(self, output_dir: str = 'output'):
        """Create comparison plots"""
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        qualities = []
        all_ratios = []
        spiral_ratios = []
        dwarf_ratios = []
        all_z = []
        spiral_z = []
        dwarf_z = []
        
        for quality in self.quality_levels:
            qual_results = self.results.get(quality, {})
            
            all_res = qual_results.get('all')
            sp_res = qual_results.get('spirals')
            dw_res = qual_results.get('dwarfs')
            
            if all_res:
                qualities.append(quality.upper())
                all_ratios.append(all_res['mean_ratio'])
                all_z.append(all_res['combined_z'])
            
            if sp_res:
                spiral_ratios.append(sp_res['mean_ratio'])
                spiral_z.append(sp_res['combined_z'])
            
            if dw_res:
                dwarf_ratios.append(dw_res['mean_ratio'])
                dwarf_z.append(dw_res['combined_z'])
        
        # Plot 1: Ratio comparison
        ax = axes[0, 0]
        x_pos = np.arange(len(qualities))
        width = 0.25
        
        if all_ratios:
            ax.bar(x_pos - width, all_ratios, width, label='All', alpha=0.8)
        if spiral_ratios:
            ax.bar(x_pos, spiral_ratios, width, label='Spirals', alpha=0.8)
        if dwarf_ratios:
            ax.bar(x_pos + width, dwarf_ratios, width, label='Dwarfs', alpha=0.8)
        
        ax.axhline(1.00, color='red', linestyle='--', linewidth=2, label='ΛCDM')
        ax.axhline(1.12, color='blue', linestyle='--', linewidth=2, label='SDH+')
        
        ax.set_ylabel('a₀(inner) / a₀(outer)')
        ax.set_title('Mean Ratios Across Quality Levels')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(qualities)
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
        ax.set_ylim(0.9, 1.4)
        
        # Plot 2: Z-score comparison
        ax = axes[0, 1]
        
        if all_z:
            ax.plot(qualities, all_z, 'o-', label='All', linewidth=2, markersize=8)
        if spiral_z:
            ax.plot(qualities, spiral_z, 's-', label='Spirals', linewidth=2, markersize=8)
        if dwarf_z:
            ax.plot(qualities, dwarf_z, '^-', label='Dwarfs', linewidth=2, markersize=8)
        
        ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(2, color='orange', linestyle=':', linewidth=2, label='2σ threshold')
        ax.axhline(3, color='green', linestyle=':', linewidth=2, label='3σ threshold')
        
        ax.set_ylabel('Combined Z-score (σ)')
        ax.set_title('Significance Across Quality Levels')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Plot 3: Trend analysis
        ax = axes[1, 0]
        
        quality_order = [0, 1, 2]  # strict, relaxed, minimal
        if all_ratios:
            ax.plot(quality_order[:len(all_ratios)], all_ratios, 'o-', linewidth=2, markersize=10, label='All')
        if spiral_ratios:
            ax.plot(quality_order[:len(spiral_ratios)], spiral_ratios, 's-', linewidth=2, markersize=10, label='Spirals')
        if dwarf_ratios:
            ax.plot(quality_order[:len(dwarf_ratios)], dwarf_ratios, '^-', linewidth=2, markersize=10, label='Dwarfs')
        
        ax.axhline(1.00, color='red', linestyle='--', alpha=0.5, label='ΛCDM')
        ax.axhline(1.12, color='blue', linestyle='--', alpha=0.5, label='SDH+')
        
        ax.set_xlabel('Quality Level (Stricter → Looser)')
        ax.set_ylabel('Mean Ratio')
        ax.set_title('Trend: Convergence with Larger Sample')
        ax.set_xticks(quality_order)
        ax.set