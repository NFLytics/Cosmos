# ADQL-Migrated Astronomical Dataset Summary

| Category | Source | Rows | Schema (First 4 Cols) |
| :--- | :--- | :--- | :--- |
| Planetary | NASA_PS | 39315 | pl_name, hostname, pl_orbper |
| Planetary | TESS_TOI | 7890 | toi, ra, dec, st_dist |
| Stars | Gaia_DR3 | 5000 | RA_ICRS, DE_ICRS, Source, e_RA_ICRS |
| Stars | 2MASS_PSC | 1768 | ra, dec, err_maj, err_min |
| StarSystems | WDS_Summary | 5000 | WDS, Disc, Comp, Obs1 |
| Galaxy | PGC_Extragal | 5000 | PGC, RAJ2000, DEJ2000, OType |
| Galaxy | SDSS_DR16 | 5000 | objID, RA_ICRS, DE_ICRS, mode |
| Clusters | Open_Clusters | 5000 | main_id, ra, dec, otype |
| Clusters | Globular_Clust | 5000 | main_id, ra, dec, otype |
| SuperClusters | LSS_LargeScale | 5000 | main_id, ra, dec, otype |
| BlackHoles | Fermi_LAT_BH | 1 | name, ra, dec, flux_1_100_gev |
| BlackHoles | Chandra_Master | 187 | obsid, status, name, ra |