# QUICK START GUIDE

## TL;DR - Get Results in 5 Minutes

### 1. Organize Files

Put SPARC files in:
```
data/raw_sparc/
├── Table1.mrt
├── Table2.mrt
└── sparc_mass_models/
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Analysis

**Windows:**
```bash
run_analysis.bat
```

**Mac/Linux:**
```bash
python run_analysis.py
```

### 4. View Results

Check these files:
- **Results**: `output/tables/radial_fits_results.csv`
- **Verdict**: `output/tables/interpretation.json`
- **Plot**: `output/plots/radial_rar_analysis.png`

---

## What Does It Do?

1. **Loads SPARC data** (175 galaxies, 2693 rotation curve points)
2. **Fits RAR formula** separately to inner and outer regions
3. **Compares a₀ values**: Does inner differ from outer?
   - If YES → Supports SDH+ (quantum RG running)
   - If NO → Supports ΛCDM (universal a₀)
4. **Generates plots and statistics**

---

## Key Output Metrics

**If SDH+ wins:**
- Ratio > 1.05 (a₀ is 5%+ larger inside)
- Combined z-score > 2σ

**If ΛCDM wins:**
- Ratio ≈ 1.00 (a₀ is universal)
- Combined z-score < 1σ

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| FileNotFoundError: Table1.mrt | Put SPARC files in `data/raw_sparc/` |
| ImportError: No module named pandas | Run `pip install -r requirements.txt` |
| Only X quality galaxies | Check `output/tables/galaxies_quality_check.csv` |
| Plots not showing | Ensure `output/plots/` exists |

---

## File Locations

```
Your Project Root/
├── data/raw_sparc/          ← PUT SPARC FILES HERE
├── src/                     ← Python scripts
├── config/                  ← Configuration
├── output/                  ← Results (auto-created)
├── run_analysis.py          ← MAIN SCRIPT
├── run_analysis.bat         ← Windows batch file
└── requirements.txt         ← Dependencies
```

---

## Expected Runtime

- **Loading data**: ~5-10 seconds
- **Quality control**: ~5 seconds
- **Fitting**: ~30-60 seconds (depends on CPU)
- **Statistics & plots**: ~10 seconds
- **Total**: ~2 minutes

---

## Results Summary

After running, you'll get:

```
VERDICT: SDH+ or ΛCDM
Confidence: HIGH or LOW

Evidence:
- Mean ratio a₀(in)/a₀(out): X.XXXX ± X.XXXX
- Combined significance: X.XXσ
- Interpretation: [Detailed explanation]
```

---

## Next Steps

**If SDH+ confirmed**: Proceed to other predictions (S₈, H₀, core slopes)
**If ΛCDM confirmed**: Refine feedback models, investigate other mechanisms

---

Need help? See `SETUP_AND_RUN.md` or code comments.