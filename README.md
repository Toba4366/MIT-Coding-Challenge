# MIT Coding Challenge: Monetary Policy Shocks and Exchange Rates

## Overview

This repository contains my solutions to the MIT Coding Challenge, analyzing the transmission of U.S. monetary policy surprises to exchange rates and testing whether external balance sheets (NFA/GDP) mediate this transmission.

**Key Finding:** Within a daily-frequency framework using 8 major currencies, we do not find statistically robust evidence that NFA/GDP systematically mediates FX responses to U.S. monetary surprises—neither unconditionally, post-GFC, nor during stress episodes.

---

## Writeup Documents

| Document | Description |
|----------|-------------|
| [`Output/writeup.pdf`](Output/writeup.pdf) | **Main submission** (~5 pages text + tables/figures) |
| [`Output/writeup_v2.pdf`](Output/writeup_v2.pdf) | Extended version with additional robustness checks |

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
│   ├── daily-treasury-rates*.csv # Treasury yield data (2024-2026)
│   └── par-yield-curve-rates*.csv # Historical par yield curves
│
├── Output/                       # Generated outputs (see detailed list below)
│   ├── writeup.pdf              # Main submission document
│   ├── writeup_v2.pdf           # Extended version
│   ├── table1–8*.tex            # LaTeX tables
│   ├── figure1–16*.png          # All figures
│   ├── merged_fomc_data.csv     # Master merged dataset
│   └── task*_*.csv              # Intermediate results
│
└── scripts/                      # All Python analysis scripts
    ├── task1_data_preparation.py  # Merge MPS, FX, yields, NFA
    ├── task1_visualizations.py    # Summary stat figures (fig 1-6)
    ├── task2_regressions.py       # Event-study regressions (fig 7-9)
    ├── task2_placebo.py           # Placebo test with lead surprises
    ├── task3_panel_regression.py  # NFA × surprise panel (fig 10-12)
    ├── task4_time_variation.py    # Post-GFC regime (fig 13-14)
    ├── task4b_vix_stress.py       # VIX stress interaction (fig 15-16)
    └── check_*.py, analyze_*.py   # Validation & diagnostics
```

---

## Task Summary

### Task 1: Data Preparation
- Merged Bauer-Swanson monetary policy surprises (STMT, MP1, MP2) with daily FX log-changes and Treasury yield changes
- Sample: 274 FOMC announcements (1994–2024), 8 major currencies (AUD, CAD, CHF, EUR, GBP, JPY, MXN, NOK)
- Output: `merged_fomc_data.csv`, summary statistics

### Task 2: Event-Study Regressions
- Regressed daily FX changes and yield changes on monetary policy surprises
- Key result: STMT strongly predicts 2Y/5Y/10Y Treasury yield changes (t > 5)
- FX responses are noisy but directionally consistent (hawkish → USD appreciation)

### Task 3: Panel Regression with NFA Interaction
- Specification: `r_{i,t} = α_i + β₁·Surprise + β₂·(Surprise × NFA) + ε`
- FX convention: Spot return `r = −Δlog(e)`, positive = foreign appreciation
- Result: β₂ ≈ −0.005 (p = 0.48), opposite to Bruno-Shin prediction
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
| **Spot return convention** | `r = −Δlog(e)` so positive = foreign appreciation |
| **Demeaned NFA** | Β₁ interpretable as effect at mean NFA |
| **Entity fixed effects** | Control for currency-specific level differences |

---

## Output Files

### Tables (LaTeX)

| File | Description |
|------|-------------|
| `table1_summary_stats.tex` | Summary statistics: MP surprises (STMT, MP1), NFA/GDP by country |
| `table2_regression_results.tex` | Panel A: Treasury yield responses; Panel B: Breakeven inflation; Panel C: FX spot returns |
| `table2a_nfa_by_country.tex` | NFA/GDP values by country (creditor/debtor classification) |
| `table2b_treasury_response.tex` | Treasury yield responses to STMT (2Y, 5Y, 10Y maturities) |
| `table2c_fx_response.tex` | Currency-by-currency FX responses to monetary surprises |
| `table3_nfa_panel.tex` | Panel regression: Surprise × NFA interaction with clustering variants |
| `table4_time_variation.tex` | Post-GFC triple interaction (Surprise × NFA × Post2008) |
| `table5_vix_stress.tex` | VIX stress triple interaction (Surprise × NFA × HighVIX) |
| `table8_placebo.tex` | Placebo test: Non-FOMC date regressions |

### Intermediate Data (CSV)

| File | Description |
|------|-------------|
| `merged_fomc_data.csv` | Master dataset: FOMC dates with surprises, FX returns, yields, NFA |
| `summary_statistics.csv` | Computed summary stats for all variables |
| `task2_regression_results.csv` | Event-study coefficients (all assets) |
| `task2_country_betas.csv` | Currency-specific β estimates (STMT) |
| `task2_country_betas_mp1.csv` | Currency-specific β estimates (MP1) |
| `task3_panel_data.csv` | Panel-formatted data for NFA regressions |
| `task3_nfa_panel_results.csv` | Panel regression coefficient estimates |
| `task3_marginal_effects.csv` | Marginal effects across NFA distribution |
| `task4_time_variation_results.csv` | Post-GFC regime coefficient estimates |
| `task4b_vix_stress_results.csv` | VIX stress interaction estimates |
| `placebo_results.csv` | Placebo test results |

### Figures (PNG)

| File | Description |
|------|-------------|
| `figure1_surprise_timeseries.png` | Time series of STMT and MP1 surprises (1994–2024) |
| `figure2_correlation_heatmap.png` | Correlation matrix across all surprise measures |
| `figure3_surprise_distributions.png` | Histograms of STMT and MP1 distributions |
| `figure4_stmt_validation.png` | Scatter: STMT vs. 2Y Treasury yield change |
| `figure5_event_scatter.png` | Event scatter plots for key announcements |
| `figure6_volatility_by_period.png` | Surprise volatility by decade |
| `figure7_term_structure.png` | Term structure of yield responses (2Y→10Y) |
| `figure8_fx_heterogeneity.png` | Cross-currency FX response heterogeneity |
| `figure9_coefficient_plot.png` | Coefficient plot with 95% CIs (all currencies) |
| `figure10_betas_vs_nfa.png` | Scatter: Currency β vs. NFA/GDP (STMT) |
| `figure10b_betas_vs_nfa_both.png` | Scatter: Currency β vs. NFA/GDP (STMT + MP1) |
| `figure11_marginal_effects.png` | Marginal effect of surprise across NFA distribution |
| `figure12_predicted_responses.png` | Predicted FX responses by NFA decile |
| `figure13_time_variation.png` | Pre- vs. Post-GFC coefficient comparison |
| `figure14_coefficient_comparison.png` | NFA interaction coefficient: pre vs. post 2008 |
| `figure15_vix_stress.png` | VIX time series with stress episodes highlighted |
| `figure16_vix_coefficient_comparison.png` | NFA interaction: normal vs. high-VIX regimes |

### Writeup Documents (PDF)

| File | Description |
|------|-------------|
| `writeup.pdf` | **Main submission** (~5 pages text + tables/figures at end) |
| `writeup_v2.pdf` | Extended version (27 pages) with additional robustness checks |

---

## Narrative Arc

1. **3.1:** STMT is a valid monetary policy shock measure (strong yield transmission)
2. **3.2:** FX responses to U.S. monetary shocks are heterogeneous across G10
3. **3.3:** NFA/GDP does **not** explain this heterogeneity (β₂ ≈ 0, wrong sign)
4. **3.4:** No robust post-GFC amplification (STMT sign flip suggestive but imprecise)
5. **3.4b:** No stress-state amplification (VIX interaction insignificant)

**Conclusion:** Within a daily-frequency framework using major currencies, we do not find statistically robust evidence that NFA/GDP systematically mediates FX responses to U.S. monetary surprises. This null is disciplined and informative—developed-market currencies may not exhibit the balance-sheet sensitivity theorized for emerging markets with higher dollar debt exposure.

---

## References

- Acosta, M., Ajello, A., Bauer, M., Loria, F., & Miranda-Agrippino, S. (2025). Financial Market Effects of FOMC Communication: Evidence from a New Event-Study Database. FRB San Francisco Working Paper 2025-30.
- Antol´ın-D´ıaz, J., Cenedese, G., Han, S., & Sarno, L. (2023). U.S. Interest Rate Surprises and Currency Returns. SSRN Working Paper
- Bauer, M. D., & Swanson, E. T. (2022). "A Reassessment of Monetary Policy Surprises and High-Frequency Identification." *NBER Macroeconomics Annual*, 37.
- Bruno, V., & Shin, H. S. (2015). "Cross-border Banking and Global Liquidity." *Review of Economic Studies*, 82(2), 535–564.
- Lane, P. R., & Milesi-Ferretti, G. M. (2018). "The External Wealth of Nations Revisited." *IMF Economic Review*, 66(1), 189–222.
- Petersen, M. A. (2009). "Estimating Standard Errors in Finance Panel Data Sets." *Review of Financial Studies*, 22(1), 435–480.

---

## Author

Trenton Eugene O'Bannon  
MIT Coding Challenge Submission
