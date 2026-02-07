"""
Data Ingestion and Deduplication Script
Integrates extra sources (THINGS, LITTLE THINGS) with SPARC.
"""

import pandas as pd
import numpy as np
import os
import logging
import re
import argparse  # Import argparse

logging.basicConfig(level=logging.INFO, format='[INGEST] %(message)s')
logger = logging.getLogger(__name__)

def ingest_extra():
    # 1. Load original SPARC galaxy metadata and rotation curves
    sparc_table1_path = 'data/raw_sparc/Table1.mrt'
    sparc_table2_path = 'data/raw_sparc/Table2.mrt'
    
    try:
        # Load Table1.mrt with robust CSV parsing (default settings)
        logger.info(f"Loading original SPARC Table1 from {sparc_table1_path}...")
        sparc_df_table1 = pd.read_csv(sparc_table1_path, engine='python') # Use default CSV parsing
        sparc_df_table1.columns = [col.strip() for col in sparc_df_table1.columns]
        logger.info(f"Loaded {len(sparc_df_table1)} galaxies from SPARC Table1.")

        # Load Table2.mrt with robust CSV parsing
        logger.info(f"Loading original SPARC Table2 from {sparc_table2_path}...")
        sparc_df_table2 = pd.read_csv(sparc_table2_path, engine='python') # Use default CSV parsing
        sparc_df_table2.columns = [col.strip() for col in sparc_df_table2.columns]
        logger.info(f"Loaded {len(sparc_df_table2)} rotation curve points from SPARC Table2.")

    except FileNotFoundError as e:
        logger.error(f"SPARC original file not found: {e}. Please ensure Table1.mrt and Table2.mrt are in data/raw_sparc/")
        return
    except Exception as e:
        logger.error(f"Error loading original SPARC files: {e}")
        return

    sparc_galaxies = sparc_df_table1['Galaxy'].unique().tolist()
    
    # Normalize names for deduplication
    def normalize_name(name):
        return str(name).replace(" ", "").upper()
    
    sparc_norm_names = set(normalize_name(g) for g in sparc_galaxies)
    
    new_galaxy_metadata_list = [] # To store new galaxy metadata DataFrames
    new_rotation_curves_list = [] # To store new rotation curve DataFrames

    # Process J/AJ/149/180 (LITTLE THINGS - Oh et al. 2015)
    logger.info("Processing J/AJ/149/180 (LITTLE THINGS - Oh et al. 2015)")
    try:
        little_things_info_df = pd.read_csv('data/extra_sources/J_AJ_149_180_table_0.csv')
        little_things_rc_df = pd.read_csv('data/extra_sources/J_AJ_149_180_table_2.csv')

        little_things_info_df = little_things_info_df.rename(columns={
            'Name': 'Galaxy', 'Dist': 'D', 'Inc': 'Inc'}) # Map common columns
        little_things_info_df['norm_name'] = little_things_info_df['Galaxy'].apply(normalize_name)

        new_little_things_meta = little_things_info_df[~little_things_info_df['norm_name'].isin(sparc_norm_names)].copy()
        
        if not new_little_things_meta.empty:
            logger.info(f"Adding {len(new_little_things_meta)} new galaxies from LITTLE THINGS metadata.")
            new_galaxy_metadata_list.append(new_little_things_meta)
            
            for _, row in new_little_things_meta.iterrows():
                galaxy_name = row['Galaxy']
                galaxy_rc_data = little_things_rc_df[little_things_rc_df['Name'] == galaxy_name].copy()
                if not galaxy_rc_data.empty:
                    galaxy_rc_data = galaxy_rc_data.rename(columns={
                        'Rad': 'R', 'Vobs': 'V_obs', 'e_Vobs': 'e_Vobs', 'Vgas': 'V_gas', 'Vdisk': 'V_disk', 'Vbul': 'V_bul'})
                    galaxy_rc_data['Galaxy'] = galaxy_name
                    new_rotation_curves_list.append(galaxy_rc_data)
                    logger.info(f"Added rotation curve data for new galaxy: {galaxy_name}")

    except FileNotFoundError:
        logger.warning("LITTLE THINGS data files not found. Skipping.")
    except Exception as e:
        logger.error(f"Error processing LITTLE THINGS data: {e}")

    # Process J/MNRAS/386/1667 (FIGGS - Begum et al. 2008)
    logger.info("Processing J/MNRAS/386/1667 (FIGGS - Begum et al. 2008)")
    try:
        figgs_info_df = pd.read_csv('data/extra_sources/J_MNRAS_386_1667_table_0.csv')
        figgs_rc_df = pd.read_csv('data/extra_sources/J_MNRAS_386_1667_table_2.csv') 
        
        figgs_info_df = figgs_info_df.rename(columns={'Name': 'Galaxy'})
        figgs_info_df['norm_name'] = figgs_info_df['Galaxy'].apply(normalize_name)

        new_figgs_meta = figgs_info_df[~figgs_info_df['norm_name'].isin(sparc_norm_names)].copy()

        if not new_figgs_meta.empty:
            logger.info(f"Adding {len(new_figgs_meta)} new galaxies from FIGGS metadata.")
            new_galaxy_metadata_list.append(new_figgs_meta)
            
            for _, row in new_figgs_meta.iterrows():
                galaxy_name = row['Galaxy']
                galaxy_rc_data = figgs_rc_df[figgs_rc_df['Name'] == galaxy_name].copy()
                if not galaxy_rc_data.empty:
                    galaxy_rc_data = galaxy_rc_data.rename(columns={
                        'Rad': 'R', 'Vrot': 'V_obs', 'e_Vrot': 'e_Vobs'}) 
                    galaxy_rc_data['Galaxy'] = galaxy_name
                    new_rotation_curves_list.append(galaxy_rc_data)
                    logger.info(f"Added rotation curve data for new galaxy: {galaxy_name}")

    except FileNotFoundError:
        logger.warning("FIGGS data files not found. Skipping.")
    except Exception as e:
        logger.error(f"Error processing FIGGS data: {e}")

    # Append new metadata to SPARC Table1 format (saving as CSV)
    if new_galaxy_metadata_list:
        combined_new_meta_df = pd.concat(new_galaxy_metadata_list, ignore_index=True)
        
        sparc_table1_template_cols = ['Galaxy', 'T', 'D', 'e_D', 'f_D', 'Inc', 'e_Inc', 'L[3.6]', 'e_L[3.6]', 
                                    'Reff', 'SBeff', 'Rdisk', 'SBdisk', 'MHI', 'RHI', 'Vflat', 'e_Vflat', 'Q', 'Ref.']
        
        new_meta_to_add = pd.DataFrame(columns=sparc_table1_template_cols)
        
        for col in combined_new_meta_df.columns:
            if col in sparc_table1_template_cols:
                new_meta_to_add[col] = combined_new_meta_df[col]
            else:
                logger.debug(f"Column '{col}' from new metadata not in SPARC Table1 template, skipping.")

        for col in sparc_table1_template_cols:
            if col not in new_meta_to_add.columns:
                new_meta_to_add[col] = np.nan
        
        new_meta_to_add = new_meta_to_add[sparc_table1_template_cols]
        
        # Load existing SPARC Table1 (prioritize expanded CSV, fallback to original MRT)
        sparc_df_table1_current = pd.DataFrame(columns=sparc_table1_template_cols) # Initialize empty
        try:
            if os.path.exists('data/raw_sparc/Table1_expanded.csv'):
                sparc_df_table1_current = pd.read_csv('data/raw_sparc/Table1_expanded.csv')
                sparc_df_table1_current.columns = [col.strip() for col in sparc_df_table1_current.columns]
                logger.info(f"Loaded existing Table1_expanded.csv.")
            else:
                logger.warning("Table1_expanded.csv not found, loading original Table1.mrt.")
                mrt_path = 'data/raw_sparc/Table1.mrt'
                with open(mrt_path, 'r') as f:
                    lines = f.readlines()
                # Original MRT data starts after 99 header/comment lines (line 100 is first data row)
                original_mrt_data_lines = [re.split(r'\s{2,}', line.strip()) for line in lines[99:] if line.strip() and not line.strip().startswith('----')]
                sparc_df_table1_current = pd.DataFrame(original_mrt_data_lines)
                sparc_df_table1_current.columns = sparc_table1_template_cols[:len(sparc_df_table1_current.columns)]
                logger.info(f"Loaded original Table1.mrt format with {len(sparc_df_table1_current)} rows.")
        except Exception as e:
            logger.error(f"Failed to load existing SPARC Table1: {e}. Starting with empty data.")
            sparc_df_table1_current = pd.DataFrame(columns=sparc_table1_template_cols)

        final_table1_df = pd.concat([sparc_df_table1_current, new_meta_to_add], ignore_index=True)
        final_table1_df.to_csv('data/raw_sparc/Table1_expanded.csv', index=False)
        logger.info(f"Expanded Table1 metadata saved to data/raw_sparc/Table1_expanded.csv with {len(final_table1_df)} galaxies.")
    
    # Append new rotation curves to SPARC Table2 format
    if new_rotation_curves_list:
        combined_new_rc_df = pd.concat(new_rotation_curves_list, ignore_index=True)
        
        # Load existing SPARC Table2 (prioritize expanded CSV)
        existing_sparc_table2_path_csv = 'data/raw_sparc/Table2_expanded.csv'
        existing_sparc_table2_path_mrt = 'data/raw_sparc/Table2.mrt'

        existing_sparc_table2_df = pd.DataFrame() # Initialize empty DF

        if os.path.exists(existing_sparc_table2_path_csv):
            try:
                existing_sparc_table2_df = pd.read_csv(existing_sparc_table2_path_csv)
                existing_sparc_table2_df.columns = [col.strip() for col in existing_sparc_table2_df.columns]
                logger.info(f"Loaded existing Table2_expanded.csv.")
            except Exception as e:
                logger.warning(f"Could not load {existing_sparc_table2_path_csv} as CSV: {e}. Trying original MRT.")
        
        if existing_sparc_table2_df.empty and os.path.exists(existing_sparc_table2_path_mrt):
            try:
                logger.info(f"Loading original SPARC Table2 from {existing_sparc_table2_path_mrt}.")
                # Use pd.read_csv with default settings (inferring separators) for robustness
                existing_sparc_table2_df = pd.read_csv(existing_sparc_table2_path_mrt, engine='python')
                existing_sparc_table2_df.columns = [col.strip() for col in existing_sparc_table2_df.columns]
                logger.info(f"Loaded original Table2.mrt as CSV.")
            except Exception as e:
                logger.error(f"Table2 CSV load failed for original MRT: {e}. ")
                # Fallback to explicit MRT parsing if default CSV fails
                try:
                    logger.warning("Falling back to explicit MRT parsing for Table2.mrt.")
                    with open(existing_sparc_table2_path_mrt, 'r') as f:
                        lines = f.readlines()
                    data_lines = lines[29:] # Data starts around line 30
                    processed_data_table2 = [re.split(r'\s{2,}', line.strip()) for line in data_lines if line.strip() and not line.strip().startswith('----')]
                    existing_sparc_table2_df = pd.DataFrame(processed_data_table2)
                    cols_table2 = ['Galaxy', 'D', 'R', 'Vobs', 'e_Vobs', 'Vgas', 'Vdisk', 'Vbul', 'SBdisk', 'SBbul']
                    existing_sparc_table2_df.columns = cols_table2[:len(existing_sparc_table2_df.columns)]
                    logger.info(f"Loaded original Table2.mrt using regex split.")
                except Exception as e_mrt:
                    logger.error(f"Explicit MRT parsing for Table2 failed: {e_mrt}")

        if existing_sparc_table2_df.empty: # If still empty after all attempts
             logger.warning("No existing Table2 data found or loaded. Starting with new data.")
             
        sparc_table2_template_cols = ['Galaxy', 'D', 'R', 'Vobs', 'e_Vobs', 'Vgas', 'Vdisk', 'Vbul', 'SBdisk', 'SBbul']
        new_rc_to_add = pd.DataFrame(columns=sparc_table2_template_cols)
        
        for col in combined_new_rc_df.columns:
            if col in sparc_table2_template_cols:
                new_rc_to_add[col] = combined_new_rc_df[col]
            else:
                logger.debug(f"Column '{col}' from new RC data not in SPARC Table2 template, skipping.")
        
        for col in sparc_table2_template_cols:
            if col not in new_rc_to_add.columns:
                new_rc_to_add[col] = np.nan
        
        new_rc_to_add = new_rc_to_add[sparc_table2_template_cols]

        final_table2_df = pd.concat([existing_sparc_table2_df, new_rc_to_add], ignore_index=True)
        final_table2_df.to_csv('data/raw_sparc/Table2_expanded.csv', index=False)
        logger.info(f"Expanded Table2 rotation curves saved to data/raw_sparc/Table2_expanded.csv with {len(final_table2_df)} entries.")


if __name__ == "__main__":
    # This script is for ingestion, not fetching. 
    # It relies on fetch_extra_data.py having already downloaded data into data/extra_sources/
    # Therefore, it does not need argparse for catalogs.
    logger.info("Starting data ingestion process...")
    ingest_extra()
    logger.info("Ingestion process finished.")