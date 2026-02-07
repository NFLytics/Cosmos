# SPARC Radial-Dependent RAR Analysis - Complete Setup and Run Guide

## Overview

This project analyzes SPARC galaxy rotation curves to test whether the MOND acceleration scale (a₀) shows scale-dependence, which would support SDH+ (Superfluid Dark Halos Plus) over ΛCDM.

## Prerequisites

- **Python 3.8+** installed
- **Your SPARC data files** in `C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\data\raw_sparc\`

## Step 1: Create Directory Structure

Create the following directory structure in your project root:

```
C:\Users\radar\Downloads\CDM_ALT_MODEL_ANALYSIS\
│
├── data/
│   ├── raw_sparc/              ← Place SPARC files here
│   │   ├── Table1.mrt
│   │   ├── Table2.mrt
│   │   ├── rar_all_data.txt
│   │   └── sparc_mass_models/
│   │
│   ├── processed/              ← Created by script
│   └── cache/                  ← Created by script
│
├── src/                        ← Copy Python scripts here
│   ├── __init__.py
│   ├── sparc_loader.py
│   ├── rar_fitting.py
│   ├── radial_analysis.py
│   ├── statistical_tests.py
│   ├── visualization.py
│   └── main.py
│
├── config/                     ← Copy config files here
│   ├── analysis_config.yaml
│   └── galaxy_whitelist.txt
│
├── output/                     ← Created by script
│   ├── plots/
│   ├── tables/
│   └── reports/
│
├── logs/                       ← Created by script
│
├── run_analysis.py             ← Copy this main script
├── requirements.txt            ← Copy this file
└── setup.py                    ← Optional
```

## Step 2: Install Dependencies

Open Command Prompt in your project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- numpy, scipy, pandas (numerical computing)
- matplotlib, seaborn (plotting)
- scikit-learn (statistical analysis)
- pyyaml (configuration)
- tqdm (progress bars)

## Step 3: Organize SPARC Data

Ensure your SPARC files are in `data/raw_sparc/`:

```
data/raw_sparc/
├── Table1.mrt                    (Galaxy metadata - 175 galaxies)
├── Table2.mrt                    (Rotation curves - combined)
├── rar_all_data.txt              (Pre-computed RAR data)
└── sparc_mass_models/
    ├── NGC_0024.txt
    ├── NGC_0100.txt
    ├── ...
    └── UGC_12591.txt             (175 individual files)
```

## Step 4: Run the Analysis

### Option A: Command Line (Simplest)

```bash
python run_analysis.py
```

This will:
1. Load SPARC data
2. Run quality control
3. Fit RAR to inner and outer radii of each galaxy
4. Compute scale-dependence statistics
5. Generate interpretation and plots
6. Save all results

### Option B: Python Interactive (for debugging)

```python
from src.sparc_loader import SPARCRotationCurves
from src.radial_analysis import RadialDependenceAnalyzer
from src.statistical_tests import StatisticalInterpreter
from src.visualization import RARVisualizer

# Load data
sparc = SPARCRotationCurves('data/raw_sparc')

# Get quality galaxies
quality_galaxies = sparc.get_quality_galaxies()
print(f"Found {len(quality_galaxies)} quality galaxies")

# Analyze
analyzer = RadialDependenceAnalyzer(n_radial_bins=2)
galaxy_data_list = [(name, sparc.extract_galaxy_profile(name)) 
                   for name in quality_galaxies]
df_results = analyzer.analyze_ensemble(galaxy_data_list)

# Interpret
interpreter = StatisticalInterpreter()
interpretation = interpreter.interpret_results(df_results)
interpreter.print_interpretation(interpretation)

# Plot
visualizer = RARVisualizer()
visualizer.plot_ensemble_results(df_results, interpretation)
```

## Expected Output

### Console Output:

```
======================================================================
SPARC RADIAL-DEPENDENT RAR ANALYSIS
Testing SDH+ vs ΛCDM with existing data
======================================================================

Step 1: Loading SPARC data...
[2026-02-XX XX:XX:XX] Loaded 175 galaxies
[2026-02-XX XX:XX:XX] Loaded 2693 rotation curve points

Step 2: Running quality control...
Quality galaxies: 152/175

Step 3: Analyzing radial dependence...
Analyzing 152 quality galaxies...
...

Step 4: Interpreting results...

======================================================================
ENSEMBLE ANALYSIS RESULTS (152/175 galaxies)
======================================================================
Mean ratio a0(inner) / a0(outer): 1.XXXX
Std of ratios: 0.XXXX
Mean z-score: X.XXσ
Combined significance: XX.Xσ
======================================================================

... detailed statistics ...

======================================================================
RADIAL-DEPENDENT RAR ANALYSIS: INTERPRETATION
======================================================================

VERDICT: SDH+ or ΛCDM
Confidence: HIGH or LOW

[Detailed interpretation follows]
```

### Output Files:

After running, check these outputs:

```
output/tables/
├── galaxies_quality_check.csv        (Quality control results)
├── radial_fits_results.csv           (Detailed fits for each galaxy)
├── interpretation.json               (Statistical results)
└── interpretation_summary.txt        (Human-readable summary)

output/plots/
└── radial_rar_analysis.png          (4-panel diagnostic figure)
```

## Key Results to Look For

### If the analysis supports **SDH+**:

- **Mean ratio**: a₀(inner) / a₀(outer) > 1.05
- **Combined significance**: > 2σ (ideally > 3σ)
- **Interpretation**: "RG-running coupling detected"
- **Implication**: Quantum effects manifest at galactic scales

### If the analysis supports **ΛCDM**:

- **Mean ratio**: a₀(inner) / a₀(outer) ≈ 1.00 (within ~2%)
- **Combined significance**: < 1σ
- **Interpretation**: "Scale-independent a₀ (universal)"
- **Implication**: Feedback alone explains properties

## Troubleshooting

### Error: "FileNotFoundError: Table1.mrt not found"

**Solution**: Verify SPARC files are in `data/raw_sparc/` directory. Check that:
- File names match exactly (case-sensitive on Linux)
- Path is correct

### Error: "Only X quality galaxies - analysis may be unreliable"

**Possible causes**:
- SPARC data files are incomplete or corrupted
- Quality thresholds are too strict

**Solution**: Check output/tables/galaxies_quality_check.csv for details on which galaxies failed.

### Error: "Fitting failed"

**Possible causes**:
- Rotation curve has insufficient points
- Errors are very large
- Galaxy has physical inconsistencies

**Solution**: Check individual galaxy in output/tables/radial_fits_results.csv.

### Plots not appearing

**Solution**: Check that output/plots/ directory exists and has write permissions:

```python
import os
os.makedirs('output/plots', exist_ok=True)
```

## Understanding the Results

### Main Diagnostic Figure (4 panels):

1. **Top Left - Ratio Histogram**: 
   - Shows distribution of a₀(inner) / a₀(outer) for all galaxies
   - Red dashed line = ΛCDM prediction (1.00)
   - Blue dashed line = SDH+ prediction (1.12)
   - Green solid line = Your measured mean

2. **Top Right - Z-score Distribution**:
   - Shows statistical significance for each galaxy
   - Red curve = Standard normal (ΛCDM expectation)
   - Orange/green lines = 2σ and 3σ thresholds

3. **Bottom Left - Ranked Significances**:
   - Each point is one galaxy, ranked by z-score
   - Colors indicate significance level
   - Shows consistency of effect across sample

4. **Bottom Right - Summary Text**:
   - Key statistics
   - Final verdict (SDH+ vs ΛCDM)
   - Confidence level

## Next Steps (If Confirmed)

If SDH+ is supported:
1. Analyze environmental dependence of a₀ (Component B)
2. Extract coupling running from power spectra (Component D)
3. Measure H₀(z) profile (Prediction 2)
4. Measure S₈ environmental split (Prediction 1)

If ΛCDM is supported:
1. Investigate why SDH+ RG-running is not detected
2. Refine ΛCDM feedback models
3. Move on to Prediction 1-3 to test other SDH+ mechanisms

## Questions?

Refer to:
- **Data issues**: Check SPARC website (https://data.astrochem.org/sparc/)
- **Code questions**: See inline comments in src/*.py
- **Scientific questions**: Review gann_orchestrated_challenge.md

---

**Last Updated**: 2026-02-07
**Status**: Ready for execution