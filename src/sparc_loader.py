"""
SPARC Data Loader and Parser

Loads rotation curves, metadata, and baryonic components from SPARC catalog.
Handles both Table2.mrt (combined) and individual galaxy model files.
"""

import numpy as np
import pandas as pd
import os
import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import json

logger = logging.getLogger(__name__)

class SPARCRotationCurves:
    """
    Load and organize SPARC rotation curve data.
    
    Attributes:
        catalog_path: Path to SPARC data directory
        df_table1: Galaxy metadata (Table1.mrt)
        df_table2: Rotation curve data (Table2.mrt)
        galaxies: List of galaxy names
    """
    
    def __init__(self, sparc_data_dir: str):
        """
        Initialize SPARC loader.
        
        Args:
            sparc_data_dir: Path to directory containing SPARC files
                          Expected structure:
                          - Table1.mrt (galaxy metadata)
                          - Table2.mrt (combined rotation curves)
                          - sparc_mass_models/ (individual galaxy files)
        """
        self.sparc_dir = Path(sparc_data_dir)
        self.mass_models_dir = self.sparc_dir / 'sparc_mass_models'
        
        # Validate directory
        if not self.sparc_dir.exists():
            raise FileNotFoundError(f"SPARC directory not found: {sparc_data_dir}")
        
        logger.info(f"Initializing SPARC loader from {sparc_data_dir}")
        
        # Load metadata and rotation curves
        self.df_table1 = self._load_table1()
        self.df_table2 = self._load_table2()
        self.galaxies = self.df_table1['Galaxy'].unique().tolist()
        
        logger.info(f"Loaded {len(self.galaxies)} galaxies")
        logger.info(f"Total rotation curve points: {len(self.df_table2)}")
    
    def _load_table1(self) -> pd.DataFrame:
        """Load Table1.mrt (galaxy metadata)"""
        table1_path = self.sparc_dir / 'Table1.mrt'
        
        if not table1_path.exists():
            raise FileNotFoundError(f"Table1.mrt not found at {table1_path}")
        
        # Column names and fixed widths for Table1.mrt
        names = [
            'Galaxy', 'T', 'D', 'e_D', 'f_D', 'Inc', 'e_Inc', 'L[3.6]', 'e_L[3.6]',
            'Reff', 'SBeff', 'Rdisk', 'SBdisk', 'MHI', 'RHI', 'Vflat', 'e_Vflat', 'Q', 'Ref.'
        ]
        colspecs = [
            (0, 11), (11, 13), (13, 19), (19, 24), (24, 26), (26, 30), (30, 34),
            (34, 41), (41, 48), (48, 53), (53, 61), (61, 66), (66, 74), (74, 81),
            (81, 86), (86, 91), (91, 96), (96, 99), (99, 113)
        ]
        
        # Data starts after line 98
        try:
            df = pd.read_fwf(str(table1_path), skiprows=98, names=names, colspecs=colspecs)
        except Exception as e:
            logger.warning(f"FWF parsing failed, trying CSV: {e}")
            df = pd.read_csv(str(table1_path), sep='\s+', skiprows=98, names=names, engine='python')
        
        # Clean data
        df['Galaxy'] = df['Galaxy'].str.strip()
        df = df.dropna(subset=['Galaxy'])
        
        logger.info(f"Loaded Table1.mrt: {len(df)} galaxies")
        return df
    
    def _load_table2(self) -> pd.DataFrame:
        """Load Table2.mrt (combined rotation curves)"""
        table2_path = self.sparc_dir / 'Table2.mrt'
        
        if not table2_path.exists():
            raise FileNotFoundError(f"Table2.mrt not found at {table2_path}")
        
        # Column names and fixed widths for Table2.mrt
        names = ['Galaxy', 'D', 'R', 'Vobs', 'e_Vobs', 'Vgas', 'Vdisk', 'Vbul', 'SBdisk', 'SBbul']
        colspecs = [
            (0, 11), (12, 18), (19, 25), (26, 32), (33, 38), (39, 45), (46, 52),
            (53, 59), (60, 67), (68, 76)
        ]
        
        # Data starts after line 25
        try:
            df = pd.read_fwf(str(table2_path), skiprows=25, names=names, colspecs=colspecs)
        except Exception as e:
            logger.warning(f"FWF parsing failed, trying CSV: {e}")
            df = pd.read_csv(str(table2_path), sep='\s+', skiprows=25, names=names, engine='python')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        df['Galaxy'] = df['Galaxy'].str.strip()
        
        # Ensure numeric columns
        numeric_cols = [col for col in df.columns if col not in ['Galaxy']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Standard SPARC M/L ratios at 3.6 microns:
        # Disk: 0.5, Bulge: 0.7
        ML_disk = 0.5
        ML_bulge = 0.7
        
        # Compute total baryonic velocity: V_bar^2 = V_gas^2 + ML_disk*V_disk^2 + ML_bulge*V_bulge^2
        v_gas_sq = np.sign(df['Vgas']) * (df['Vgas']**2)
        v_disk_sq = np.sign(df['Vdisk']) * (df['Vdisk']**2)
        v_bul_sq = np.sign(df['Vbul']) * (df['Vbul']**2)
        
        df['V_bar_sq'] = v_gas_sq + ML_disk * v_disk_sq + ML_bulge * v_bul_sq
        df['V_bar'] = np.sqrt(np.maximum(df['V_bar_sq'], 0))
        
        # Map other names
        df = df.rename(columns={
            'Vobs': 'V_obs',
            'e_Vobs': 'σ_V'
        })
        
        logger.info(f"Loaded Table2.mrt: {len(df)} rotation curve points")
        return df
    
    def load_individual_model(self, galaxy_name: str) -> Optional[Dict]:
        """
        Load individual galaxy mass model from file.
        
        Args:
            galaxy_name: Galaxy name (e.g., 'NGC_0024')
        
        Returns:
            Dictionary with keys: r, v_circ, v_bar, v_dm, errors
            or None if file not found
        """
        # Try various filename conventions
        possible_names = [
            f"{galaxy_name}.txt",
            f"{galaxy_name.upper()}.txt",
            f"{galaxy_name.lower()}.txt",
        ]
        
        model_file = None
        for name in possible_names:
            candidate = self.mass_models_dir / name
            if candidate.exists():
                model_file = candidate
                break
        
        if model_file is None:
            logger.warning(f"Mass model file not found for {galaxy_name}")
            return None
        
        try:
            # Parse individual model file
            data = pd.read_csv(str(model_file), sep='\s+', skiprows=3, engine='python')
            
            # Expected columns: R, V_obs, σ_V, V_bar, σ_Vbar, V_dm, σ_Vdm, ...
            result = {
                'r': data.iloc[:, 0].values,  # Radius
                'v_circ': data.iloc[:, 1].values,  # Observed velocity
                'v_bar': data.iloc[:, 3].values,  # Baryonic velocity
                'errors': {
                    'v_circ': data.iloc[:, 2].values,
                    'v_bar': data.iloc[:, 4].values,
                }
            }
            
            # Optional: DM contribution
            if data.shape[1] > 5:
                result['v_dm'] = data.iloc[:, 5].values
                if data.shape[1] > 6:
                    result['errors']['v_dm'] = data.iloc[:, 6].values
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing {model_file}: {e}")
            return None
    
    def extract_galaxy_profile(self, galaxy_name: str) -> Optional[Dict]:
        """
        Extract rotation curve for single galaxy from Table2.mrt.
        
        Args:
            galaxy_name: Galaxy identifier
        
        Returns:
            Dictionary with keys:
            - r: radius (kpc)
            - v_circ: circular velocity (km/s)
            - g_bar: baryonic acceleration (m/s²)
            - g_obs: observed acceleration (m/s²)
            - errors: velocity and acceleration errors
            or None if galaxy not found
        """
        # Find galaxy data
        gal_mask = self.df_table2['Galaxy'].str.contains(galaxy_name, case=False, na=False)
        gal_data = self.df_table2[gal_mask].copy()
        
        if len(gal_data) == 0:
            logger.warning(f"Galaxy {galaxy_name} not found in Table2.mrt")
            return None
        
        # Clean data
        gal_data = gal_data.dropna(subset=['Galaxy', 'R', 'V_obs', 'V_bar'])
        
        if len(gal_data) < 3:
            logger.warning(f"Galaxy {galaxy_name} has insufficient data points: {len(gal_data)}")
            return None
        
        # Extract columns (handle various naming conventions)
        r = gal_data['R'].values if 'R' in gal_data.columns else gal_data[gal_data.columns[1]].values
        v_circ = gal_data['V_obs'].values if 'V_obs' in gal_data.columns else gal_data[gal_data.columns[2]].values
        v_bar = gal_data['V_bar'].values if 'V_bar' in gal_data.columns else gal_data[gal_data.columns[4]].values
        
        # Compute accelerations
        # Constant to convert (km/s)^2 / kpc to m/s^2
        # 1 km/s = 10^3 m/s
        # 1 kpc = 3.08567758e19 m
        # factor = (10^3)^2 / 3.08567758e19 = 3.24077885e-14
        CONV_FACTOR = 3.24077885e-14
        
        with np.errstate(divide='ignore', invalid='ignore'):
            g_obs = (v_circ ** 2) / r * CONV_FACTOR
            g_bar = (v_bar ** 2) / r * CONV_FACTOR
        
        # Remove invalid values
        valid = np.isfinite(g_obs) & np.isfinite(g_bar) & (r > 0) & (v_circ > 0)
        
        # Convert velocity error to acceleration error
        # dg = 2 * v * dv / r * CONV_FACTOR
        v_err = gal_data['σ_V'].values[valid] if 'σ_V' in gal_data.columns else np.ones_like(v_circ[valid]) * 0.05
        dg_obs = 2 * v_circ[valid] * v_err / r[valid] * CONV_FACTOR
        
        result = {
            'r': r[valid],
            'v_circ': v_circ[valid],
            'g_bar': g_bar[valid],
            'g_obs': g_obs[valid],
            'errors': {
                'v_circ': v_err,
                'g_obs': dg_obs,
                'g_bar': g_bar[valid] * 0.1,  # Assume 10% error on g_bar for weight
            }
        }
        
        return result
    
    def quality_check_galaxy(self, galaxy_data: Dict) -> Tuple[bool, str]:
        """
        Check if galaxy meets quality criteria for analysis.
        
        Args:
            galaxy_data: Galaxy data dictionary
        
        Returns:
            (passes_quality, reason_string)
        """
        reasons = []
        
        # Check 1: Minimum number of points
        n_points = len(galaxy_data['r'])
        if n_points < 8:
            reasons.append(f"Only {n_points} points (need ≥8)")
        
        # Check 2: Radial range
        r_range = galaxy_data['r'].max() - galaxy_data['r'].min()
        if r_range < 5:
            reasons.append(f"Limited radial range: {r_range:.1f} kpc (need ≥5)")
        
        # Check 3: Inner radius
        r_min = galaxy_data['r'].min()
        if r_min > 1.0:
            reasons.append(f"Inner radius too large: {r_min:.1f} kpc (need <1.0)")
        
        # Check 4: Outer radius
        r_max = galaxy_data['r'].max()
        if r_max < 10:
            reasons.append(f"Outer radius too small: {r_max:.1f} kpc (need >10)")
        
        # Check 5: Data quality (large error bars)
        v_errors = galaxy_data['errors']['v_circ']
        median_rel_error = np.median(v_errors / galaxy_data['v_circ'])
        if median_rel_error > 0.20:
            reasons.append(f"Large velocity errors: {median_rel_error*100:.1f}% (need <20%)")
        
        # Check 6: Physical consistency
        if np.any(galaxy_data['g_obs'] < galaxy_data['g_bar']):
            reasons.append("g_obs < g_bar at some radii (unphysical)")
        
        passes = len(reasons) == 0
        reason_str = " | ".join(reasons) if reasons else "PASS"
        
        return passes, reason_str
    
    def get_quality_galaxies(self) -> List[str]:
        """
        Return list of galaxies passing quality checks.
        
        Returns:
            List of galaxy names suitable for analysis
        """
        quality_galaxies = []
        
        for gal_name in self.galaxies:
            gal_data = self.extract_galaxy_profile(gal_name)
            if gal_data is None:
                continue
            
            passes, _ = self.quality_check_galaxy(gal_data)
            if passes:
                quality_galaxies.append(gal_name)
        
        logger.info(f"Quality galaxies: {len(quality_galaxies)}/{len(self.galaxies)}")
        return quality_galaxies
    
    def save_quality_report(self, output_path: str):
        """Generate and save quality control report."""
        report = []
        
        for gal_name in self.galaxies:
            gal_data = self.extract_galaxy_profile(gal_name)
            if gal_data is None:
                passes, reason = False, "Data not found"
            else:
                passes, reason = self.quality_check_galaxy(gal_data)
            
            report.append({
                'Galaxy': gal_name,
                'Passes': passes,
                'Reason': reason,
                'N_points': len(gal_data['r']) if gal_data else 0,
                'R_range_kpc': gal_data['r'].max() - gal_data['r'].min() if gal_data else 0,
            })
        
        df_report = pd.DataFrame(report)
        df_report.to_csv(output_path, index=False)
        logger.info(f"Quality report saved to {output_path}")
        
        return df_report