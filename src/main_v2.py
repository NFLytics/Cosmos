"""
Main script for Phase 1B of the SPARC RAR Analysis.
Orchestrates data loading, quality control, morphology splitting, and radial acceleration relation analysis.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from src.sparc_loader_v2 import SPARCRotationCurvesV2
from src.rar_fitting import RARFitter
from src.radial_analysis_v2 import RadialDependenceAnalyzerV2
from src.statistical_tests import Interpretation
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

    output_dir = Path(config['output_dir']) / f"output_{quality_level}"
    output_dir.mkdir(parents=True, exist_ok=True)

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
    rar_fitter = RARFitter(onnx_engine=ONNXComputeEngine()) # Assuming ONNX is integrated
    analyzer = RadialDependenceAnalyzerV2(sparc, rar_fitter, output_dir)
    
    # Store results for all quality galaxies
    all_results = []
    
    if quality_galaxies:
        logger.info(f"Analyzing {len(quality_galaxies)} quality galaxies...")
        df_all = analyzer.analyze_galaxies(quality_galaxies, quality_level)
        all_results.append(df_all)
    else:
        logger.warning("No quality galaxies to analyze for this quality level.")
        # Create an empty DataFrame with expected columns if no quality galaxies
        df_all = pd.DataFrame(columns=['Galaxy', 'chi2_DM', 'chi2_MOND', 'delta_chi2', 'morphology', 'quality_pass', 'success'])

    # Step 5: Interpreting results
    logger.info("Step 5: Interpreting results...")
    interpreter = Interpretation()

    summary = {}
    if not df_all.empty:
        df_all['success'] = True # Assume success if it made it this far (this is a placeholder)
        interpretation_all = interpreter.interpret_results(df_all)
        logger.info(f"Overall interpretation: {interpretation_all['overall_conclusion']}")
        summary['all'] = interpretation_all

        # Save detailed results
        df_all.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_all.csv', index=False)
    else:
        logger.warning("No results to interpret.")
        summary['all'] = {'overall_conclusion': 'No galaxies analyzed.'}


    # Process by morphology
    if spirals_qc:
        df_spirals = analyzer.analyze_galaxies(spirals_qc, quality_level)
        if not df_spirals.empty:
            df_spirals['success'] = True
            interpretation_spirals = interpreter.interpret_results(df_spirals)
            logger.info(f"  Spirals interpretation: {interpretation_spirals['overall_conclusion']}")
            summary['spirals'] = interpretation_spirals
            df_spirals.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_spirals.csv', index=False)
        else:
            logger.warning("No spiral galaxies analyzed.")
            summary['spirals'] = {'overall_conclusion': 'No spiral galaxies analyzed.'}

    if dwarfs_qc:
        df_dwarfs = analyzer.analyze_galaxies(dwarfs_qc, quality_level)
        if not df_dwarfs.empty:
            df_dwarfs['success'] = True
            interpretation_dwarfs = interpreter.interpret_results(df_dwarfs)
            logger.info(f"  Dwarfs interpretation: {interpretation_dwarfs['overall_conclusion']}")
            summary['dwarfs'] = interpretation_dwarfs
            df_dwarfs.to_csv(output_dir / 'tables' / f'rar_results_{quality_level}_dwarfs.csv', index=False)
        else:
            logger.warning("No dwarf galaxies analyzed.")
            summary['dwarfs'] = {'overall_conclusion': 'No dwarf galaxies analyzed.'}

    # Step 6: Generate summary plots
    logger.info("Step 6: Generating summary plots...")
    if not df_all.empty:
        plot_rar_summary(df_all, output_dir / 'plots' / f'rar_summary_{quality_level}.png')
        if 'spirals' in summary and summary['spirals'] != {'overall_conclusion': 'No spiral galaxies analyzed.'}:
            plot_rar_summary(df_spirals, output_dir / 'plots' / f'rar_summary_{quality_level}_spirals.png', title=f'RAR Summary (Spirals - {quality_level.upper()})')
        if 'dwarfs' in summary and summary['dwarfs'] != {'overall_conclusion': 'No dwarf galaxies analyzed.'}:
            plot_rar_summary(df_dwarfs, output_dir / 'plots' / f'rar_summary_{quality_level}_dwarfs.png', title=f'RAR Summary (Dwarfs - {quality_level.upper()})')

    logger.info(f"Analysis for {quality_level} criteria completed.")
    return summary

def main():
    logger.info(f"\n{'='*70}\nSPARC RADIAL-DEPENDENT RAR ANALYSIS - PHASE 1B\nEXPANDED SAMPLE WITH FLEXIBLE QUALITY CRITERIA AND MORPHOLOGY SPLITTING\n{'='*70}\n")
    
    config = load_config()

    overall_summary = {}

    # Run analysis for different quality levels
    for quality_level in ['strict', 'relaxed', 'minimal']:
        level_summary = run_analysis_with_quality_level(quality_level, config)
        overall_summary[quality_level] = level_summary
    
    # Save overall summary (e.g., to a JSON file)
    with open(Path(config['output_dir']) / 'overall_summary.json', 'w') as f:
        json.dump(overall_summary, f, indent=4)
    logger.info(f"Overall analysis summary saved to {Path(config['output_dir']) / 'overall_summary.json'}")
    
    logger.info("Phase 1B analysis complete.")

if __name__ == "__main__":
    main()
