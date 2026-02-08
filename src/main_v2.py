"""
Main script for Phase 1B of the SPARC RAR Analysis.
Orchestrates data loading, quality control, morphology splitting, and radial acceleration relation analysis.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import json

from src.sparc_loader_v2 import SPARCRotationCurvesV2
from src.rar_fitting import RARFitter
from src.radial_analysis_v2 import RadialDependenceAnalyzerV2
from src.statistical_tests import StatisticalInterpreter as Interpretation
from src.config_loader import load_config
from src.plotting import plot_rar_data, plot_rar_fits, plot_rar_summary, plot_mass_model_decomposition
from src.onnx_engine import ONNXComputeEngine # Assuming ONNX is used
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_analysis_with_quality_level(quality_level: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Runs the full analysis pipeline for a given quality level."""
    logger.info(f"\n{'='*50}\nPHASE 1B: EXPANDED ANALYSIS - {quality_level.upper()} QUALITY CRITERIA\n{'='*50}\n")

    output_base = config['data'].get('output_dir', 'output')
    output_dir = Path(output_base) / f"quality_{quality_level}"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'tables').mkdir(parents=True, exist_ok=True)
    (output_dir / 'plots').mkdir(parents=True, exist_ok=True)

    # Step 1: Load SPARC data
    logger.info(f"Step 1: Loading SPARC data with {quality_level} criteria...")
    sparc = SPARCRotationCurvesV2(config['data']['sparc_dir'], strictness=quality_level)

    # Step 2: Quality control
    logger.info("Step 2: Running quality control...")
    # This also saves the report internally.
    quality_report = sparc.save_quality_report(str(output_dir / 'tables' / 'galaxies_quality_check.csv'))

    quality_galaxies = sparc.get_quality_galaxies()
    logger.info(f"Quality galaxies: {len(quality_galaxies)}/{len(sparc.galaxies)}")

    # Step 3: Splitting sample by galaxy morphology
    logger.info("Step 3: Splitting sample by galaxy morphology...")
    spirals_all = sparc.get_galaxies_by_morphology('spiral')
    dwarfs_all = sparc.get_galaxies_by_morphology('dwarf')
    unknown_all = sparc.get_galaxies_by_morphology('unknown')

    spirals_qc = [g for g in spirals_all if g in quality_galaxies]
    dwarfs_qc = [g for g in dwarfs_all if g in quality_galaxies]
    unknown_qc = [g for g in unknown_all if g in quality_galaxies]

    logger.info(f"  Spirals: {len(spirals_all)} galaxies (QC: {len(spirals_qc)})")
    logger.info(f"  Dwarfs: {len(dwarfs_all)} galaxies (QC: {len(dwarfs_qc)})")
    logger.info(f"  Unknown: {len(unknown_all)} galaxies (QC: {len(unknown_qc)})")

    logger.info("Step 4: Analyzing radial dependence...")
    # Use GPU if available
    use_gpu = True 
    analyzer = RadialDependenceAnalyzerV2(use_gpu=use_gpu)
    
    def analyze_list(galaxy_names):
        galaxy_list = []
        for gal_name in galaxy_names:
            gal_data = sparc.extract_galaxy_profile(gal_name)
            if gal_data:
                morphology = sparc.galaxy_metadata.get(gal_name, {}).get('morphology', 'unknown')
                galaxy_list.append((gal_name, gal_data, morphology))
        return analyzer.analyze_ensemble(galaxy_list)

    # Store results for all quality galaxies
    if quality_galaxies:
        logger.info(f"Analyzing {len(quality_galaxies)} quality galaxies...")
        df_all = analyze_list(quality_galaxies)
    else:
        logger.warning("No quality galaxies to analyze for this quality level.")
        # Create an empty DataFrame with expected columns if no quality galaxies
        df_all = pd.DataFrame(columns=['galaxy', 'morphology', 'success', 'ratio', 'z_score'])

    # Step 5: Interpreting results
    logger.info("Step 5: Interpreting results...")
    interpreter = Interpretation()

    summary = {}
    if not df_all.empty and df_all['success'].any():
        interpretation_all = interpreter.interpret_results(df_all)
        logger.info(f"Overall interpretation: {interpretation_all.get('overall_conclusion', 'N/A')}")
        summary['all'] = interpretation_all

        # Save detailed results
        df_all.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_all.csv', index=False)
    else:
        logger.warning("No successful results to interpret.")
        summary['all'] = {'overall_conclusion': 'No galaxies successfully analyzed.'}

    # Process by morphology
    if spirals_qc:
        df_spirals = analyze_list(spirals_qc)
        if not df_spirals.empty and df_spirals['success'].any():
            interpretation_spirals = interpreter.interpret_results(df_spirals)
            logger.info(f"  Spirals interpretation: {interpretation_spirals.get('overall_conclusion', 'N/A')}")
            summary['spirals'] = interpretation_spirals
            df_spirals.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_spirals.csv', index=False)
        else:
            summary['spirals'] = {'overall_conclusion': 'No spiral galaxies successfully analyzed.'}

    if dwarfs_qc:
        df_dwarfs = analyze_list(dwarfs_qc)
        if not df_dwarfs.empty and df_dwarfs['success'].any():
            interpretation_dwarfs = interpreter.interpret_results(df_dwarfs)
            logger.info(f"  Dwarfs interpretation: {interpretation_dwarfs.get('overall_conclusion', 'N/A')}")
            summary['dwarfs'] = interpretation_dwarfs
            df_dwarfs.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_dwarfs.csv', index=False)
        else:
            summary['dwarfs'] = {'overall_conclusion': 'No dwarf galaxies successfully analyzed.'}

    # Step 6: Generate summary plots
    logger.info("Step 6: Generating summary plots...")
    if not df_all.empty and df_all['success'].any():
        plot_rar_summary(df_all, output_dir / 'plots' / f'rar_summary_{quality_level}.png')
        if 'spirals' in summary and 'mean_ratio' in summary['spirals']:
             plot_rar_summary(df_spirals, output_dir / 'plots' / f'rar_summary_{quality_level}_spirals.png', title=f'RAR Summary (Spirals - {quality_level.upper()})')
        if 'dwarfs' in summary and 'mean_ratio' in summary['dwarfs']:
             plot_rar_summary(df_dwarfs, output_dir / 'plots' / f'rar_summary_{quality_level}_dwarfs.png', title=f'RAR Summary (Dwarfs - {quality_level.upper()})')

    logger.info(f"Analysis for {quality_level} criteria completed.")
    return summary

def main():
    logger.info(f"\n{'='*70}\nSPARC RADIAL-DEPENDENT RAR ANALYSIS - PHASE 1B\nEXPANDED SAMPLE WITH FLEXIBLE QUALITY CRITERIA AND MORPHOLOGY SPLITTING\n{'='*70}\n")
    
    config = load_config()

    overall_summary = {}

    # Run analysis for different quality levels
    for quality_level in ['strict', 'relaxed', 'minimal', 'maximal']:
        level_summary = run_analysis_with_quality_level(quality_level, config)
        overall_summary[quality_level] = level_summary
    
    # Save overall summary (e.g., to a JSON file)
    output_base = config['data'].get('output_dir', 'output')
    with open(Path(output_base) / 'overall_summary.json', 'w') as f:
        json.dump(overall_summary, f, indent=4)
    logger.info(f"Overall analysis summary saved to {Path(output_base) / 'overall_summary.json'}")
    
    logger.info("Phase 1B analysis complete.")

if __name__ == "__main__":
    main()
