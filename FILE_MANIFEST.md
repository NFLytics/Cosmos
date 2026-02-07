# Project File Manifest

## Complete List of Files Needed

### Configuration Files (Copy to project root)
- ✅ `requirements.txt` - Python dependencies
- ✅ `setup.py` - Package configuration
- ✅ `run_analysis.py` - Main entry point (Python)
- ✅ `run_analysis.bat` - Main entry point (Windows)

### Source Code (Copy to `src/` directory)
- ✅ `src/__init__.py` - Package initialization
- ✅ `src/main.py` - Main orchestrator
- ✅ `src/sparc_loader.py` - Data loading and parsing
- ✅ `src/rar_fitting.py` - RAR formula and fitting
- ✅ `src/radial_analysis.py` - Radial-dependent analysis
- ✅ `src/statistical_tests.py` - Statistical interpretation
- ✅ `src/visualization.py` - Plotting utilities

### Configuration Files (Copy to `config/` directory)
- ✅ `config/analysis_config.yaml` - Analysis parameters

### Documentation (Reference only)
- `README.md` - Project overview
- `SETUP_AND_RUN.md` - Detailed setup instructions
- `QUICK_START.md` - Quick reference
- `FILE_MANIFEST.md` - This file

### Data (User-provided)
- Place SPARC files in `data/raw_sparc/`:
  - `Table1.mrt`
  - `Table2.mrt`
  - `rar_all_data.txt`
  - `sparc_mass_models/` (directory with 175 galaxy files)

### Auto-Created Directories (Script creates these)
- `data/processed/` - Intermediate results
- `data/cache/` - Temporary files
- `output/plots/` - Generated figures
- `output/tables/` - CSV results
- `output/reports/` - Text reports
- `logs/` - Analysis logs

## File Sizes (Approximate)

| File | Size |
|------|------|
| Table1.mrt | 50 KB |
| Table2.mrt | 500 KB |
| sparc_mass_models/ (175 files) | 10 MB |
| Complete source code | 100 KB |
| Output (plots + tables) | 5 MB |

## Directory Tree (After Setup)

```
C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\
│
├── README.md
├── SETUP_AND_RUN.md
├── QUICK_START.md
├── FILE_MANIFEST.md
│
├── requirements.txt
├── setup.py
├── run_analysis.py
├── run_analysis.bat
│
├── config/
│   ├── __init__.py
│   └── analysis_config.yaml
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── sparc_loader.py
│   ├── rar_fitting.py
│   ├── radial_analysis.py
│   ├── statistical_tests.py
│   └── visualization.py
│
├── data/
│   ├── raw_sparc/                     [YOUR SPARC FILES]
│   │   ├── Table1.mrt
│   │   ├── Table2.mrt
│   │   ├── rar_all_data.txt
│   │   └── sparc_mass_models/
│   │       ├── NGC_0024.txt
│   │       ├── NGC_0100.txt
│   │       └── ...
│   │
│   ├── processed/                      [AUTO-CREATED]
│   ├── cache/                          [AUTO-CREATED]
│
├── output/                             [AUTO-CREATED]
│   ├── plots/
│   │   └── radial_rar_analysis.png
│   ├── tables/
│   │   ├── galaxies_quality_check.csv
│   │   ├── radial_fits_results.csv
│   │   ├── interpretation.json
│   │   └── interpretation_summary.txt
│   └── reports/
│
├── logs/                               [AUTO-CREATED]
│   └── analysis.log
│
└── tests/                              [OPTIONAL]
    ├── __init__.py
    ├── test_sparc_loader.py
    ├── test_rar_fitting.py
    └── test_statistics.py
```

## Checklist for Setup

Before running:

- [ ] Python 3.8+ installed and accessible
- [ ] All files from "Configuration Files" copied to project root
- [ ] All files from "Source Code" copied to `src/` directory
- [ ] `config/analysis_config.yaml` copied to `config/`
- [ ] SPARC files (Table1.mrt, Table2.mrt, sparc_mass_models/) in `data/raw_sparc/`
- [ ] `requirements.txt` dependency package installed
- [ ] Running from project root directory
- [ ] Write permissions in project directory

## Usage

### Minimal Setup
```bash
# 1. Copy all Python files to src/
# 2. Copy config to config/
# 3. Put SPARC data in data/raw_sparc/
# 4. Install requirements
pip install -r requirements.txt

# 5. Run
python run_analysis.py
```

### With Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run
python run_analysis.py
```

---

**Version**: 1.0
**Last Updated**: 2026-02-07
**Status**: Ready for deployment