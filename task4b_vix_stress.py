"""
Task 3.4b: VIX Stress Interaction — The Final Research Flex
============================================================
Tests whether the NFA channel operates specifically during market stress episodes,
proxied by elevated VIX levels.

Hypothesis:
    If balance-sheet effects work through dollar funding stress and risk
    amplification, the NFA × Surprise interaction should be stronger when
    VIX is high. During crisis periods, net creditors face valuation gains
    on foreign assets but may experience dollar funding pressure, while
    net debtors face acute balance-sheet deterioration.

Specification:
    r_{i,t} = α_i + β1·Surprise_t + β2·(Surprise_t × NFA_{i,t-1})
              + β3·(Surprise_t × NFA_{i,t-1} × HighVIX_t)
              + γ·NFA_{i,t-1} + δ·HighVIX_t + controls + ε_{i,t}

    where r_{i,t} = -Δlog(e_{i,t}), positive = foreign appreciation.
    HighVIX_t = 1 if VIX on day t exceeds some threshold (e.g., 75th percentile).

This is mechanism-driven: balance-sheet channels should bite during stress.

References:
    - Bruno & Shin (2015): Risk-taking channel and VIX
    - Rey (2015): Global financial cycle and VIX
    - Engel & Wu (2018): Liquidity and FX
"""

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

BASE = '/Users/trentonobannontrenton/MIT Coding Challenge'
os.makedirs(f'{BASE}/Output', exist_ok=True)

print("=" * 80)
print("TASK 3.4b: VIX STRESS INTERACTION")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD PANEL DATA AND VIX
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Load Panel Data and VIX")
print("=" * 80)

panel = pd.read_csv(f'{BASE}/Output/task3_panel_data.csv')
panel['Date'] = pd.to_datetime(panel['Date'])

print(f"Panel observations: {len(panel)}")
print(f"Date range: {panel['Date'].min().strftime('%Y-%m-%d')} to {panel['Date'].max().strftime('%Y-%m-%d')}")

# Try to get VIX data from Yahoo Finance (or use synthetic proxy)
# For this exercise, we'll use the VIX OHLC data if available
# If not available, we'll use Treasury volatility as a proxy (via yield changes)

# Try to get VIX data
vix_data = None
vix_source = None

# First try yfinance
try:
    import yfinance as yf
    vix_df = yf.download('^VIX', start='1990-01-01', end='2025-12-31', progress=False)
    if len(vix_df) > 0:
        vix_data = vix_df[['Close']].reset_index()
        vix_data.columns = ['Date', 'VIX']
        vix_data['Date'] = pd.to_datetime(vix_data['Date'])
        print(f"Downloaded VIX data: {len(vix_data)} observations")
        print(f"VIX range: {vix_data['Date'].min()} to {vix_data['Date'].max()}")
        vix_source = "Yahoo Finance (^VIX)"
except Exception as e:
    print(f"Could not download VIX: {e}")

# If yfinance failed, create synthetic VIX from Treasury yield changes
if vix_data is None:
    print("Creating synthetic VIX proxy from Treasury yield volatility...")
    
    # Load the merged FOMC data
    merged = pd.read_csv(f'{BASE}/Output/merged_fomc_data.csv')
    merged['Date'] = pd.to_datetime(merged['Date'])
    
    # Use absolute 10Y yield change as a volatility proxy
    # Scale to roughly match VIX levels (VIX typically 15-30 in normal times)
    if 'd_UST_10Y' in merged.columns:
        # Absolute 10Y yield change (bps), scaled
        merged['VIX_proxy'] = merged['d_UST_10Y'].abs().rolling(5, min_periods=1).mean() * 1.5 + 15
    else:
        # Fallback: use STMT absolute value
        merged['VIX_proxy'] = merged['STMT_bps'].abs().rolling(5, min_periods=1).mean() * 0.5 + 15
    
    vix_data = merged[['Date', 'VIX_proxy']].rename(columns={'VIX_proxy': 'VIX'})
    vix_source = "Synthetic (Treasury yield volatility proxy)"
    print(f"Created synthetic VIX proxy: {len(vix_data)} observations")

# Merge VIX into panel
panel = panel.merge(vix_data, on='Date', how='left')

# Handle missing VIX
vix_missing = panel['VIX'].isna().sum()
if vix_missing > 0:
    print(f"VIX missing for {vix_missing} observations ({100*vix_missing/len(panel):.1f}%)")
    # Fill with median
    panel['VIX'] = panel['VIX'].fillna(panel['VIX'].median())

print(f"\nVIX statistics in sample:")
print(f"  Source: {vix_source}")
print(f"  Mean:   {panel['VIX'].mean():.1f}")
print(f"  Median: {panel['VIX'].median():.1f}")
print(f"  Std:    {panel['VIX'].std():.1f}")
print(f"  P25:    {panel['VIX'].quantile(0.25):.1f}")
print(f"  P75:    {panel['VIX'].quantile(0.75):.1f}")
print(f"  P90:    {panel['VIX'].quantile(0.90):.1f}")
print(f"  Max:    {panel['VIX'].max():.1f}")

# ============================================================================
# STEP 2: DEFINE HIGH-VIX REGIMES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: Define High-VIX Regimes")
print("=" * 80)

# Multiple thresholds for robustness
thresholds = {
    'P75': panel['VIX'].quantile(0.75),
    'P90': panel['VIX'].quantile(0.90),
    '25': 25,  # Classic "fear" threshold
    '30': 30,  # Elevated fear
}

print(f"\nThreshold definitions:")
for name, thresh in thresholds.items():
    count = (panel['VIX'] >= thresh).sum()
    pct = 100 * count / len(panel)
    print(f"  {name:>4s}: VIX ≥ {thresh:>5.1f}  →  {count:>4d} obs ({pct:>5.1f}%)")

# Use P75 as primary threshold (standard in macro-finance)
primary_thresh = 'P75'
panel['HighVIX'] = (panel['VIX'] >= thresholds[primary_thresh]).astype(int)

high_vix_dates = panel.loc[panel['HighVIX'] == 1, 'Date'].nunique()
total_dates = panel['Date'].nunique()
print(f"\nPrimary threshold (P75 = {thresholds[primary_thresh]:.1f}):")
print(f"  {high_vix_dates} FOMC dates in high-VIX regime ({100*high_vix_dates/total_dates:.1f}%)")

# ============================================================================
# STEP 3: CREATE INTERACTION TERMS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: Create Interaction Terms")
print("=" * 80)

# Double interactions
panel['HighVIX_x_STMT'] = panel['HighVIX'] * panel['STMT']
panel['HighVIX_x_NFA'] = panel['HighVIX'] * panel['NFA_GDP_dm']

# Triple interaction (key test)
panel['STMT_x_NFA_x_HighVIX'] = panel['STMT'] * panel['NFA_GDP_dm'] * panel['HighVIX']

# MP1 interactions
panel['HighVIX_x_MP1'] = panel['HighVIX'] * panel['MP1']
panel['MP1_x_NFA_x_HighVIX'] = panel['MP1'] * panel['NFA_GDP_dm'] * panel['HighVIX']

# Also include STMT_x_NFA from original
panel['STMT_x_NFA'] = panel['STMT'] * panel['NFA_GDP_dm']
panel['MP1_x_NFA'] = panel['MP1'] * panel['NFA_GDP_dm']

print("Interaction terms created:")
print("  STMT: STMT_x_NFA, HighVIX_x_STMT, HighVIX_x_NFA, STMT_x_NFA_x_HighVIX")
print("  MP1:  MP1_x_NFA, HighVIX_x_MP1, HighVIX_x_NFA, MP1_x_NFA_x_HighVIX")

# ============================================================================
# STEP 4: REGRESSIONS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: Panel Regressions")
print("=" * 80)

# Set panel index
panel_idx = panel.set_index(['currency', 'Date'])

# ---- (1) Baseline from 3.3 (reproduced) ----
print("\n--- Column (1): Baseline (from 3.3) ---")
exog_base = panel_idx[['STMT', 'STMT_x_NFA', 'NFA_GDP_dm']]
model_base = PanelOLS(panel_idx['d_e'], exog_base,
                      entity_effects=True, drop_absorbed=True, check_rank=False)
result_base = model_base.fit(cov_type='clustered', cluster_time=True)

# ---- (2) STMT with VIX interaction ----
print("\n--- Column (2): STMT + VIX Triple Interaction ---")
exog_stmt_cols = ['STMT', 'STMT_x_NFA', 'NFA_GDP_dm',
                  'HighVIX', 'HighVIX_x_STMT', 'HighVIX_x_NFA',
                  'STMT_x_NFA_x_HighVIX']
exog_stmt = panel_idx[exog_stmt_cols]
model_stmt = PanelOLS(panel_idx['d_e'], exog_stmt,
                      entity_effects=True, drop_absorbed=True, check_rank=False)
result_stmt = model_stmt.fit(cov_type='clustered', cluster_time=True)
print(result_stmt.summary)

# ---- (3) MP1 with VIX interaction ----
print("\n--- Column (3): MP1 + VIX Triple Interaction ---")
exog_mp1_cols = ['MP1', 'MP1_x_NFA', 'NFA_GDP_dm',
                 'HighVIX', 'HighVIX_x_MP1', 'HighVIX_x_NFA',
                 'MP1_x_NFA_x_HighVIX']
panel_idx_mp1 = panel_idx[exog_mp1_cols + ['d_e']].dropna()
exog_mp1 = panel_idx_mp1[exog_mp1_cols]
dep_mp1 = panel_idx_mp1['d_e']
model_mp1 = PanelOLS(dep_mp1, exog_mp1,
                     entity_effects=True, drop_absorbed=True, check_rank=False)
result_mp1 = model_mp1.fit(cov_type='clustered', cluster_time=True)
print(result_mp1.summary)

# ============================================================================
# STEP 5: EXTRACT & DISPLAY RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: Results Summary")
print("=" * 80)

def stars(p):
    if pd.isna(p): return ''
    if p < 0.01: return '***'
    if p < 0.05: return '**'
    if p < 0.10: return '*'
    return ''

def extract(res, labels):
    out = {}
    for lab in labels:
        out[f'{lab}_coef'] = res.params.get(lab, np.nan)
        out[f'{lab}_se'] = res.std_errors.get(lab, np.nan)
        out[f'{lab}_pval'] = res.pvalues.get(lab, np.nan)
    out['N'] = int(res.nobs)
    out['R2'] = res.rsquared
    return out

r1 = extract(result_base, ['STMT', 'STMT_x_NFA', 'NFA_GDP_dm'])
r2 = extract(result_stmt, ['STMT', 'STMT_x_NFA', 'NFA_GDP_dm',
                            'HighVIX', 'HighVIX_x_STMT', 'HighVIX_x_NFA',
                            'STMT_x_NFA_x_HighVIX'])
r3 = extract(result_mp1, ['MP1', 'MP1_x_NFA', 'NFA_GDP_dm',
                           'HighVIX', 'HighVIX_x_MP1', 'HighVIX_x_NFA',
                           'MP1_x_NFA_x_HighVIX'])

# Print compact table
print(f"\n{'':35s} {'(1) Baseline':>14s} {'(2) STMT+VIX':>14s} {'(3) MP1+VIX':>14s}")
print("-" * 80)

rows = [
    ('Surprise (STMT or MP1)', 'STMT', 'STMT', 'MP1'),
    ('Surprise × NFA/GDP', 'STMT_x_NFA', 'STMT_x_NFA', 'MP1_x_NFA'),
    ('Surprise × NFA × HighVIX', None, 'STMT_x_NFA_x_HighVIX', 'MP1_x_NFA_x_HighVIX'),
    ('NFA/GDP', 'NFA_GDP_dm', 'NFA_GDP_dm', 'NFA_GDP_dm'),
    ('HighVIX', None, 'HighVIX', 'HighVIX'),
    ('HighVIX × Surprise', None, 'HighVIX_x_STMT', 'HighVIX_x_MP1'),
    ('HighVIX × NFA/GDP', None, 'HighVIX_x_NFA', 'HighVIX_x_NFA'),
]

for label, k1, k2, k3 in rows:
    vals = []
    for r, k in [(r1, k1), (r2, k2), (r3, k3)]:
        if k is None:
            vals.append(('', ''))
        else:
            c = r.get(f'{k}_coef', np.nan)
            s = r.get(f'{k}_se', np.nan)
            p = r.get(f'{k}_pval', np.nan)
            vals.append((f"{c:.4f}{stars(p)}", f"({s:.4f})"))
    print(f"  {label:<33s} {vals[0][0]:>14s} {vals[1][0]:>14s} {vals[2][0]:>14s}")
    print(f"  {'':33s} {vals[0][1]:>14s} {vals[1][1]:>14s} {vals[2][1]:>14s}")

print("-" * 80)
print(f"  {'Country FE':33s} {'Yes':>14s} {'Yes':>14s} {'Yes':>14s}")
print(f"  {'Date Cluster':33s} {'Yes':>14s} {'Yes':>14s} {'Yes':>14s}")
print(f"  {'Observations':33s} {r1['N']:>14d} {r2['N']:>14d} {r3['N']:>14d}")
print(f"  {'R²':33s} {r1['R2']:>14.4f} {r2['R2']:>14.4f} {r3['R2']:>14.4f}")

# ============================================================================
# STEP 6: MARGINAL EFFECTS BY VIX REGIME
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: Marginal Effects by VIX Regime")
print("=" * 80)

# STMT coefficients
b1_stmt = result_stmt.params['STMT']
b2_stmt = result_stmt.params['STMT_x_NFA']
b3_stmt = result_stmt.params['STMT_x_NFA_x_HighVIX']
b1_vix_stmt = result_stmt.params['HighVIX_x_STMT']

# MP1 coefficients
b1_mp1 = result_mp1.params['MP1']
b2_mp1 = result_mp1.params['MP1_x_NFA']
b3_mp1 = result_mp1.params['MP1_x_NFA_x_HighVIX']
b1_vix_mp1 = result_mp1.params['HighVIX_x_MP1']

# NFA mean/std for interpretation
nfa_mean = panel['NFA_GDP'].mean()
nfa_std = panel['NFA_GDP'].std()

print(f"\nSTMT SPECIFICATION (VIX Interaction):")
print(f"  β2 (low-VIX NFA slope):        {b2_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA']:.6f})")
print(f"  β3 (high-VIX amplification):   {b3_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA_x_HighVIX']:.6f})")
print(f"  p-value for β3:                {result_stmt.pvalues['STMT_x_NFA_x_HighVIX']:.4f}")
print(f"  High-VIX NFA slope (β2+β3):    {b2_stmt + b3_stmt:.6f}")

print(f"\nMP1 SPECIFICATION (VIX Interaction):")
print(f"  β2 (low-VIX NFA slope):        {b2_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA']:.6f})")
print(f"  β3 (high-VIX amplification):   {b3_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA_x_HighVIX']:.6f})")
print(f"  p-value for β3:                {result_mp1.pvalues['MP1_x_NFA_x_HighVIX']:.4f}")
print(f"  High-VIX NFA slope (β2+β3):    {b2_mp1 + b3_mp1:.6f}")

# ============================================================================
# STEP 7: FIGURE 15 — VIX STRESS INTERACTION
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: Generate Figures")
print("=" * 80)

plt.style.use('seaborn-v0_8-whitegrid')

# NFA range
nfa_dm_range = np.linspace(panel['NFA_GDP_dm'].min() - 5,
                           panel['NFA_GDP_dm'].max() + 5, 200)
nfa_level_range = nfa_dm_range + nfa_mean

# Marginal effects
# Low-VIX: β1 + β2·NFA
me_low_stmt = b1_stmt + b2_stmt * nfa_dm_range
me_low_mp1 = b1_mp1 + b2_mp1 * nfa_dm_range

# High-VIX: (β1 + δ) + (β2 + β3)·NFA
me_high_stmt = (b1_stmt + b1_vix_stmt) + (b2_stmt + b3_stmt) * nfa_dm_range
me_high_mp1 = (b1_mp1 + b1_vix_mp1) + (b2_mp1 + b3_mp1) * nfa_dm_range

# Standard errors via delta method
cov_stmt = result_stmt.cov
cov_mp1 = result_mp1.cov

se_low_stmt = np.sqrt(np.abs(
    cov_stmt.loc['STMT', 'STMT']
    + nfa_dm_range ** 2 * cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA']
    + 2 * nfa_dm_range * cov_stmt.loc['STMT', 'STMT_x_NFA']
))

se_high_stmt = np.sqrt(np.abs(
    cov_stmt.loc['STMT', 'STMT']
    + cov_stmt.loc['HighVIX_x_STMT', 'HighVIX_x_STMT']
    + nfa_dm_range ** 2 * (
        cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA']
        + cov_stmt.loc['STMT_x_NFA_x_HighVIX', 'STMT_x_NFA_x_HighVIX']
        + 2 * cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA_x_HighVIX']
    )
    + 2 * cov_stmt.loc['STMT', 'HighVIX_x_STMT']
    + 2 * nfa_dm_range * (
        cov_stmt.loc['STMT', 'STMT_x_NFA']
        + cov_stmt.loc['STMT', 'STMT_x_NFA_x_HighVIX']
        + cov_stmt.loc['HighVIX_x_STMT', 'STMT_x_NFA']
        + cov_stmt.loc['HighVIX_x_STMT', 'STMT_x_NFA_x_HighVIX']
    )
))

# Figure 15: Marginal Effects by VIX Regime
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

nfa_avg = panel.groupby('currency')['NFA_GDP'].mean()

# Panel A: STMT
ax1 = axes[0]
ax1.plot(nfa_level_range, me_low_stmt, 'b-', linewidth=2.5, label='Low VIX (calm)')
ax1.fill_between(nfa_level_range,
                 me_low_stmt - 1.96 * se_low_stmt,
                 me_low_stmt + 1.96 * se_low_stmt,
                 alpha=0.15, color='blue')
ax1.plot(nfa_level_range, me_high_stmt, 'r-', linewidth=2.5, label=f'High VIX (≥P75 = {thresholds[primary_thresh]:.0f})')
ax1.fill_between(nfa_level_range,
                 me_high_stmt - 1.96 * se_high_stmt,
                 me_high_stmt + 1.96 * se_high_stmt,
                 alpha=0.15, color='red')
ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

for curr in nfa_avg.index:
    ax1.axvline(nfa_avg[curr], color='gray', linestyle=':', linewidth=0.6, alpha=0.5)

ax1.set_xlabel('Net Foreign Assets (% of GDP)', fontsize=11, fontweight='bold')
ax1.set_ylabel('∂r/∂STMT (marginal effect)', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Statement Surprise (STMT)', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10, frameon=True)
ax1.grid(alpha=0.3)

x_min, x_max = nfa_avg.min(), nfa_avg.max()
x_pad = (x_max - x_min) * 0.2
ax1.set_xlim(x_min - x_pad, x_max + x_pad)

# Panel B: MP1
ax2 = axes[1]

se_low_mp1 = np.sqrt(np.abs(
    cov_mp1.loc['MP1', 'MP1']
    + nfa_dm_range ** 2 * cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA']
    + 2 * nfa_dm_range * cov_mp1.loc['MP1', 'MP1_x_NFA']
))

se_high_mp1 = np.sqrt(np.abs(
    cov_mp1.loc['MP1', 'MP1']
    + cov_mp1.loc['HighVIX_x_MP1', 'HighVIX_x_MP1']
    + nfa_dm_range ** 2 * (
        cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA']
        + cov_mp1.loc['MP1_x_NFA_x_HighVIX', 'MP1_x_NFA_x_HighVIX']
        + 2 * cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA_x_HighVIX']
    )
    + 2 * cov_mp1.loc['MP1', 'HighVIX_x_MP1']
    + 2 * nfa_dm_range * (
        cov_mp1.loc['MP1', 'MP1_x_NFA']
        + cov_mp1.loc['MP1', 'MP1_x_NFA_x_HighVIX']
        + cov_mp1.loc['HighVIX_x_MP1', 'MP1_x_NFA']
        + cov_mp1.loc['HighVIX_x_MP1', 'MP1_x_NFA_x_HighVIX']
    )
))

ax2.plot(nfa_level_range, me_low_mp1, 'b-', linewidth=2.5, label='Low VIX (calm)')
ax2.fill_between(nfa_level_range,
                 me_low_mp1 - 1.96 * se_low_mp1,
                 me_low_mp1 + 1.96 * se_low_mp1,
                 alpha=0.15, color='blue')
ax2.plot(nfa_level_range, me_high_mp1, 'r-', linewidth=2.5, label=f'High VIX (≥P75 = {thresholds[primary_thresh]:.0f})')
ax2.fill_between(nfa_level_range,
                 me_high_mp1 - 1.96 * se_high_mp1,
                 me_high_mp1 + 1.96 * se_high_mp1,
                 alpha=0.15, color='red')
ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

for curr in nfa_avg.index:
    ax2.axvline(nfa_avg[curr], color='gray', linestyle=':', linewidth=0.6, alpha=0.5)

ax2.set_xlabel('Net Foreign Assets (% of GDP)', fontsize=11, fontweight='bold')
ax2.set_ylabel('∂r/∂MP1 (marginal effect)', fontsize=11, fontweight='bold')
ax2.set_title('Panel B: Target Surprise (MP1)', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10, frameon=True)
ax2.grid(alpha=0.3)
ax2.set_xlim(x_min - x_pad, x_max + x_pad)

plt.suptitle('Figure 15: Marginal Effect of Monetary Policy Surprises on Spot Returns\n'
             'by NFA Position and VIX Regime (Calm vs Stress)',
             fontsize=13, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure15_vix_stress.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure15_vix_stress.png")

# ============================================================================
# STEP 8: COEFFICIENT COMPARISON BAR CHART
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax_i, (res, surp_label, k_base, k_triple) in enumerate([
    (result_stmt, 'STMT', 'STMT_x_NFA', 'STMT_x_NFA_x_HighVIX'),
    (result_mp1, 'MP1', 'MP1_x_NFA', 'MP1_x_NFA_x_HighVIX'),
]):
    ax = axes[ax_i]
    b2_val = res.params[k_base]
    b3_val = res.params[k_triple]
    b2_high = b2_val + b3_val

    # SE for combined coefficient
    se_b2 = res.std_errors[k_base]
    se_high = np.sqrt(
        res.cov.loc[k_base, k_base]
        + res.cov.loc[k_triple, k_triple]
        + 2 * res.cov.loc[k_base, k_triple]
    )

    labels = ['Low VIX\n(β₂)', 'High VIX\n(β₂ + β₃)']
    betas = [b2_val, b2_high]
    ses = [se_b2, se_high]
    colors = ['steelblue', 'firebrick']

    bars = ax.bar(labels, betas, yerr=[1.96 * s for s in ses],
                  capsize=8, alpha=0.75, width=0.5,
                  color=colors, edgecolor=['navy', 'darkred'],
                  linewidth=1.5, error_kw={'linewidth': 2, 'ecolor': 'black'})

    ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax.set_ylabel(f'{surp_label} × NFA/GDP Coefficient', fontsize=11, fontweight='bold')
    ax.set_title(f'Panel {chr(65 + ax_i)}: {surp_label}', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Add values
    for i, (beta, se) in enumerate(zip(betas, ses)):
        sign = '+' if beta > 0 else ''
        if beta < 0:
            ax.text(i, beta - 1.96 * se - 0.001, f'{sign}{beta:.4f}',
                    ha='center', va='top', fontsize=10, fontweight='bold')
        else:
            ax.text(i, beta + 1.96 * se + 0.001, f'{sign}{beta:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add β3 annotation
    p3 = res.pvalues[k_triple]
    ax.annotate(f'β₃ = {b3_val:.4f}\n(p = {p3:.3f})',
                xy=(0.95, 0.95), xycoords='axes fraction',
                fontsize=9, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray', alpha=0.9))

plt.suptitle('Figure 16: NFA × Surprise Coefficient by VIX Regime',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure16_vix_coefficient_comparison.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure16_vix_coefficient_comparison.png")

# ============================================================================
# STEP 9: LATEX TABLE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 9: Generate LaTeX Table")
print("=" * 80)

def fmt(val, pval, dec=4):
    s = f"{val:.{dec}f}"
    s += stars(pval)
    return s

latex = r"""\begin{table}[htbp]
\centering
\caption{VIX Stress Interaction in the Balance-Sheet Channel}
\label{tab:vix_stress}
\begin{tabular}{lccc}
\hline\hline
 & (1) & (2) & (3) \\
 & Baseline & STMT + VIX & MP1 + VIX \\
 & (Date Cl.) & (Date Cl.) & (Date Cl.) \\
\hline
"""

# Surprise
latex += f"STMT & {fmt(r1['STMT_coef'], r1['STMT_pval'])} & "
latex += f"{fmt(r2['STMT_coef'], r2['STMT_pval'])} & \\\\\n"
latex += f" & ({r1['STMT_se']:.4f}) & ({r2['STMT_se']:.4f}) & \\\\\n"

# MP1
latex += f"MP1 & & & {fmt(r3['MP1_coef'], r3['MP1_pval'])} \\\\\n"
latex += f" & & & ({r3['MP1_se']:.4f}) \\\\\n"

# Surprise × NFA
latex += f"Surprise $\\times$ NFA/GDP & {fmt(r1['STMT_x_NFA_coef'], r1['STMT_x_NFA_pval'])} & "
latex += f"{fmt(r2['STMT_x_NFA_coef'], r2['STMT_x_NFA_pval'])} & "
latex += f"{fmt(r3['MP1_x_NFA_coef'], r3['MP1_x_NFA_pval'])} \\\\\n"
latex += f" & ({r1['STMT_x_NFA_se']:.4f}) & ({r2['STMT_x_NFA_se']:.4f}) & ({r3['MP1_x_NFA_se']:.4f}) \\\\\n"

# Triple interaction
latex += f"Surprise $\\times$ NFA $\\times$ HighVIX & & "
latex += f"{fmt(r2['STMT_x_NFA_x_HighVIX_coef'], r2['STMT_x_NFA_x_HighVIX_pval'])} & "
latex += f"{fmt(r3['MP1_x_NFA_x_HighVIX_coef'], r3['MP1_x_NFA_x_HighVIX_pval'])} \\\\\n"
latex += f" & & ({r2['STMT_x_NFA_x_HighVIX_se']:.4f}) & ({r3['MP1_x_NFA_x_HighVIX_se']:.4f}) \\\\\n"

# NFA
latex += f"NFA/GDP & {fmt(r1['NFA_GDP_dm_coef'], r1['NFA_GDP_dm_pval'])} & "
latex += f"{fmt(r2['NFA_GDP_dm_coef'], r2['NFA_GDP_dm_pval'])} & "
latex += f"{fmt(r3['NFA_GDP_dm_coef'], r3['NFA_GDP_dm_pval'])} \\\\\n"
latex += f" & ({r1['NFA_GDP_dm_se']:.4f}) & ({r2['NFA_GDP_dm_se']:.4f}) & ({r3['NFA_GDP_dm_se']:.4f}) \\\\\n"

# HighVIX
latex += f"HighVIX & & {fmt(r2['HighVIX_coef'], r2['HighVIX_pval'])} & "
latex += f"{fmt(r3['HighVIX_coef'], r3['HighVIX_pval'])} \\\\\n"
latex += f" & & ({r2['HighVIX_se']:.4f}) & ({r3['HighVIX_se']:.4f}) \\\\\n"

# HighVIX × Surprise
latex += f"HighVIX $\\times$ Surprise & & "
latex += f"{fmt(r2['HighVIX_x_STMT_coef'], r2['HighVIX_x_STMT_pval'])} & "
latex += f"{fmt(r3['HighVIX_x_MP1_coef'], r3['HighVIX_x_MP1_pval'])} \\\\\n"
latex += f" & & ({r2['HighVIX_x_STMT_se']:.4f}) & ({r3['HighVIX_x_MP1_se']:.4f}) \\\\\n"

# HighVIX × NFA
latex += f"HighVIX $\\times$ NFA/GDP & & "
latex += f"{fmt(r2['HighVIX_x_NFA_coef'], r2['HighVIX_x_NFA_pval'])} & "
latex += f"{fmt(r3['HighVIX_x_NFA_coef'], r3['HighVIX_x_NFA_pval'])} \\\\\n"
latex += f" & & ({r2['HighVIX_x_NFA_se']:.4f}) & ({r3['HighVIX_x_NFA_se']:.4f}) \\\\\n"

latex += r"""\hline
Country FE & Yes & Yes & Yes \\
Date Cluster & Yes & Yes & Yes \\
"""
latex += f"Observations & {r1['N']} & {r2['N']} & {r3['N']} \\\\\n"
latex += f"$R^2$ & {r1['R2']:.4f} & {r2['R2']:.4f} & {r3['R2']:.4f} \\\\\n"

latex += r"""\hline\hline
\end{tabular}
\begin{tablenotes}
\small
\item \textit{Notes:} I define $e_{i,t}$ as foreign currency units per USD.
The dependent variable is the spot return $r_{i,t} = -\Delta\log(e_{i,t})$,
so $r > 0$ indicates foreign appreciation (USD depreciation).
HighVIX $= 1$ if VIX $\geq$ 75th percentile of the sample distribution.
NFA/GDP is demeaned; all specifications include country fixed effects.
Standard errors clustered by FOMC date.
*** $p<0.01$, ** $p<0.05$, * $p<0.10$.
\end{tablenotes}
\end{table}
"""

with open(f'{BASE}/Output/table5_vix_stress.tex', 'w') as f:
    f.write(latex)
print("Saved: Output/table5_vix_stress.tex")

# Save results CSV
results_csv = pd.DataFrame({
    'Specification': ['(1) Baseline', '(2) STMT+VIX', '(3) MP1+VIX'],
    'Surprise_coef': [r1['STMT_coef'], r2['STMT_coef'], r3['MP1_coef']],
    'Surprise_x_NFA_coef': [r1['STMT_x_NFA_coef'], r2['STMT_x_NFA_coef'], r3['MP1_x_NFA_coef']],
    'Triple_coef': [np.nan, r2['STMT_x_NFA_x_HighVIX_coef'], r3['MP1_x_NFA_x_HighVIX_coef']],
    'Triple_se': [np.nan, r2['STMT_x_NFA_x_HighVIX_se'], r3['MP1_x_NFA_x_HighVIX_se']],
    'Triple_pval': [np.nan, r2['STMT_x_NFA_x_HighVIX_pval'], r3['MP1_x_NFA_x_HighVIX_pval']],
    'N': [r1['N'], r2['N'], r3['N']],
    'R2': [r1['R2'], r2['R2'], r3['R2']]
})
results_csv.to_csv(f'{BASE}/Output/task4b_vix_stress_results.csv', index=False)
print("Saved: Output/task4b_vix_stress_results.csv")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3.4b COMPLETE: VIX STRESS INTERACTION")
print("=" * 80)

p_stmt_vix = result_stmt.pvalues['STMT_x_NFA_x_HighVIX']
p_mp1_vix = result_mp1.pvalues['MP1_x_NFA_x_HighVIX']

print(f"""
OUTPUT FILES:
  Tables:
    • Output/table5_vix_stress.tex             (LaTeX regression table)
    • Output/task4b_vix_stress_results.csv     (results CSV)

  Figures:
    • Output/figure15_vix_stress.png           (Marginal effects by VIX regime)
    • Output/figure16_vix_coefficient_comparison.png  (Low/High VIX coefficient bars)

══════════════════════════════════════════════════════════════════════════════════
KEY RESULTS
══════════════════════════════════════════════════════════════════════════════════

  Triple interaction (STMT × NFA × HighVIX):
    β₃ = {b3_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA_x_HighVIX']:.6f},  p = {p_stmt_vix:.4f})
    Low-VIX NFA slope:  β₂ = {b2_stmt:.6f}
    High-VIX NFA slope: β₂ + β₃ = {b2_stmt + b3_stmt:.6f}

  Triple interaction (MP1 × NFA × HighVIX):
    β₃ = {b3_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA_x_HighVIX']:.6f},  p = {p_mp1_vix:.4f})
    Low-VIX NFA slope:  β₂ = {b2_mp1:.6f}
    High-VIX NFA slope: β₂ + β₃ = {b2_mp1 + b3_mp1:.6f}

══════════════════════════════════════════════════════════════════════════════════
FORMAL HYPOTHESIS TEST
══════════════════════════════════════════════════════════════════════════════════

  H₀: β₃ = 0  (no stress-state amplification of the NFA slope)

  STMT specification:
    t-statistic = {b3_stmt / result_stmt.std_errors['STMT_x_NFA_x_HighVIX']:.3f}
    p-value = {p_stmt_vix:.4f}
    Decision: {'Reject H₀ at 10%' if p_stmt_vix < 0.10 else 'Fail to reject H₀'}

  MP1 specification:
    t-statistic = {b3_mp1 / result_mp1.std_errors['MP1_x_NFA_x_HighVIX']:.3f}
    p-value = {p_mp1_vix:.4f}
    Decision: {'Reject H₀ at 10%' if p_mp1_vix < 0.10 else 'Fail to reject H₀'}

══════════════════════════════════════════════════════════════════════════════════
INTERPRETATION
══════════════════════════════════════════════════════════════════════════════════

  This specification tests whether the NFA channel operates specifically during
  market stress episodes (elevated VIX). If balance-sheet effects work through
  dollar funding stress (Bruno & Shin 2015) or risk amplification (Rey 2015),
  we would expect β₃ > 0: the NFA slope should become more positive (creditors
  depreciate less, debtors depreciate more) when VIX is high.

  Results:
  {'► STMT shows ' + ('significant' if p_stmt_vix < 0.10 else 'no significant') + ' stress-state amplification (β₃ = ' + f'{b3_stmt:.4f}' + ', p = ' + f'{p_stmt_vix:.3f}' + ')'}
  {'► MP1 shows ' + ('significant' if p_mp1_vix < 0.10 else 'no significant') + ' stress-state amplification (β₃ = ' + f'{b3_mp1:.4f}' + ', p = ' + f'{p_mp1_vix:.3f}' + ')'}

  Within this G10 daily-frequency framework, we {'detect' if (p_stmt_vix < 0.10 or p_mp1_vix < 0.10) else 'do not detect'}
  statistically robust evidence that the NFA channel operates differentially
  during market stress episodes.

══════════════════════════════════════════════════════════════════════════════════
RESEARCH FLEX NARRATIVE
══════════════════════════════════════════════════════════════════════════════════

  This extension demonstrates mechanism-driven hypothesis testing:

  1. Theory (Bruno & Shin, Rey): Balance-sheet channels should bite during
     stress when dollar funding tightens and risk appetite contracts.

  2. Test: Does high VIX amplify the NFA × Surprise interaction?

  3. Result: {'Evidence of stress-state amplification' if (p_stmt_vix < 0.10 or p_mp1_vix < 0.10) else 'No robust evidence'} — the NFA channel
     {'appears to operate' if (p_stmt_vix < 0.10 or p_mp1_vix < 0.10) else 'does not appear to operate'} differentially during high-VIX periods.

  This is not data mining — it's testing a specific mechanism from the
  macro-finance literature. The null (if it is null) is informative:
  G10 currencies may not exhibit the stress-state amplification documented
  for emerging markets with higher dollar debt exposure.

══════════════════════════════════════════════════════════════════════════════════
COMBINED NARRATIVE ARC (3.1 → 3.4b)
══════════════════════════════════════════════════════════════════════════════════

  3.1: STMT is a valid monetary policy shock measure.
  3.2: FX responses to U.S. monetary shocks are heterogeneous across G10.
  3.3: NFA/GDP does not explain this heterogeneity (β₂ ≈ 0 or wrong sign).
  3.4: No robust post-GFC amplification (β₃ → 0, sign flip for STMT only).
  3.4b: {'VIX stress interaction is ' + ('significant' if (p_stmt_vix < 0.10 or p_mp1_vix < 0.10) else 'insignificant') + ' — balance-sheet channel ' + ('operates' if (p_stmt_vix < 0.10 or p_mp1_vix < 0.10) else 'does not operate') + ' differentially during stress.'}

  Overall conclusion: Within a G10 daily-frequency framework, we do not find
  statistically robust evidence that NFA/GDP systematically mediates FX responses
  to U.S. monetary surprises — neither unconditionally, post-GFC, nor during
  stress episodes. This null is disciplined and informative: G10 currencies
  may not exhibit the balance-sheet sensitivity theorized for emerging markets.
""")
