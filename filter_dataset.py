import pandas as pd
import logging
from pathlib import Path
from src.sparc_loader_v2 import SPARCRotationCurvesV2
from src.config_loader import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def filter_dataset(quality_level='relaxed'):
    """
    Filters the SPARC dataset based on quality criteria and saves a cleaned CSV.
    """
    config = load_config()
    sparc_dir = config['data']['sparc_dir']
    
    logger.info(f"Initializing filter with {quality_level} criteria...")
    sparc = SPARCRotationCurvesV2(sparc_dir, strictness=quality_level)
    
    # Get names of galaxies that pass the quality check
    quality_galaxies = sparc.get_quality_galaxies()
    logger.info(f"Filtering complete. {len(quality_galaxies)} galaxies passed out of {len(sparc.galaxies)}.")
    
    # Load the standardized dataset if it exists
    standardized_path = 'data/standardized_cosmos_v2.csv'
    if Path(standardized_path).exists():
        df = pd.read_csv(standardized_path)
        # Filter rows based on galaxy name
        df_filtered = df[df['galaxy'].isin(quality_galaxies)]
        
        output_path = f'data/filtered_cosmos_{quality_level}.csv'
        df_filtered.to_csv(output_path, index=False)
        logger.info(f"Saved filtered standardized dataset to {output_path}")
    else:
        logger.warning(f"{standardized_path} not found. Creating a new combined dataset for quality galaxies...")
        # Fallback: create combined data from scratch for quality galaxies
        data_list = []
        for gal_name in quality_galaxies:
            profile = sparc.extract_galaxy_profile(gal_name)
            if profile:
                morph = sparc.galaxy_metadata.get(gal_name, {}).get('morphology', 'unknown')
                dist = sparc.galaxy_metadata.get(gal_name, {}).get('distance_mpc', 0)
                inc = sparc.galaxy_metadata.get(gal_name, {}).get('inclination', 0)
                
                gal_df = pd.DataFrame({
                    'galaxy': gal_name,
                    'r_kpc': profile['r'],
                    'v_obs': profile['v_circ'],
                    'v_obs_err': profile['errors']['v_circ'],
                    'g_bar': profile['g_bar'],
                    'g_obs': profile['g_obs'],
                    'morphology': morph,
                    'dist': dist,
                    'inc': inc
                })
                data_list.append(gal_df)
        
        if data_list:
            full_filtered = pd.concat(data_list, ignore_index=True)
            output_path = f'data/filtered_cosmos_{quality_level}.csv'
            full_filtered.to_csv(output_path, index=False)
            logger.info(f"Saved new filtered dataset to {output_path} ({len(full_filtered)} records)")
        else:
            logger.error("No data could be extracted for the quality galaxies.")

if __name__ == "__main__":
    # We use 'relaxed' as the default for a good balance of quantity and quality
    filter_dataset('relaxed')
