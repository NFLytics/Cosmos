"""
Plotting utilities for Phase 1B Analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def plot_rar_summary(df, output_path, title="RAR Scale-Dependence Summary"):
    """
    Create a summary plot of the RAR scale-dependence results.
    """
    if df.empty:
        logger.warning(f"Empty DataFrame for summary plot: {output_path}")
        return
        
    df_success = df[df['success'] == True]
    if df_success.empty:
        logger.warning(f"No successful galaxies for summary plot: {output_path}")
        return
        
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Plot histogram of ratios
    sns.histplot(df_success['ratio'], kde=True, color='steelblue', alpha=0.7)
    
    # Add vertical lines for predictions
    plt.axvline(1.0, color='red', linestyle='--', linewidth=2, label='ΛCDM (1.00)')
    plt.axvline(1.12, color='blue', linestyle='--', linewidth=2, label='SDH+ (1.12)')
    
    mean_ratio = df_success['ratio'].mean()
    plt.axvline(mean_ratio, color='green', linestyle='-', linewidth=2, label=f'Mean ({mean_ratio:.3f})')
    
    plt.title(title, fontsize=15)
    plt.xlabel('a0(inner) / a0(outer)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()
    
    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved summary plot to {output_path}")

def plot_rar_data(galaxy_name, r, g_bar, g_obs, g_obs_err, output_path):
    """Stub for plotting raw RAR data for a galaxy."""
    pass

def plot_rar_fits(galaxy_name, r, g_bar, g_obs, fits, output_path):
    """Stub for plotting RAR fits for a galaxy."""
    pass

def plot_mass_model_decomposition(galaxy_name, r, v_disk, v_bul, v_gas, v_obs, output_path):
    """Stub for plotting mass model decomposition."""
    pass
