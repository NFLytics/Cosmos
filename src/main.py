"""
SPARC Radial-Dependent RAR Analysis - Main Entry Point

Orchestrates the complete analysis pipeline.
"""

import logging
import sys
from pathlib import Path
import json
import pandas as pd
import yaml
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sparc_loader import SPARCRotationCurves
from src.radial_analysis import RadialDependenceAnalyzer
from src.statistical_tests import StatisticalInterpreter
from src.visualization import RARVisualizer

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = 'config/analysis_config.yaml'):
    """Load analysis configuration."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    """Execute complete analysis pipeline."""
    
    print("\n" + "="*70)
    print("SPARC RADIAL-DEPENDENT RAR ANALYSIS")
    print("Testing SDH+ vs ΛCDM with existing data")
    print("="*70 + "\n")
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults")
        config = {
            'data': {'sparc_dir': 'data/raw_sparc'},
            'analysis': {'n_radial_bins': 2}
        }
    
    # Create output directories
    Path('output/plots').mkdir(parents=True, exist_ok=True)
    Path('output/tables').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    # ========== STEP 1: LOAD SPARC DATA ==========
    logger.info("Step 1: Loading SPARC data...")
    try:
        sparc = SPARCRotationCurves(config['data']['sparc_dir'])
    except FileNotFoundError as e:
        logger.error(f"Failed to load SPARC data: {e}")
        logger.error("Make sure SPARC files are in: " + config['data']['sparc_dir'])
        sys.exit(1)
    
    # ========== STEP 2: QUALITY CONTROL ==========
    logger.info("Step 2: Running quality control...")
    quality_report = sparc.save_quality_report('output/tables/galaxies_quality_check.csv')
    
    quality_galaxies = sparc.get_quality_galaxies()
    logger.info(f"Quality galaxies: {len(quality_galaxies)}/{len(sparc.galaxies)}")
    
    if len(quality_galaxies) < 10:
        logger.error(f"Only {len(quality_galaxies)} quality galaxies - analysis may be unreliable")
    
    # ========== STEP 3: RADIAL-DEPENDENT FITTING ==========
    logger.info("Step 3: Analyzing radial dependence...")
    
    analyzer = RadialDependenceAnalyzer(
        n_radial_bins=config['analysis']['n_radial_bins']
    )
    
    # Prepare galaxy list
    galaxy_data_list = []
    for gal_name in quality_galaxies:
        gal_data = sparc.extract_galaxy_profile(gal_name)
        if gal_data is not None:
            passes, _ = sparc.quality_check_galaxy(gal_data)
            if passes:
                galaxy_data_list.append((gal_name, gal_data))
    
    logger.info(f"Analyzing {len(galaxy_data_list)} quality galaxies...")
    df_results = analyzer.analyze_ensemble(galaxy_data_list)
    
    # Save results
    df_results.to_csv('output/tables/radial_fits_results.csv', index=False)
    logger.info(f"Saved detailed results to output/tables/radial_fits_results.csv")
    
    # ========== STEP 4: STATISTICAL INTERPRETATION ==========
    logger.info("Step 4: Interpreting results...")
    
    interpreter = StatisticalInterpreter()
    interpretation = interpreter.interpret_results(df_results)
    
    if interpretation.get('success'):
        interpreter.print_interpretation(interpretation)
        
        # Save interpretation (convert numpy types to python types)
        def convert_numpy(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(i) for i in obj]
            return obj

        serializable_interpretation = convert_numpy(interpretation)
        
        with open('output/tables/interpretation.json', 'w') as f:
            json.dump(serializable_interpretation, f, indent=2)
    else:
        logger.error(f"Interpretation failed: {interpretation.get('reason')}")
    
    # ========== STEP 5: VISUALIZATION ==========
    logger.info("Step 5: Creating visualizations...")
    
    visualizer = RARVisualizer(output_dir='output/plots')
    visualizer.plot_ensemble_results(df_results, interpretation)
    visualizer.save_summary_table(df_results, interpretation)
    
    logger.info("Visualization saved to output/plots/")
    
    # ========== FINAL REPORT ==========
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nResults saved to:")
    print(f"  - output/tables/radial_fits_results.csv")
    print(f"  - output/tables/galaxies_quality_check.csv")
    print(f"  - output/tables/interpretation.json")
    print(f"  - output/plots/radial_rar_analysis.png")
    print("\n" + "="*70 + "\n")
    
    return interpretation

if __name__ == "__main__":
    main()