"""
SPARC Data Loader v2 - Enhanced with Flexible Quality Control
Updated to load expanded CSVs or fall back to original MRTs.
Also improved error handling and column mapping.
"""

import numpy as np
import pandas as pd
import os
import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import json
import re

logger = logging.getLogger(__name__)

class QualityCriteria:
    """Define quality control thresholds"""
    
    def __init__(self, strictness='relaxed'):
        """
        Initialize quality criteria.
        
        Args:
            strictness: 'strict' (original), 'relaxed' (expanded), or 'minimal' (loose)
        """
        if strictness == 'strict':
            self.min_points = 8
            self.min_radial_range_kpc = 5.0
            self.min_inner_radius_kpc = 0.0
            self.max_inner_radius_kpc = 1.0
            self.min_outer_radius_kpc = 10.0
            self.max_velocity_error_fraction = 0.20
            self.name = "STRICT"
        
        elif strictness == 'relaxed':
            self.min_points = 6
            self.min_radial_range_kpc = 4.0
            self.min_inner_radius_kpc = 0.0
            self.max_inner_radius_kpc = 2.0
            self.min_outer_radius_kpc = 8.0
            self.max_velocity_error_fraction = 0.25
            self.name = "RELAXED"
        
        elif strictness == 'minimal':
            self.min_points = 5
            self.min_radial_range_kpc = 3.0
            self.min_inner_radius_kpc = 0.0
            self.max_inner_radius_kpc = 3.0
            self.min_outer_radius_kpc = 6.0
            self.max_velocity_error_fraction = 0.30
            self.name = "MINIMAL"
        
        elif strictness == 'maximal':
            self.min_points = 3
            self.min_radial_range_kpc = 0.0
            self.min_inner_radius_kpc = 0.0
            self.max_inner_radius_kpc = 100.0
            self.min_outer_radius_kpc = 0.0
            self.max_velocity_error_fraction = 1.0
            self.name = "MAXIMAL"
        
        else:
            raise ValueError(f"Unknown strictness: {strictness}")
    
    def __repr__(self):
        return f"QualityCriteria({self.name})"


class SPARCRotationCurvesV2:
    """Enhanced SPARC loader with flexible quality control"""
    
    def __init__(self, sparc_data_dir: str, strictness: str = 'relaxed'):
        """
        Initialize SPARC loader with flexible criteria.
        
        Args:
            sparc_data_dir: Path to SPARC data directory
            strictness: 'strict', 'relaxed', or 'minimal'
        """
        self.sparc_dir = Path(sparc_data_dir)
        self.mass_models_dir = self.sparc_dir / 'sparc_mass_models'
        self.quality_criteria = QualityCriteria(strictness)
        
        logger.info(f"Initializing SPARC loader with {strictness.upper()} criteria")
        
        # Load metadata and rotation curves
        self.df_table1 = self._load_table1()
        self.df_table2 = self._load_table2()
        
        # Map Table1 columns
        if 'Galaxy' not in self.df_table1.columns:
            # Fallback for ID/Name
            if 'ID' in self.df_table1.columns:
                self.df_table1 = self.df_table1.rename(columns={'ID': 'Galaxy'})
            # If no 'Galaxy' or 'ID', try to use the first column if it looks like a name
            elif self.df_table1.columns[0] not in ['Galaxy', 'ID']: 
                self.df_table1 = self.df_table1.rename(columns={self.df_table1.columns[0]: 'Galaxy'})
            else:
                if 'Galaxy' not in self.df_table1.columns:
                    raise KeyError("Galaxy column not found in Table1 metadata.")
        
        # Ensure 'Galaxy' column is always first for consistency
        if 'Galaxy' in self.df_table1.columns:
            cols = ['Galaxy'] + [col for col in self.df_table1.columns if col != 'Galaxy']
            self.df_table1 = self.df_table1[cols]
        else:
            raise KeyError("Galaxy column not found in Table1 metadata after potential rename.")

        # Discovery: use files from sparc_mass_models to get full galaxy list if available
        if self.mass_models_dir.exists():
            self.galaxies = [f.stem for f in self.mass_models_dir.glob('*.txt')]
            logger.info(f"Discovered {len(self.galaxies)} galaxies from {self.mass_models_dir}")
        else:
            self.galaxies = self.df_table1['Galaxy'].unique().tolist()
        
        # Add galaxy metadata
        self.galaxy_metadata = self._extract_galaxy_metadata()
        
        logger.info(f"Loaded {len(self.galaxies)} galaxies total")
    
    def _load_table1(self) -> pd.DataFrame:
        """Load Table1 metadata, prioritizing expanded/cleaned CSV, falling back to original MRT."""
        paths = [
            self.sparc_dir / 'Table1_cleaned.csv',
            self.sparc_dir / 'Table1_expanded.csv',
            self.sparc_dir / 'Table1.mrt'
        ]
        
        file_to_load = None
        for path in paths:
            if path.exists():
                file_to_load = str(path)
                break
        
        if not file_to_load:
            raise FileNotFoundError("Table1.mrt or Table1_cleaned.csv not found.")

        logger.info(f"Loading Table1 from: {file_to_load}")
        try:
            df = pd.read_csv(file_to_load)
            df.columns = [col.strip() for col in df.columns]
            return df
        except Exception as e:
            logger.error(f"Table1 load failed for {file_to_load}: {e}")
            raise

    def _load_table2(self) -> pd.DataFrame:
        """Load Table2 metadata, prioritizing expanded/cleaned CSV, falling back to original MRT."""
        paths = [
            self.sparc_dir / 'Table2_cleaned.csv',
            self.sparc_dir / 'Table2_expanded.csv',
            self.sparc_dir / 'Table2.mrt'
        ]
        
        file_to_load = None
        for path in paths:
            if path.exists():
                file_to_load = str(path)
                break
        
        if not file_to_load:
            raise FileNotFoundError("Table2.mrt or Table2_cleaned.csv not found.")

        logger.info(f"Loading Table2 from: {file_to_load}")
        try:
            df = pd.read_csv(file_to_load)
            df.columns = [col.strip() for col in df.columns]
            return df
        except Exception as e:
            logger.error(f"Table2 load failed for {file_to_load}: {e}")
            raise
    
    def _extract_galaxy_metadata(self) -> Dict:
        """Extract metadata for each galaxy"""
        metadata = {}
        for gal_name in self.galaxies:
            try:
                # Use .loc to avoid SettingWithCopyWarning and ensure correct row access
                gal_row = self.df_table1.loc[self.df_table1['Galaxy'] == gal_name].iloc[0]
                metadata[gal_name] = {
                    'name': gal_name,
                    'morphology': self._infer_morphology(gal_name),
                    'distance_mpc': gal_row.get('D', np.nan),
                    'inclination': gal_row.get('Inc', np.nan),
                }
            except IndexError:
                logger.warning(f"Galaxy '{gal_name}' not found in Table1 metadata for properties.")
                # If galaxy name from metadata is not found (e.g., due to parsing issues or new galaxies)
                metadata[gal_name] = {'name': gal_name, 'morphology': self._infer_morphology(gal_name)}
            except KeyError as e:
                logger.warning(f"Missing expected column in metadata for galaxy '{gal_name}': {e}")
                metadata[gal_name] = {'name': gal_name, 'morphology': self._infer_morphology(gal_name)}
        return metadata
    
    def _infer_morphology(self, galaxy_name: str) -> str:
        name_upper = str(galaxy_name).upper()
        if any(kw in name_upper for kw in ['DDO', 'UGCA', 'D5', 'F5']): return 'dwarf'
        if any(kw in name_upper for kw in ['NGC', 'UGC', 'ESO', 'IC', 'PGC']): return 'spiral'
        return 'unknown'
    
    def extract_galaxy_profile(self, galaxy_name: str) -> Optional[Dict]:
        # Try to get from Table2 first
        gal_data = self.df_table2[self.df_table2['Galaxy'] == galaxy_name].copy()
        
        # If Table2 is empty or mostly NaNs, try the individual file
        if len(gal_data) < 3 or gal_data['Vobs'].isna().sum() > len(gal_data) - 3:
            # Try individual file in sparc_mass_models
            file_path = self.sparc_dir / 'sparc_mass_models' / f"{galaxy_name.replace(' ', '')}.txt"
            if file_path.exists():
                logger.info(f"Loading data for {galaxy_name} from individual file: {file_path}")
                try:
                    # Skip header lines (starting with #)
                    df_ind = pd.read_csv(file_path, sep=r'\s+', comment='#', 
                                         names=['R', 'Vobs', 'e_Vobs', 'Vgas', 'Vdisk', 'Vbul', 'SBdisk', 'SBbul'])
                    gal_data = df_ind
                except Exception as e:
                    logger.warning(f"Failed to load individual file for {galaxy_name}: {e}")
            else:
                # Try with different naming convention (e.g. NGC0024 instead of NGC 24)
                # (Already handled by replace(' ', '') above)
                pass

        if len(gal_data) < 3: 
            logger.warning(f"Galaxy {galaxy_name} has insufficient data points for analysis.")
            return None
        
        # Ensure columns are numeric, coerce errors to NaN
        numeric_cols = ['R', 'Vobs', 'e_Vobs', 'Vgas', 'Vdisk', 'Vbul']
        for col in numeric_cols:
            if col in gal_data.columns:
                gal_data[col] = pd.to_numeric(gal_data[col], errors='coerce')
        
        # Drop rows with NaN in critical columns
        gal_data = gal_data.dropna(subset=['R', 'Vobs'])
        
        if len(gal_data) < 3:
            return None

        r = gal_data['R'].values
        v_obs = gal_data['Vobs'].values
        v_gas = gal_data['Vgas'].values if 'Vgas' in gal_data.columns else np.zeros_like(v_obs)
        v_disk = gal_data['Vdisk'].values if 'Vdisk' in gal_data.columns else np.zeros_like(v_obs)
        v_bul = gal_data['Vbul'].values if 'Vbul' in gal_data.columns else np.zeros_like(v_obs)
        v_err = gal_data['e_Vobs'].values if 'e_Vobs' in gal_data.columns else np.full_like(v_obs, 0.05 * v_obs)
        
        # Conversion factor from (km/s)^2 / kpc to m/s^2
        conv = 3.24078e-14
        
        # Total baryonic velocity: v_bar^2 = v_gas^2 + Ups_disk * v_disk^2 + Ups_bulge * v_bul^2
        # Using McGaugh 2016 reference values for 3.6um: disk=0.5, bulge=0.7
        v_bar_sq = v_gas**2 + 0.5 * v_disk**2 + 0.7 * v_bul**2
        
        with np.errstate(divide='ignore', invalid='ignore'):
            g_obs = (v_obs ** 2) / r * conv
            g_bar = v_bar_sq / r * conv
        
        # Apply validity mask after all calculations
        # Ensure r > 0, v_err is finite and non-negative, g_obs/g_bar are finite
        valid = np.isfinite(g_obs) & np.isfinite(g_bar) & (r > 0) & \
                np.isfinite(v_err) & (v_err >= 0) & (v_obs > 0)
        
        # Calculate g_obs_err from v_err propagation
        # dg = 2 * v / r * dv * conv = 2 * sqrt(g_obs * conv_factor_inv) * dv * conv
        # Ensure division by zero is handled for g_obs_err calculation
        with np.errstate(divide='ignore', invalid='ignore'):
            g_obs_err = 2 * np.sqrt(g_obs) * v_err / np.sqrt(r) * conv
        
        return {
            'r': r[valid],
            'v_circ': v_obs[valid],
            'g_bar': g_bar[valid],
            'g_obs': g_obs[valid],
            'errors': {
                'v_circ': v_err[valid],
                'g_obs': g_obs_err[valid],
                # Assuming default g_bar error if not provided or calculated
                'g_bar': np.ones_like(g_bar[valid]) * 0.05 * g_bar[valid], 
            }
        }
    
    def quality_check_galaxy(self, galaxy_data: Dict) -> Tuple[bool, str]:
        reasons = []
        c = self.quality_criteria
        
        r_values = galaxy_data.get('r', np.array([]))
        v_obs_values = galaxy_data.get('v_circ', np.array([]))
        g_obs_values = galaxy_data.get('g_obs', np.array([]))
        g_bar_values = galaxy_data.get('g_bar', np.array([]))
        v_err_values = galaxy_data.get('errors', {}).get('v_circ', np.array([]))
        
        if len(r_values) == 0:
            reasons.append("No radial points")
            
        if len(r_values) < c.min_points: reasons.append(f"Points({len(r_values)}<{c.min_points})")
        
        if len(r_values) > 0:
            if (r_values.max() - r_values.min()) < c.min_radial_range_kpc: reasons.append("Range")
            if r_values.min() > c.max_inner_radius_kpc: reasons.append("InnerR")
            if r_values.max() < c.min_outer_radius_kpc: reasons.append("OuterR")
        else:
            reasons.append("Empty radial data for range check")
        
        # Check velocity errors relative to observed velocity
        if 'v_circ' in galaxy_data['errors'] and len(v_obs_values) > 0 and np.any(v_obs_values != 0):
            # Ensure v_circ is not zero to avoid division by zero
            valid_error_indices = v_obs_values != 0
            if np.sum(valid_error_indices) > 0:
                try:
                    median_rel_error = np.median(v_err_values[valid_error_indices] / v_obs_values[valid_error_indices])
                    if median_rel_error > c.max_velocity_error_fraction: reasons.append("Err")
                except FloatingPointError:
                    reasons.append("ErrCalcError") # Error during calculation
            else:
                reasons.append("Zero velocity for error calculation")
        else:
            reasons.append("Missing or invalid velocity errors")
        
        # Check for unphysical g_obs < g_bar, but only if both are valid and finite
        if self.quality_criteria.name != "MAXIMAL" and 'g_obs' in galaxy_data and 'g_bar' in galaxy_data and len(g_obs_values) > 0 and len(g_bar_values) > 0:
            finite_mask = np.isfinite(g_obs_values) & np.isfinite(g_bar_values)
            if np.sum(finite_mask) > 0:
                # Relaxed check: only fail if g_obs is significantly less than g_bar
                if np.any(g_obs_values[finite_mask] < 0.7 * g_bar_values[finite_mask]):
                    reasons.append("g_obs<<g_bar")
        
        return len(reasons) == 0, " | ".join(reasons) if reasons else "PASS"
    
    def get_quality_galaxies(self) -> List[str]:
        quality_galaxies = []
        for gal_name in self.galaxies:
            try:
                d = self.extract_galaxy_profile(gal_name)
                if d is not None:
                    passes, _ = self.quality_check_galaxy(d)
                    if passes:
                        quality_galaxies.append(gal_name)
            except Exception as e:
                logger.warning(f"Skipping galaxy {gal_name} due to error in profile extraction or quality check: {e}")
        logger.info(f"Quality galaxies ({self.quality_criteria.name}): {len(quality_galaxies)}/{len(self.galaxies)}")
        return quality_galaxies
    
    def save_quality_report(self, output_path: str):
        report = []
        for g in self.galaxies:
            d = self.extract_galaxy_profile(g)
            passes, reason = self.quality_check_galaxy(d) if d else (False, "NoData")
            report.append({'Galaxy': g, 'Passes': passes, 'Reason': reason})
        df = pd.DataFrame(report)
        df.to_csv(output_path, index=False)
        logger.info(f"Quality report saved to {output_path}")
        return df

    def get_galaxies_by_morphology(self, morphology: str) -> List[str]:
        return [g for g in self.galaxies if self.galaxy_metadata.get(g, {}).get('morphology') == morphology]
