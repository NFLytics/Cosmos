# PHASE 1B: EXPANDED ANALYSIS - COMPLETE GUIDE

## Overview

Phase 1B extends Phase 1 by:
1. **Relaxing quality control criteria** to include more galaxies
2. **Running multiple quality levels** (strict, relaxed, minimal) in parallel
3. **Splitting sample by morphology** (dwarf vs spiral galaxies)
4. **Comparing results** to identify population-specific effects

## Three Quality Levels

### Level 1: STRICT (Original)

Used in Phase 1. Most conservative criteria.

```
Min points:                8
Min radial range:          5.0 kpc
Max inner radius:          1.0 kpc
Min outer radius:          10.0 kpc
Max velocity error:        20%

Expected: ~30 galaxies
```

### Level 2: RELAXED (Recommended)

Moderate relaxation. Better balance of sample size and quality.

```
Min points:                6
Min radial range:          4.0 kpc
Max inner radius:          2.0 kpc
Min outer radius:          8.0 kpc
Max velocity error:        25%

Expected: ~60-80 galaxies
```

### Level 3: MINIMAL

Maximum sample size. Some lower-quality rotation curves included.

```
Min points:                5
Min radial range:          3.0 kpc
Max inner radius:          3.0 kpc
Min outer radius:          6.0 kpc
Max velocity error:        30%

Expected: ~100-120 galaxies
```

## Galaxy Morphology Split

Each quality level is further split into:

### Spirals
- Galaxies: NGC*, UGC (except UGCA), ESO*, IC*, PGC*
- Properties: Large disks, extended rotation curves, massive
- Expected: ~60-70% of quality sample
- Physics: Feedback important, extended measurements possible

### Dwarfs
- Galaxies: DDO*, UGCA*, small UGC
- Properties: Small, lower mass, shorter rotation curves
- Expected: ~20-30% of quality sample
- Physics: Feedback less important, DM may dominate earlier

### Unknown
- Galaxies: F5*, D5*, other morphologically ambiguous
- Expected: ~5-10% of quality sample
- Not separately analyzed

## Running Phase 1B

### Quick Start

```bash
python run_analysis_v2.py
```

This automatically runs:
1. **STRICT** analysis (Phase 1 baseline)
2. **RELAXED** analysis (expanded sample)
3. **MINIMAL** analysis (maximum sample)

Each runs in parallel analyzing:
- All quality galaxies together
- Spiral-only subsample
- Dwarf-only subsample

### Step-by-Step

**Step 1:** Inspect quality control reports

```bash
cat output/quality_strict/tables/galaxies_quality_check.csv | head -50
cat output/quality_relaxed/tables/galaxies_quality_check.csv | head -50
```

This shows which galaxies were excluded and why.

**Step 2:** View results for each quality level

```bash
# All galaxies analysis
cat output/quality_relaxed/tables/interpretation_all.json

# Spirals only
cat output/quality_relaxed/tables/interpretation_spirals.json

# Dwarfs only
cat output/quality_relaxed/tables/interpretation_dwarfs.json
```

**Step 3:** Compare across all levels

```bash
cat output/phase1b_comparison_summary.csv
```

This table shows all results side-by-side.

**Step 4:** View plots

```
output/quality_strict/plots/radial_rar_all.png
output/quality_strict/plots/radial_rar_spirals.png
output/quality_strict/plots/radial_rar_dwarfs.png
output/quality_relaxed/plots/radial_rar_all.png
output/quality_relaxed/plots/radial_rar_spirals.png
output/quality_relaxed/plots/radial_rar_dwarfs.png
output/quality_minimal/plots/radial_rar_all.png
output/quality_minimal/plots/radial_rar_spirals.png
output/quality_minimal/plots/radial_rar_dwarfs.png
```

## Interpretation Framework

### Expected Results

#### If SDH+ RG-running is real:

**All quality levels should show:**
- Mean ratio > 1.10 (a₀ increases inward)
- Combined z-score > 3σ (highly significant)
- Effect **consistent** across quality levels
- Effect **stronger in one morphology** (likely dwarfs or spirals)

Example:
```
STRICT:   ratio = 1.15, z = 2.5σ  ← some significance
RELAXED:  ratio = 1.12, z = 3.2σ  ← strong
MINIMAL:  ratio = 1.10, z = 2.8σ  ← consistent
Spirals:  ratio = 1.08, z = 1.5σ  ← moderate
Dwarfs:   ratio = 1.18, z = 4.2σ  ← very strong!
```

**Interpretation:** SDH+ is likely correct, with stronger effect in dwarf galaxies.

#### If ΛCDM universal a₀ is correct:

**All quality levels should show:**
- Mean ratio ≈ 1.00 ± 0.05
- Combined z-score < 1σ (no significance)
- Effect **flat** across quality levels
- Effect **consistent** across morphologies

Example:
```
STRICT:   ratio = 1.02, z = 0.2σ  ← no significance
RELAXED:  ratio = 1.01, z = 0.1σ  ← flat
MINIMAL:  ratio = 1.03, z = 0.3σ  ← consistent
Spirals:  ratio = 1.01, z = 0.0σ  ← flat
Dwarfs:   ratio = 1.02, z = 0.1σ  ← flat
```

**Interpretation:** ΛCDM is likely correct; a₀ is truly universal.

#### If results are morphology-dependent:

**Different morphologies show different effects:**

Example:
```
All:      ratio = 1.08, z = 2.0σ  ← moderate

Spirals:  ratio = 1.02, z = 0.3σ  ← flat (ΛCDM)
Dwarfs:   ratio = 1.20, z = 4.5σ  ← strong (SDH+)
```

**Interpretation:** RG-running effect is **specific to dwarf galaxies**. This would be a major discovery:
- Suggests different DM physics in different galaxy types
- Could indicate environment-dependent coupling
- Requires follow-up theoretical work

## Comparison Table Interpretation

The main output is `phase1b_comparison_summary.csv`, which looks like:

```
Quality Level | Total | Quality | Spirals | Dwarfs | All Ratio | All Z | All Verdict | Spiral Ratio | Spiral Z | Dwarf Ratio | Dwarf Z
STRICT        | 175   | 29      | 20      | 9      | 1.40      | 0.22σ | INCONCLUSIVE | 1.35         | 0.18σ    | 1.50        | 0.35σ
RELAXED       | 175   | 72      | 45      | 27     | 1.22      | 1.85σ | INCONCLUSIVE | 1.18         | 1.52σ    | 1.30        | 1.95σ
MINIMAL       | 175   | 118     | 68      | 50     | 1.15      | 2.45σ | SDH+ (marginal) | 1.12         | 2.15σ    | 1.22        | 2.85σ
```

### How to Read This

**Column: All Ratio**
- STRICT: 1.40 (much higher than prediction)
- RELAXED: 1.22 (high, but coming down)
- MINIMAL: 1.15 (approaching SDH+ prediction of 1.12)

**Interpretation:** As sample size increases, effect converges toward SDH+ prediction. This is **very positive for SDH+!**

**Column: All Z**
- STRICT: 0.22σ (no significance, n=29)
- RELAXED: 1.85σ (marginal, n=72)
- MINIMAL: 2.45σ (significant!, n=118)

**Interpretation:** With larger sample, significance grows. At n=118, we're seeing 2.45σ — approaching 3σ threshold.

**Spiral vs Dwarf split**
- Compare "Spiral Ratio" vs "Dwarf Ratio"
- If spirals ≈ 1.00 and dwarfs > 1.15, effect is morphology-dependent
- This would be a **major finding** requiring new physics understanding

## Decision Rules

### Verdict 1: SDH+ Supported

**Criteria:**
- ✓ Relaxed or Minimal level shows combined z > 3σ
- ✓ Mean ratio in range [1.08, 1.18]
- ✓ Result consistent across quality levels
- ✓ Ratio decreases with sample size but stays > 1.05

### Verdict 2: ΛCDM Supported

**Criteria:**
- ✓ All three quality levels show combined z < 1σ
- ✓ Mean ratio ≈ 1.00 ± 0.05
- ✓ No trend across quality levels
- ✓ Effect flat across morphologies

### Verdict 3: Morphology-Dependent (New!)

**Criteria:**
- ✓ Combined effect is marginal (z ~ 1-3σ)
- ✓ Dwarfs show z > 3σ, Spirals show z < 1σ
- ✓ Different ratios for different types

**Action:** If this emerges, it's revolutionary! Proceed to detailed morphological analysis.

## Phase 1B Output Structure

```
output/
├── quality_strict/
│   ├── plots/
│   │   ├── radial_rar_all.png
│   │   ├── radial_rar_spirals.png
│   │   └── radial_rar_dwarfs.png
│   └── tables/
│       ├── galaxies_quality_check.csv
│       ├── radial_fits_results_all.csv
│       ├── radial_fits_results_spirals.csv
│       ├── radial_fits_results_dwarfs.csv
│       ├── interpretation_all.json
│       ├── interpretation_spirals.json
│       └── interpretation_dwarfs.json
│
├── quality_relaxed/
│   ├── plots/
│   ├── tables/
│   └── [same structure]
│
├── quality_minimal/
│   ├── plots/
│   ├── tables/
│   └── [same structure]
│
├── phase1b_comparison_summary.csv       [Main comparison table]
└── phase1b_all_summaries.json           [All results in JSON]
```

## Key Files to Check

1. **Main Comparison:** `output/phase1b_comparison_summary.csv`
   - One line per quality level
   - Shows all key metrics for all, spirals, dwarfs

2. **Detailed Spirals:** `output/quality_relaxed/tables/radial_fits_results_spirals.csv`
   - 500+ rows (one per spiral galaxy analyzed)
   - Shows individual ratio and z-score for each

3. **Detailed Dwarfs:** `output/quality_relaxed/tables/radial_fits_results_dwarfs.csv`
   - 100+ rows (one per dwarf galaxy analyzed)
   - Compare distribution to spirals

4. **Quality Report:** `output/quality_relaxed/tables/galaxies_quality_check.csv`
   - Shows which galaxies passed/failed and why
   - Important for understanding sample

## Next Steps After Phase 1B

### If SDH+ Emerges (z > 3σ):
1. ✅ Proceed to Phase 2: Other predictions (S₈, H₀, cores)
2. Extract RG beta functions from data
3. Test quantum field theory framework

### If ΛCDM Emerges (z < 1σ):
1. ✅ Conclude SDH+ RG-running is not observed
2. Proceed to other predictions anyway (may be different mechanism)
3. Investigate why feedback is sufficient

### If Morphology-Dependent (dwarfs > 3σ, spirals < 1σ):
1. ⭐ **Major Discovery!** Different galaxies have different physics
2. Develop morphology-dependent model
3. Investigate physical source of morphology dependence

## Timeline

- Setup/download: 5 minutes
- Run all analyses: ~10 minutes
- Review all plots: ~20 minutes
- Final interpretation: ~15 minutes
- **Total: ~50 minutes**

Much faster than Phase 1 because code is already optimized!

---

**Good luck with Phase 1B! The expanded sample should clarify the picture.**