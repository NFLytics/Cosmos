"""
Data Acquisition Script for Phase 1B Expansion - Optimized Fetching

Fetches data from VizieR catalogs, with support for CLI arguments and parallel downloads.
"""

import os
import logging
from astroquery.vizier import Vizier
import pandas as pd
import numpy as np
import argparse
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='[DATA] %(message)s')
logger = logging.getLogger(__name__)

def fetch_catalog_data(cat_id: str, output_dir: str):
    """Fetches tables from a single VizieR catalog and saves them as CSV."""
    logger.info(f"Attempting to fetch catalog: {cat_id}...")
    v = Vizier(row_limit=-1)
    
    catalogs = None
    try:
        catalogs = v.get_catalogs(cat_id)
        if not catalogs:
            logger.warning(f"Direct fetch failed for catalog ID: {cat_id}. Trying keyword search.")
            
            keywords = ["LITTLE THINGS", "Oh 2015", "FIGGS", "Begum 2008"]
            found_cat_id = None
            for kw in keywords:
                search_results = v.find_catalogs(f"{kw} {cat_id}") 
                if search_results:
                    found_cat_id = list(search_results.keys())[0]
                    logger.info(f"Found catalog via search: {found_cat_id}")
                    break
            
            if not found_cat_id:
                logger.error(f"Keyword search also failed for {cat_id}.")
                return

            catalogs = v.get_catalogs(found_cat_id)
        else:
            logger.info(f"Direct fetch successful for catalog ID: {cat_id}")

    except Exception as e:
        logger.error(f"Error during VizieR query for {cat_id}: {e}")
        return

    if not catalogs:
        logger.warning(f"No tables found for catalog ID: {cat_id} after all attempts.")
        return

    logger.info(f"Found {len(catalogs)} tables in {cat_id}.")
    
    for i, table in enumerate(catalogs):
        try:
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else str(x))
                    except Exception as e:
                        logger.warning(f"Could not decode column '{col}' in {cat_id}: {e}")
                        pass 

            prefix = cat_id.replace("/", "_").replace("+", "p")
            path = os.path.join(output_dir, f"{prefix}_table_{i}.csv")
            df.to_csv(path, index=False)
            logger.info(f"Saved {path} with {len(df)} rows.")
            
        except Exception as e:
            logger.error(f"Error processing table {i} from {cat_id}: {e}")

def fetch_data(catalog_ids: list, output_dir: str = "data/extra_sources"):
    """
    Orchestrates fetching of data from multiple VizieR catalogs in parallel.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    max_workers = 4  # Using a moderate number of threads for parallel downloads
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_catalog_data, cat_id, output_dir) for cat_id in catalog_ids]
        
        for future in futures:
            future.result() 

    logger.info("Data fetching and initial saving complete.")
    # TODO: Implement deduplication logic here by comparing fetched data with existing SPARC data.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch VizieR data for Phase 1B expansion.")
    parser.add_argument('--catalogs', nargs='+', required=True, help='List of VizieR catalog IDs to fetch (e.g., J/AJ/149/180 J/MNRAS/386/1667).')
    parser.add_argument('--output-dir', default='data/extra_sources', help='Directory to save downloaded data.')
    
    args = parser.parse_args()
    
    fetch_data(args.catalogs, args.output_dir)
