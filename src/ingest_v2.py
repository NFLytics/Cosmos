import pandas as pd, glob, os
import numpy as np

def ingest():
    print("Starting master ingestion for maximal dataset expansion...")
    
    # 1. Load metadata
    meta = pd.read_csv('data/raw_sparc/rar_all_data.txt', sep=r'\s+', comment='#', 
                       names=['galaxy','dist','inc','lum','type','v_flat','m_hi'], 
                       on_bad_lines='skip')
    
    data = []
    
    # 2. Load SPARC LTGs
    ltg_files = glob.glob('data/raw_sparc/sparc_mass_models/*.txt')
    print(f"Found {len(ltg_files)} LTG files.")
    for f in ltg_files:
        try:
            df = pd.read_csv(f, sep=r'\s+', comment='#', 
                             names=['r_kpc','v_obs','v_obs_err','v_gas','v_disk','v_bulge','sb_disk','sb_bulge'])
            df = df.assign(galaxy=os.path.basename(f).replace('.txt',''), source_type='LTG')
            data.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")

    # 3. Load ETGs
    etg_files = glob.glob('*.dens')
    print(f"Found {len(etg_files)} ETG files.")
    for f in etg_files:
        try:
            df = pd.read_csv(f, sep=r'\s+', comment='#', 
                             names=['r_kpc','sb_disk','sb_bulge'])
            df = df.assign(galaxy=os.path.basename(f).replace('.dens',''), source_type='ETG')
            # Initialize missing columns
            for col in ['v_obs','v_obs_err','v_gas','v_disk','v_bulge']:
                df[col] = np.nan
            data.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")

    # 4. Load Extra Sources (Experimental)
    extra_files = glob.glob('data/extra_sources/*.csv')
    print(f"Processing {len(extra_files)} extra source tables...")
    for f in extra_files:
        if 'table_2' in f: # Usually the data table
            try:
                df_extra = pd.read_csv(f)
                if 'Name' in df_extra.columns and 'Vel' in df_extra.columns:
                    # Map to standard format
                    df_mapped = pd.DataFrame({
                        'galaxy': df_extra['Name'],
                        'v_obs': df_extra['Vel'],
                        'source_type': 'EXTRA'
                    })
                    # Add dummy/nan for others
                    for col in ['r_kpc','v_obs_err','v_gas','v_disk','v_bulge','sb_disk','sb_bulge']:
                        df_mapped[col] = np.nan
                    data.append(df_mapped)
            except:
                pass

    if not data:
        print("No data found to ingest!")
        return

    full = pd.concat(data, ignore_index=True)
    
    # Merge with metadata
    full = full.merge(meta[['galaxy','dist','inc','lum','type']], on='galaxy', how='left')
    
    # Numeric cleanup
    cols = ['r_kpc','v_obs','v_obs_err','v_gas','v_disk','v_bulge','sb_disk','sb_bulge','dist','inc','lum']
    for col in cols:
        if col in full.columns:
            full[col] = pd.to_numeric(full[col], errors='coerce')
    
    full.to_csv('data/standardized_cosmos_v2.csv', index=False)
    print(f'Ingest Complete: {len(full)} records across {full.galaxy.nunique()} galaxies.')
    print(f'Maximal dataset saved to data/standardized_cosmos_v2.csv')

if __name__ == '__main__': 
    ingest()
