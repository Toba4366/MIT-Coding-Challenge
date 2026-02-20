# MIT Coding Challenge: Monetary Policy Shocks and Exchange Rates

## Overview

This repository contains my solutions to the MIT Coding Challenge, analyzing the transmission of U.S. monetary policy surprises to exchange rates and testing whether external balance sheets (NFA/GDP) mediate this transmission.

**Key Finding:** Within a G10 daily-frequency framework, we do not find statistically robust evidence that NFA/GDP systematically mediates FX responses to U.S. monetary surprises—neither unconditionally, post-GFC, nor during stress episodes.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run All Analyses

```bash
python run_all.py
```

This executes all scripts from start to finish without manual intervention, generating all tables and figures in the `Output/` directory.

---

## Repository Structure

```
MIT Coding Challenge/
├── run_all.py                    # Master script — runs everything
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── Data/                         # Input data
│   ├── monetary-policy-surprises/
│   │   ├── mps.csv              # Bauer-Swanson monetary policy surprises
│   │   └── README.md            # Data documentation
│   ├── daily-treasury-rates*.csv # Treasury yield data
│   └── par-yield-curve-rates*.csv
│
├── Output/                       # Generated outputs
│   ├── table1_summary_stats.tex  # Summary statistics (LaTeX)
│   ├── table2_regression_results.tex  # Event-study regressions
│   ├── table3_panel_regression.tex    # NFA interaction panel
│   ├── table4_time_variation.tex      # Post-GFC analysis
│   ├── table5_vix_stress.tex          # VIX stress analysis
│   ├── figure1–16*.png               # All figures
│   └── *.csv                          # Intermediate data files
│
└── Scripts (executed by run_all.py):
    ├── task1_data_preparation.py  # Merge MPS, FX, yields
    ├── task1_visualizations.py    # Summary stat figures
    ├── task2_regressions.py       # Event-study regressions
    ├── task3_panel_regression.py  # NFA × surprise interaction
    ├── task4_time_variation.py    # Post-GFC regime analysis
    ├── task4b_vix_stress.py       # VIX stress interaction
    └── check_*.py, analyze_*.py   # Validation & diagnostics
```

---

## Task Summary

### Task 1: Data Preparation
- Merged Bauer-Swanson monetary policy surprises (STMT, MP1, MP2) with daily FX log-changes and Treasury yield changes
- Sample: 269 FOMC announcements (1994–2025), 8 G10 currencies
- Output: `merged_fomc_data.csv`, summary statistics

### Task 2: Event-Study Regressions
- Regressed daily FX changes and yield changes on monetary policy surprises
- Key result: STMT strongly predicts 2Y/5Y/10Y Treasury yield changes (t > 5)
- FX responses are noisy but directionally consistent (hawkish → USD appreciation)

### Task 3: Panel Regression with NFA Interaction
- Specification: `r_{i,t} = α_i + β₁·Surprise + β₂·(Surprise × NFA) + ε`
- FX convention: Spot return `r = −Δlog(e)`, positive = foreign appreciation
- Result: β₂ ≈ −0.005 (p = 0.48), opposite to Antolín-Díaz et al. (2023) prediction
- NFA/GDP does not robustly explain cross-currency heterogeneity

### Task 4: Time Variation
- **4a (Post-GFC):** Triple interaction `Surprise × NFA × Post2008`
  - STMT: β₃ = 0.022 (p = 0.154) — suggestive sign flip, imprecise
  - MP1: β₃ ≈ 0 (p = 0.947) — no time variation
- **4b (VIX Stress):** Triple interaction `Surprise × NFA × HighVIX`
  - STMT: β₃ = −0.019 (p = 0.199) — no stress amplification
  - MP1: β₃ = −0.010 (p = 0.653) — no stress amplification

---

## Key Methodological Choices

| Choice | Rationale |
|--------|-----------|
| **Date clustering** | Monetary shocks are common across currencies on FOMC dates (Petersen 2009) |
| **Spot return convention** | `r = −Δlog(e)` so positive = foreign appreciation, matching Antolín-Díaz |
| **Demeaned NFA** | Β₁ interpretable as effect at mean NFA |
| **Entity fixed effects** | Control for currency-specific level differences |

---

## Output Files

### Tables (LaTeX)
| File | Description |
|------|-------------|
| `table1_summary_stats.tex` | Summary statistics for all variables |
| `table2_regression_results.tex` | Event-study regression coefficients |
| `table3_panel_regression.tex` | NFA × Surprise panel regression |
| `table4_time_variation.tex` | Post-GFC regime analysis |
| `table5_vix_stress.tex` | VIX stress interaction |

### Figures (PNG)
| File | Description |
|------|-------------|
| `figure1–9` | Task 1–2 visualizations |
| `figure10–12` | Task 3 NFA interaction plots |
| `figure13–14` | Task 4a time variation plots |
| `figure15–16` | Task 4b VIX stress plots |

---

## Narrative Arc

1. **3.1:** STMT is a valid monetary policy shock measure (strong yield transmission)
2. **3.2:** FX responses to U.S. monetary shocks are heterogeneous across G10
3. **3.3:** NFA/GDP does **not** explain this heterogeneity (β₂ ≈ 0, wrong sign)
4. **3.4:** No robust post-GFC amplification (STMT sign flip suggestive but imprecise)
5. **3.4b:** No stress-state amplification (VIX interaction insignificant)

**Conclusion:** Within a G10 daily-frequency framework, we do not find statistically robust evidence that NFA/GDP systematically mediates FX responses to U.S. monetary surprises. This null is disciplined and informative—G10 currencies may not exhibit the balance-sheet sensitivity theorized for emerging markets with higher dollar debt exposure.

---

## References

- Antolín-Díaz, J., Drechsel, T., & Petrella, I. (2023). "Advances in Nowcasting Economic Activity"
- Bauer, M. D., & Swanson, E. T. (2023). "A Reassessment of Monetary Policy Surprises and High-Frequency Identification"
- Bruno, V., & Shin, H. S. (2015). "Cross-border Banking and Global Liquidity"
- Lane, P. R., & Milesi-Ferretti, G. M. (2018). "The External Wealth of Nations Revisited"
- Petersen, M. A. (2009). "Estimating Standard Errors in Finance Panel Data Sets"
- Rey, H. (2015). "Dilemma not Trilemma: The Global Financial Cycle and Monetary Policy Independence"

---

## Author

Trenton O'Bannon  
MIT Coding Challenge Submission
