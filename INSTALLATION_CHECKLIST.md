# Installation Checklist

Complete this checklist to ensure all files are properly organized.

## Phase 1: Create Directory Structure

- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\src\` directory
- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\config\` directory
- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\data\` directory
- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\data\raw_sparc\` directory
- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\output\` directory
- [ ] Create `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\logs\` directory

## Phase 2: Copy Python Files to `src/`

Copy these files to `src/` directory:

- [ ] `__init__.py` (create empty file)
- [ ] `sparc_loader.py` 
- [ ] `rar_fitting.py`
- [ ] `radial_analysis.py`
- [ ] `statistical_tests.py`
- [ ] `visualization.py`
- [ ] `main.py`

## Phase 3: Copy Configuration Files

- [ ] `config/analysis_config.yaml` → `config/analysis_config.yaml`
- [ ] `requirements.txt` → project root

## Phase 4: Copy Main Scripts to Project Root

- [ ] `run_analysis.py` → project root
- [ ] `run_analysis.bat` → project root (Windows only)

## Phase 5: Copy Documentation

- [ ] `README.md` → project root
- [ ] `SETUP_AND_RUN.md` → project root
- [ ] `QUICK_START.md` → project root

## Phase 6: Organize SPARC Data

Copy your SPARC files to `data/raw_sparc/`:

- [ ] `Table1.mrt` (from your downloads)
- [ ] `Table2.mrt` (from your downloads)
- [ ] `rar_all_data.txt` (from your downloads)
- [ ] `sparc_mass_models/` directory with 175 galaxy files

## Phase 7: Install Python Dependencies

Open Command Prompt in project root and run:

```bash
pip install -r requirements.txt
```

- [ ] NumPy installed
- [ ] Pandas installed
- [ ] SciPy installed
- [ ] Matplotlib installed
- [ ] Seaborn installed
- [ ] All other dependencies installed

## Phase 8: Verify Installation

Run this test command:

```bash
python -c "from src.sparc_loader import SPARCRotationCurves; print('Installation successful!')"
```

- [ ] Test command succeeded (no errors)

## Phase 9: Run Full Analysis

```bash
python run_analysis.py
```

- [ ] Analysis completes without errors
- [ ] Results appear in `output/tables/` and `output/plots/`
- [ ] Console shows final verdict (SDH+ or ΛCDM)

## Expected Final Structure

```
C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\
├── src/
│   ├── __init__.py ✓
│   ├── sparc_loader.py ✓
│   ├── rar_fitting.py ✓
│   ├── radial_analysis.py ✓
│   ├── statistical_tests.py ✓
│   ├── visualization.py ✓
│   └── main.py ✓
│
├── config/
│   └── analysis_config.yaml ✓
│
├── data/
│   ├── raw_sparc/
│   │   ├── Table1.mrt ✓
│   │   ├── Table2.mrt ✓
│   │   ├── rar_all_data.txt ✓
│   │   └── sparc_mass_models/ ✓
│   ├── processed/
│   └── cache/
│
├── output/
│   ├── plots/
│   ├── tables/
│   └── reports/
│
├── logs/
│
├── run_analysis.py ✓
├── run_analysis.bat ✓
├── requirements.txt ✓
├── README.md ✓
├── SETUP_AND_RUN.md ✓
└── QUICK_START.md ✓
```

## Troubleshooting Installation

### Issue: "FileNotFoundError: No module named 'src'"

**Solution**: 
- Verify you're running from the project root directory
- Verify `src/__init__.py` exists
- Verify `src/*.py` files are in place

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "Table1.mrt not found"

**Solution**:
- Verify SPARC files are in `data/raw_sparc/`
- Verify path is exact: `data/raw_sparc/Table1.mrt`
- On Windows, path is case-insensitive, but filename must match exactly

### Issue: "Cannot import yaml"

**Solution**:
```bash
pip install pyyaml
```

---

**Estimated Installation Time**: 5-10 minutes
**Once Complete**: Ready to run analysis!

For detailed help, see `SETUP_AND_RUN.md`