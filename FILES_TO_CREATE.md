# Complete List of Files to Create

## How to Use This List

Copy each file exactly as shown below, in the correct location within your project structure.

---

## 🎯 CRITICAL: Files Needed in `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\`

### 1. Root Directory Files

**File: `requirements.txt`**
```
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
scikit-learn>=1.0.0
astropy>=4.3
h5py>=3.4
statsmodels>=0.13.0
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0
pyyaml>=5.4
tqdm>=4.62.0
joblib>=1.1.0
pytest>=6.2.0
jupyter>=1.0.0
```

**File: `run_analysis.py`**
- See: `src/main.py` content above (save as is)

**File: `run_analysis.bat`** (Windows only)
- See: Batch file content above (save as is)

**File: `setup.py`**
- See: Setup file content above (save as is)

---

## 🗂️ Files Needed in `src/` Directory

Create directory: `src/`

**File: `src/__init__.py`**
```python
"""
SPARC Radial-Dependent RAR Analysis Package
"""

__version__ = "1.0.0"
__author__ = "CDM Alternative Model Analysis Team"

from . import sparc_loader
from . import rar_fitting
from . import radial_analysis
from . import statistical_tests
from . import visualization

__all__ = [
    'sparc_loader',
    'rar_fitting',
    'radial_analysis',
    'statistical_tests',
    'visualization',
]
```

**Files in `src/`:**
- `sparc_loader.py` - See complete code above
- `rar_fitting.py` - See complete code above
- `radial_analysis.py` - See complete code above
- `statistical_tests.py` - See complete code above
- `visualization.py` - See complete code above
- `main.py` - See complete code above

---

## ⚙️ Files Needed in `config/` Directory

Create directory: `config/`

**File: `config/analysis_config.yaml`**
```yaml
# SPARC Radial-Dependent RAR Analysis Configuration

data:
  sparc_dir: "data/raw_sparc"
  processed_dir: "data/processed"
  output_dir: "output"

analysis:
  n_radial_bins: 2
  a0_bounds: [1e-12, 1e-8]
  
  quality:
    min_points: 8
    min_radial_range_kpc: 5.0
    min_inner_radius_kpc: 0.0
    min_outer_radius_kpc: 10.0
    max_velocity_error_fraction: 0.20

predictions:
  cdm:
    ratio_mean: 1.00
    ratio_std: 0.05
  
  sdh_plus:
    ratio_mean: 1.12
    ratio_std: 0.06

plotting:
  figsize: [14, 11]
  dpi: 300
```

---

## 📚 Documentation Files

Create these in project root:

- `README.md` - See content above
- `SETUP_AND_RUN.md` - See content above
- `QUICK_START.md` - See content above
- `FILE_MANIFEST.md` - See content above
- `PROJECT_SUMMARY.md` - See content above
- `INSTALLATION_CHECKLIST.md` - See content above
- `INDEX.md` - See content above
- `FILES_TO_CREATE.md` - This file

---

## 📦 Your Data Files

**Location: `data/raw_sparc/`**

These are files you should already have from the SPARC website:
- `Table1.mrt`
- `Table2.mrt`
- `rar_all_data.txt`
- `sparc_mass_models/` (directory containing 175 .txt files)

---

## 📋 Complete File Count

| Category | Count | Location |
|----------|-------|----------|
| Root directory files | 4 | Project root |
| Python modules | 7 | `src/` |
| Config files | 1 | `config/` |
| Documentation | 8 | Project root |
| Data files | 175+ | `data/raw_sparc/` |
| **TOTAL** | **195+** | — |

---

## ✅ Verification Checklist

After creating files, verify:

```
CDM_ALT_MODEL_ANALYSIS/
├── src/
│   ├── __init__.py                    ✓
│   ├── sparc_loader.py               ✓
│   ├── rar_fitting.py                ✓
│   ├── radial_analysis.py            ✓
│   ├── statistical_tests.py          ✓
│   ├── visualization.py              ✓
│   └── main.py                       ✓
│
├── config/
│   └── analysis_config.yaml          ✓
│
├── data/raw_sparc/
│   ├── Table1.mrt                    ✓
│   ├── Table2.mrt                    ✓
│   ├── rar_all_data.txt              ✓
│   └── sparc_mass_models/            ✓
│
├── run_analysis.py                   ✓
├── run_analysis.bat                  ✓
├── requirements.txt                  ✓
├── setup.py                          ✓
├── README.md                         ✓
├── SETUP_AND_RUN.md                  ✓
├── QUICK_START.md                    ✓
├── FILE_MANIFEST.md                  ✓
├── PROJECT_SUMMARY.md                ✓
├── INSTALLATION_CHECKLIST.md         ✓
└── INDEX.md                          ✓
```

---

## 🚀 After Creating All Files

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run analysis:
   ```bash
   python run_analysis.py
   ```

3. Check results:
   - `output/tables/interpretation.json`
   - `output/plots/radial_rar_analysis.png`

---

## 📝 Notes

- All Python files use **Python 3.8+**
- All files use **UTF-8 encoding**
- No special characters or formatting issues
- Copy-paste ready (handles line endings)

---

**Status**: All files prepared and ready for setup!  
**Next Step**: Create directory structure and copy files as listed above.