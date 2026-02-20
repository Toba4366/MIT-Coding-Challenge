"""
Task 3.4: Time Variation in the Balance-Sheet Channel
======================================================
Tests whether the interaction between monetary policy surprises and
NFA/GDP strengthened after the 2008 global financial crisis.

Hypothesis:
    If the NFA channel operates through dollar funding stress and
    valuation effects on USD-denominated liabilities, the interaction
    should strengthen post-GFC when dollar funding became more critical
    to global finance.

Specification:
    r_{i,t} = α_i + β1·Surprise_t + β2·(Surprise_t × NFA_{i,t-1})
              + β3·(Surprise_t × NFA_{i,t-1} × Post2008_t)
              + γ1·NFA_{i,t-1} + γ2·(NFA_{i,t-1} × Post2008_t)
              + δ·Post2008_t + ε_{i,t}

    where r_{i,t} = -Δlog(e_{i,t}), positive = foreign appreciation.

Marginal effect:
    Pre-GFC:  ∂r/∂Surprise = β1 + β2·NFA
    Post-GFC: ∂r/∂Surprise = β1 + (β2 + β3)·NFA

Test: Is β3 ≠ 0?

References:
    - Antolín-Díaz et al. (2023)
    - Lane & Milesi-Ferretti (2018)
    - Petersen (2009) on clustering
"""

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
from scipy import stats
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

# Base directory (parent of scripts/ folder where Data/ and Output/ exist)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{BASE}/Output', exist_ok=True)

print("=" * 80)
print("TASK 3.4: TIME VARIATION IN THE NFA CHANNEL")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD PANEL DATA & DEFINE STRUCTURAL BREAK
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Load Panel Data & Define Structural Break")
print("=" * 80)

panel = pd.read_csv(f'{BASE}/Output/task3_panel_data.csv')
panel['Date'] = pd.to_datetime(panel['Date'])

# Lehman Brothers collapse: September 15, 2008
BREAK_DATE = pd.Timestamp('2008-09-15')

panel['Post2008'] = (panel['Date'] >= BREAK_DATE).astype(int)

pre_count = (panel['Post2008'] == 0).sum()
post_count = (panel['Post2008'] == 1).sum()
pre_dates = panel.loc[panel['Post2008'] == 0, 'Date'].nunique()
post_dates = panel.loc[panel['Post2008'] == 1, 'Date'].nunique()

print(f"\nStructural break: {BREAK_DATE.strftime('%Y-%m-%d')} (Lehman collapse)")
print(f"Pre-GFC:  {pre_count:>5d} obs  ({pre_dates} FOMC events)")
print(f"Post-GFC: {post_count:>5d} obs  ({post_dates} FOMC events)")
print(f"Total:    {len(panel):>5d} obs")

# NFA summary by regime
nfa_mean = panel['NFA_GDP'].mean()
nfa_std = panel['NFA_GDP'].std()
print(f"\nNFA/GDP overall mean: {nfa_mean:.1f}%")
print(f"NFA/GDP overall std:  {nfa_std:.1f}%")
for regime, label in [(0, 'Pre-GFC'), (1, 'Post-GFC')]:
    sub = panel[panel['Post2008'] == regime]
    print(f"  {label}: mean={sub['NFA_GDP'].mean():.1f}%, "
          f"std={sub['NFA_GDP'].std():.1f}%, "
          f"range=[{sub['NFA_GDP'].min():.1f}%, {sub['NFA_GDP'].max():.1f}%]")

# ============================================================================
# STEP 2: CREATE INTERACTION TERMS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: Create Interaction Terms")
print("=" * 80)

# STMT interactions
panel['Post2008_x_STMT'] = panel['Post2008'] * panel['STMT']
panel['Post2008_x_NFA'] = panel['Post2008'] * panel['NFA_GDP_dm']
panel['STMT_x_NFA_x_Post'] = panel['STMT'] * panel['NFA_GDP_dm'] * panel['Post2008']

# MP1 interactions
panel['MP1_x_NFA'] = panel['MP1'] * panel['NFA_GDP_dm']
panel['Post2008_x_MP1'] = panel['Post2008'] * panel['MP1']
panel['MP1_x_NFA_x_Post'] = panel['MP1'] * panel['NFA_GDP_dm'] * panel['Post2008']

print("Interaction terms created:")
print("  STMT: STMT_x_NFA, Post2008_x_STMT, Post2008_x_NFA, STMT_x_NFA_x_Post")
print("  MP1:  MP1_x_NFA,  Post2008_x_MP1,  Post2008_x_NFA, MP1_x_NFA_x_Post")

# ============================================================================
# STEP 3: REGRESSIONS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: Panel Regressions")
print("=" * 80)

# Set panel index
panel_idx = panel.set_index(['currency', 'Date'])

# ---- (1) Baseline from 3.3 (reproduced for table) ----
print("\n--- Column (1): Baseline (reproduced from 3.3) ---")
exog_base = panel_idx[['STMT', 'STMT_x_NFA', 'NFA_GDP_dm']]
model_base = PanelOLS(panel_idx['d_e'], exog_base,
                      entity_effects=True, drop_absorbed=True, check_rank=False)
result_base = model_base.fit(cov_type='clustered', cluster_time=True)
print(result_base.summary)

# ---- (2) STMT with Post-2008 interaction ----
print("\n--- Column (2): STMT + Post-2008 Triple Interaction ---")
exog_stmt_cols = ['STMT', 'STMT_x_NFA', 'NFA_GDP_dm',
                  'Post2008', 'Post2008_x_STMT', 'Post2008_x_NFA',
                  'STMT_x_NFA_x_Post']
exog_stmt = panel_idx[exog_stmt_cols]
model_stmt = PanelOLS(panel_idx['d_e'], exog_stmt,
                      entity_effects=True, drop_absorbed=True, check_rank=False)
result_stmt = model_stmt.fit(cov_type='clustered', cluster_time=True)
print(result_stmt.summary)

# ---- (3) MP1 with Post-2008 interaction ----
print("\n--- Column (3): MP1 + Post-2008 Triple Interaction ---")
exog_mp1_cols = ['MP1', 'MP1_x_NFA', 'NFA_GDP_dm',
                 'Post2008', 'Post2008_x_MP1', 'Post2008_x_NFA',
                 'MP1_x_NFA_x_Post']
exog_mp1 = panel_idx[exog_mp1_cols].dropna()
dep_mp1 = panel_idx.loc[exog_mp1.index, 'd_e']
model_mp1 = PanelOLS(dep_mp1, exog_mp1,
                     entity_effects=True, drop_absorbed=True, check_rank=False)
result_mp1 = model_mp1.fit(cov_type='clustered', cluster_time=True)
print(result_mp1.summary)

# ============================================================================
# STEP 4: EXTRACT & DISPLAY RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: Results Summary")
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
                            'Post2008', 'Post2008_x_STMT', 'Post2008_x_NFA',
                            'STMT_x_NFA_x_Post'])
r3 = extract(result_mp1, ['MP1', 'MP1_x_NFA', 'NFA_GDP_dm',
                           'Post2008', 'Post2008_x_MP1', 'Post2008_x_NFA',
                           'MP1_x_NFA_x_Post'])

# Print compact table
print(f"\n{'':35s} {'(1) Baseline':>14s} {'(2) STMT+Post':>14s} {'(3) MP1+Post':>14s}")
print("-" * 80)

rows = [
    ('Surprise (STMT or MP1)', 'STMT', 'STMT', 'MP1'),
    ('Surprise × NFA/GDP', 'STMT_x_NFA', 'STMT_x_NFA', 'MP1_x_NFA'),
    ('Surprise × NFA × Post2008', None, 'STMT_x_NFA_x_Post', 'MP1_x_NFA_x_Post'),
    ('NFA/GDP', 'NFA_GDP_dm', 'NFA_GDP_dm', 'NFA_GDP_dm'),
    ('Post2008', None, 'Post2008', 'Post2008'),
    ('Post2008 × Surprise', None, 'Post2008_x_STMT', 'Post2008_x_MP1'),
    ('Post2008 × NFA/GDP', None, 'Post2008_x_NFA', 'Post2008_x_NFA'),
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
# STEP 5: MARGINAL EFFECTS BY REGIME
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: Marginal Effects by Regime")
print("=" * 80)

# STMT coefficients
b1_stmt = result_stmt.params['STMT']
b2_stmt = result_stmt.params['STMT_x_NFA']
b3_stmt = result_stmt.params['STMT_x_NFA_x_Post']
cov_stmt = result_stmt.cov

# MP1 coefficients
b1_mp1 = result_mp1.params['MP1']
b2_mp1 = result_mp1.params['MP1_x_NFA']
b3_mp1 = result_mp1.params['MP1_x_NFA_x_Post']
cov_mp1 = result_mp1.cov

# NFA range for plotting
nfa_dm_range = np.linspace(panel['NFA_GDP_dm'].min() - 5,
                           panel['NFA_GDP_dm'].max() + 5, 200)

# Pre-GFC marginal effect: β1 + β2·NFA_dm
me_pre_stmt = b1_stmt + b2_stmt * nfa_dm_range
me_pre_mp1 = b1_mp1 + b2_mp1 * nfa_dm_range

# Post-GFC marginal effect: (β1 + δ_surprise) + (β2 + β3)·NFA_dm
# But since we evaluate ∂r/∂Surprise, the Post2008_x_STMT shift also adds
b1_post_stmt = b1_stmt + result_stmt.params['Post2008_x_STMT']
b1_post_mp1 = b1_mp1 + result_mp1.params['Post2008_x_MP1']
me_post_stmt = b1_post_stmt + (b2_stmt + b3_stmt) * nfa_dm_range
me_post_mp1 = b1_post_mp1 + (b2_mp1 + b3_mp1) * nfa_dm_range

# Standard errors for pre/post marginal effects (STMT) via delta method
# Pre: Var(β1 + β2·n) = Var(β1) + n²·Var(β2) + 2n·Cov(β1,β2)
se_pre_stmt = np.sqrt(
    cov_stmt.loc['STMT', 'STMT']
    + nfa_dm_range ** 2 * cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA']
    + 2 * nfa_dm_range * cov_stmt.loc['STMT', 'STMT_x_NFA']
)

# Post: Var((β1+δ) + (β2+β3)·n)
# = Var(β1) + Var(δ) + n²·[Var(β2)+Var(β3)+2Cov(β2,β3)]
#   + 2Cov(β1,δ) + 2n·[Cov(β1,β2)+Cov(β1,β3)+Cov(δ,β2)+Cov(δ,β3)]
se_post_stmt = np.sqrt(np.abs(
    cov_stmt.loc['STMT', 'STMT']
    + cov_stmt.loc['Post2008_x_STMT', 'Post2008_x_STMT']
    + nfa_dm_range ** 2 * (
        cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA']
        + cov_stmt.loc['STMT_x_NFA_x_Post', 'STMT_x_NFA_x_Post']
        + 2 * cov_stmt.loc['STMT_x_NFA', 'STMT_x_NFA_x_Post']
    )
    + 2 * cov_stmt.loc['STMT', 'Post2008_x_STMT']
    + 2 * nfa_dm_range * (
        cov_stmt.loc['STMT', 'STMT_x_NFA']
        + cov_stmt.loc['STMT', 'STMT_x_NFA_x_Post']
        + cov_stmt.loc['Post2008_x_STMT', 'STMT_x_NFA']
        + cov_stmt.loc['Post2008_x_STMT', 'STMT_x_NFA_x_Post']
    )
))

# Print key coefficients
shock = 0.10  # 10 bps

print(f"\nSTMT SPECIFICATION:")
print(f"  β2 (pre-GFC NFA slope):      {b2_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA']:.6f})")
print(f"  β3 (post-GFC amplification): {b3_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA_x_Post']:.6f})")
print(f"  p-value for β3:              {result_stmt.pvalues['STMT_x_NFA_x_Post']:.4f}")
print(f"  Post-GFC NFA slope (β2+β3):  {b2_stmt + b3_stmt:.6f}")
print(f"\n  Pre-GFC:  10bp shock at mean NFA → {b1_stmt * shock:.4f}% spot return")
print(f"  Post-GFC: 10bp shock at mean NFA → {b1_post_stmt * shock:.4f}% spot return")

print(f"\nMP1 SPECIFICATION:")
print(f"  β2 (pre-GFC NFA slope):      {b2_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA']:.6f})")
print(f"  β3 (post-GFC amplification): {b3_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA_x_Post']:.6f})")
print(f"  p-value for β3:              {result_mp1.pvalues['MP1_x_NFA_x_Post']:.4f}")
print(f"  Post-GFC NFA slope (β2+β3):  {b2_mp1 + b3_mp1:.6f}")

# Marginal effect table at P25 and P75
nfa_25 = panel['NFA_GDP'].quantile(0.25)
nfa_75 = panel['NFA_GDP'].quantile(0.75)
nfa_25_dm = nfa_25 - nfa_mean
nfa_75_dm = nfa_75 - nfa_mean

print(f"\n{'─' * 80}")
print(f"  Marginal Effects at P25 (NFA={nfa_25:.0f}%) and P75 (NFA={nfa_75:.0f}%)")
print(f"  All effects: spot return (%) per 10bp hawkish surprise")
print(f"{'─' * 80}")
print(f"  {'':20s} {'P25 (Debtor)':>14s} {'P75 (Creditor)':>16s} {'Difference':>12s}")

for label, b1, b2, b3, b1p in [
    ('STMT Pre-GFC', b1_stmt, b2_stmt, 0, b1_stmt),
    ('STMT Post-GFC', b1_post_stmt, b2_stmt + b3_stmt, 0, b1_post_stmt),
    ('MP1 Pre-GFC', b1_mp1, b2_mp1, 0, b1_mp1),
    ('MP1 Post-GFC', b1_post_mp1, b2_mp1 + b3_mp1, 0, b1_post_mp1),
]:
    me_25 = (b1 + b2 * nfa_25_dm) * shock
    me_75 = (b1 + b2 * nfa_75_dm) * shock
    print(f"  {label:<20s} {me_25:>13.4f}% {me_75:>15.4f}% {me_75 - me_25:>11.4f}%")

print(f"{'─' * 80}")

# ============================================================================
# STEP 6: FIGURE 13 — MARGINAL EFFECTS BY REGIME
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: Generate Figures")
print("=" * 80)

plt.style.use('seaborn-v0_8-whitegrid')

# Convert demeaned NFA back to level for x-axis labels
nfa_level_range = nfa_dm_range + nfa_mean

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: STMT
ax1 = axes[0]
ax1.plot(nfa_level_range, me_pre_stmt, 'b-', linewidth=2.5, label='Pre-GFC (1994–2008)')
ax1.fill_between(nfa_level_range,
                 me_pre_stmt - 1.96 * se_pre_stmt,
                 me_pre_stmt + 1.96 * se_pre_stmt,
                 alpha=0.15, color='blue')
ax1.plot(nfa_level_range, me_post_stmt, 'r-', linewidth=2.5, label='Post-GFC (2008–2025)')
ax1.fill_between(nfa_level_range,
                 me_post_stmt - 1.96 * se_post_stmt,
                 me_post_stmt + 1.96 * se_post_stmt,
                 alpha=0.15, color='red')
ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

# Mark country positions
nfa_avg = panel.groupby('currency')['NFA_GDP'].mean()
for curr in nfa_avg.index:
    ax1.axvline(nfa_avg[curr], color='gray', linestyle=':', linewidth=0.6, alpha=0.5)

ax1.set_xlabel('Net Foreign Assets (% of GDP)', fontsize=11, fontweight='bold')
ax1.set_ylabel('∂r/∂STMT (marginal effect)', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Statement Surprise (STMT)', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10, frameon=True)
ax1.grid(alpha=0.3)

# Zoom to data range
x_min, x_max = nfa_avg.min(), nfa_avg.max()
x_pad = (x_max - x_min) * 0.2
ax1.set_xlim(x_min - x_pad, x_max + x_pad)

# Panel B: MP1
ax2 = axes[1]
# MP1 CIs (simpler — just use pre SE approach)
se_pre_mp1 = np.sqrt(np.abs(
    cov_mp1.loc['MP1', 'MP1']
    + nfa_dm_range ** 2 * cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA']
    + 2 * nfa_dm_range * cov_mp1.loc['MP1', 'MP1_x_NFA']
))
se_post_mp1 = np.sqrt(np.abs(
    cov_mp1.loc['MP1', 'MP1']
    + cov_mp1.loc['Post2008_x_MP1', 'Post2008_x_MP1']
    + nfa_dm_range ** 2 * (
        cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA']
        + cov_mp1.loc['MP1_x_NFA_x_Post', 'MP1_x_NFA_x_Post']
        + 2 * cov_mp1.loc['MP1_x_NFA', 'MP1_x_NFA_x_Post']
    )
    + 2 * cov_mp1.loc['MP1', 'Post2008_x_MP1']
    + 2 * nfa_dm_range * (
        cov_mp1.loc['MP1', 'MP1_x_NFA']
        + cov_mp1.loc['MP1', 'MP1_x_NFA_x_Post']
        + cov_mp1.loc['Post2008_x_MP1', 'MP1_x_NFA']
        + cov_mp1.loc['Post2008_x_MP1', 'MP1_x_NFA_x_Post']
    )
))

ax2.plot(nfa_level_range, me_pre_mp1, 'b-', linewidth=2.5, label='Pre-GFC (1994–2008)')
ax2.fill_between(nfa_level_range,
                 me_pre_mp1 - 1.96 * se_pre_mp1,
                 me_pre_mp1 + 1.96 * se_pre_mp1,
                 alpha=0.15, color='blue')
ax2.plot(nfa_level_range, me_post_mp1, 'r-', linewidth=2.5, label='Post-GFC (2008–2025)')
ax2.fill_between(nfa_level_range,
                 me_post_mp1 - 1.96 * se_post_mp1,
                 me_post_mp1 + 1.96 * se_post_mp1,
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

plt.suptitle('Figure 13: Marginal Effect of Monetary Policy Surprises on Spot Returns\n'
             'by NFA Position and Regime (Pre- vs Post-GFC)',
             fontsize=13, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure13_time_variation.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure13_time_variation.png")

# ============================================================================
# STEP 7: FIGURE 14 — COEFFICIENT COMPARISON BAR CHART
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax_i, (res, surp_label, k_base, k_triple) in enumerate([
    (result_stmt, 'STMT', 'STMT_x_NFA', 'STMT_x_NFA_x_Post'),
    (result_mp1, 'MP1', 'MP1_x_NFA', 'MP1_x_NFA_x_Post'),
]):
    ax = axes[ax_i]
    b2_val = res.params[k_base]
    b3_val = res.params[k_triple]
    b2_post = b2_val + b3_val

    # SE for post-GFC combined coefficient via delta method
    se_b2 = res.std_errors[k_base]
    se_post = np.sqrt(
        res.cov.loc[k_base, k_base]
        + res.cov.loc[k_triple, k_triple]
        + 2 * res.cov.loc[k_base, k_triple]
    )

    labels = ['Pre-GFC\n(β₂)', 'Post-GFC\n(β₂ + β₃)']
    betas = [b2_val, b2_post]
    ses = [se_b2, se_post]
    colors = ['steelblue', 'coral']

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

plt.suptitle('Figure 14: NFA × Surprise Coefficient by Regime',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure14_coefficient_comparison.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure14_coefficient_comparison.png")

# ============================================================================
# STEP 8: LATEX TABLE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 8: Generate LaTeX Table")
print("=" * 80)

def fmt(val, pval, dec=4):
    s = f"{val:.{dec}f}"
    s += stars(pval)
    return s

latex = r"""\begin{table}[htbp]
\centering
\caption{Time Variation in the Balance-Sheet Channel}
\label{tab:time_variation}
\begin{tabular}{lccc}
\hline\hline
 & (1) & (2) & (3) \\
 & Baseline & STMT + Post-GFC & MP1 + Post-GFC \\
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
latex += f"Surprise $\\times$ NFA $\\times$ Post2008 & & "
latex += f"{fmt(r2['STMT_x_NFA_x_Post_coef'], r2['STMT_x_NFA_x_Post_pval'])} & "
latex += f"{fmt(r3['MP1_x_NFA_x_Post_coef'], r3['MP1_x_NFA_x_Post_pval'])} \\\\\n"
latex += f" & & ({r2['STMT_x_NFA_x_Post_se']:.4f}) & ({r3['MP1_x_NFA_x_Post_se']:.4f}) \\\\\n"

# NFA
latex += f"NFA/GDP & {fmt(r1['NFA_GDP_dm_coef'], r1['NFA_GDP_dm_pval'])} & "
latex += f"{fmt(r2['NFA_GDP_dm_coef'], r2['NFA_GDP_dm_pval'])} & "
latex += f"{fmt(r3['NFA_GDP_dm_coef'], r3['NFA_GDP_dm_pval'])} \\\\\n"
latex += f" & ({r1['NFA_GDP_dm_se']:.4f}) & ({r2['NFA_GDP_dm_se']:.4f}) & ({r3['NFA_GDP_dm_se']:.4f}) \\\\\n"

# Post2008
latex += f"Post2008 & & {fmt(r2['Post2008_coef'], r2['Post2008_pval'])} & "
latex += f"{fmt(r3['Post2008_coef'], r3['Post2008_pval'])} \\\\\n"
latex += f" & & ({r2['Post2008_se']:.4f}) & ({r3['Post2008_se']:.4f}) \\\\\n"

# Post2008 × Surprise
latex += f"Post2008 $\\times$ Surprise & & "
latex += f"{fmt(r2['Post2008_x_STMT_coef'], r2['Post2008_x_STMT_pval'])} & "
latex += f"{fmt(r3['Post2008_x_MP1_coef'], r3['Post2008_x_MP1_pval'])} \\\\\n"
latex += f" & & ({r2['Post2008_x_STMT_se']:.4f}) & ({r3['Post2008_x_MP1_se']:.4f}) \\\\\n"

# Post2008 × NFA
latex += f"Post2008 $\\times$ NFA/GDP & & "
latex += f"{fmt(r2['Post2008_x_NFA_coef'], r2['Post2008_x_NFA_pval'])} & "
latex += f"{fmt(r3['Post2008_x_NFA_coef'], r3['Post2008_x_NFA_pval'])} \\\\\n"
latex += f" & & ({r2['Post2008_x_NFA_se']:.4f}) & ({r3['Post2008_x_NFA_se']:.4f}) \\\\\n"

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
Post2008 $= 1$ for dates after September 15, 2008 (Lehman collapse).
NFA/GDP is demeaned; all specifications include country fixed effects.
Standard errors clustered by FOMC date (preferred: common shock structure).
*** $p<0.01$, ** $p<0.05$, * $p<0.10$.
\end{tablenotes}
\end{table}
"""

with open(f'{BASE}/Output/table4_time_variation.tex', 'w') as f:
    f.write(latex)
print("Saved: Output/table4_time_variation.tex")

# Save results CSV
results_csv = pd.DataFrame({
    'Specification': ['(1) Baseline', '(2) STMT+Post2008', '(3) MP1+Post2008'],
    'Surprise_coef': [r1['STMT_coef'], r2['STMT_coef'], r3['MP1_coef']],
    'Surprise_x_NFA_coef': [r1['STMT_x_NFA_coef'], r2['STMT_x_NFA_coef'], r3['MP1_x_NFA_coef']],
    'Triple_coef': [np.nan, r2['STMT_x_NFA_x_Post_coef'], r3['MP1_x_NFA_x_Post_coef']],
    'Triple_se': [np.nan, r2['STMT_x_NFA_x_Post_se'], r3['MP1_x_NFA_x_Post_se']],
    'Triple_pval': [np.nan, r2['STMT_x_NFA_x_Post_pval'], r3['MP1_x_NFA_x_Post_pval']],
    'N': [r1['N'], r2['N'], r3['N']],
    'R2': [r1['R2'], r2['R2'], r3['R2']]
})
results_csv.to_csv(f'{BASE}/Output/task4_time_variation_results.csv', index=False)
print("Saved: Output/task4_time_variation_results.csv")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3.4 COMPLETE")
print("=" * 80)

p_stmt = result_stmt.pvalues['STMT_x_NFA_x_Post']
p_mp1 = result_mp1.pvalues['MP1_x_NFA_x_Post']

# Economic magnitude calculation (1 SD NFA ≈ 70pp based on cross-country variation)
nfa_1sd = nfa_std  # already computed above
pre_stmt_sensitivity_change = b2_stmt * nfa_1sd  # change in sensitivity from mean to +1SD NFA
post_stmt_sensitivity_change = (b2_stmt + b3_stmt) * nfa_1sd
pre_mp1_sensitivity_change = b2_mp1 * nfa_1sd
post_mp1_sensitivity_change = (b2_mp1 + b3_mp1) * nfa_1sd

# For 10bp shock, translate to FX response
shock_size = 0.10  # 10 bps
pre_stmt_fx_swing = pre_stmt_sensitivity_change * shock_size
post_stmt_fx_swing = post_stmt_sensitivity_change * shock_size

print(f"""
OUTPUT FILES:
  Tables:
    • Output/table4_time_variation.tex           (LaTeX regression table)
    • Output/task4_time_variation_results.csv     (results CSV)

  Figures:
    • Output/figure13_time_variation.png          (Marginal effects by regime)
    • Output/figure14_coefficient_comparison.png  (Pre/Post coefficient bars)

══════════════════════════════════════════════════════════════════════════════════
KEY RESULTS
══════════════════════════════════════════════════════════════════════════════════

  Triple interaction (STMT × NFA × Post2008):
    β₃ = {b3_stmt:.6f}  (SE: {result_stmt.std_errors['STMT_x_NFA_x_Post']:.6f},  p = {p_stmt:.4f})
    Pre-GFC NFA slope:  β₂ = {b2_stmt:.6f}
    Post-GFC NFA slope: β₂ + β₃ = {b2_stmt + b3_stmt:.6f}

  Triple interaction (MP1 × NFA × Post2008):
    β₃ = {b3_mp1:.6f}  (SE: {result_mp1.std_errors['MP1_x_NFA_x_Post']:.6f},  p = {p_mp1:.4f})
    Pre-GFC NFA slope:  β₂ = {b2_mp1:.6f}
    Post-GFC NFA slope: β₂ + β₃ = {b2_mp1 + b3_mp1:.6f}

══════════════════════════════════════════════════════════════════════════════════
FORMAL HYPOTHESIS TEST
══════════════════════════════════════════════════════════════════════════════════

  H₀: β₃ = 0  (no time variation in the NFA slope)

  STMT specification:
    t-statistic = {b3_stmt / result_stmt.std_errors['STMT_x_NFA_x_Post']:.3f}
    p-value = {p_stmt:.4f}
    Decision: {'Reject H₀ at 10%' if p_stmt < 0.10 else 'Fail to reject H₀'}

  MP1 specification:
    t-statistic = {b3_mp1 / result_mp1.std_errors['MP1_x_NFA_x_Post']:.3f}
    p-value = {p_mp1:.4f}
    Decision: {'Reject H₀ at 10%' if p_mp1 < 0.10 else 'Fail to reject H₀'}

  Summary: We fail to reject equality of pre- and post-GFC NFA slopes.

══════════════════════════════════════════════════════════════════════════════════
ECONOMIC MAGNITUDE
══════════════════════════════════════════════════════════════════════════════════

  NFA/GDP standard deviation: {nfa_1sd:.1f} percentage points

  STMT specification:
    Pre-GFC:  1 SD higher NFA shifts sensitivity by {pre_stmt_sensitivity_change:.4f}
              For a 10bp shock → {pre_stmt_fx_swing:.4f}% FX response difference
    Post-GFC: 1 SD higher NFA shifts sensitivity by {post_stmt_sensitivity_change:.4f}
              For a 10bp shock → {post_stmt_fx_swing:.4f}% FX response difference

  The post-GFC coefficient is economically meaningful in direction:
    Slope shifts from {b2_stmt:.4f} (creditors depreciate MORE) 
                  to  {b2_stmt + b3_stmt:.4f} (creditors depreciate LESS)
    This is consistent with—though not statistically confirmatory of—
    a post-crisis strengthening of balance-sheet mechanisms (Antolín-Díaz).

  The MP1 shows no such shift: slope remains ~{b2_mp1:.4f} both regimes.

══════════════════════════════════════════════════════════════════════════════════
STMT VS MP1 CONTRAST
══════════════════════════════════════════════════════════════════════════════════

  A striking pattern emerges from comparing the two shock measures:

  • STMT (communication component): 
      Pre-GFC slope: {b2_stmt:.4f} (negative → creditors depreciate more)
      Post-GFC slope: {b2_stmt + b3_stmt:.4f} (flips sign → toward Antolín-Díaz)
      β₃ = {b3_stmt:.4f} (p = {p_stmt:.3f}) — directionally positive, imprecise

  • MP1 (pure rate shock):
      Pre-GFC slope: {b2_mp1:.4f} 
      Post-GFC slope: {b2_mp1 + b3_mp1:.4f} (essentially unchanged)
      β₃ = {b3_mp1:.4f} (p = {p_mp1:.3f}) — no structural shift

  This suggests the post-GFC regime change, if any, operates through
  the information/communication channel rather than the pure rate channel.
  Alternatively, the STMT result is statistical noise—we lack power to
  distinguish these interpretations definitively.

══════════════════════════════════════════════════════════════════════════════════
R² DIAGNOSTIC
══════════════════════════════════════════════════════════════════════════════════

  Baseline R²:      {r1['R2']:.4f}
  STMT + Post R²:   {r2['R2']:.4f}
  MP1 + Post R²:    {r3['R2']:.4f}

  The low within R² (~0.001–0.006) indicates that daily FX variation is
  dominated by non-monetary forces, limiting statistical power to detect
  cross-sectional heterogeneity. This is a feature of daily data, not a
  specification failure—most FX variance at this frequency is orthogonal
  to identified monetary policy shocks.

══════════════════════════════════════════════════════════════════════════════════
INTERPRETATION
══════════════════════════════════════════════════════════════════════════════════

  Within the G10 sample and daily frequency framework, we do not detect
  statistically robust amplification of the NFA channel after the 2008
  global financial crisis.

  The STMT specification exhibits an economically interesting sign flip
  (β₂ < 0 → β₂ + β₃ > 0), suggestive of—but not confirmatory for—a
  post-GFC strengthening of balance-sheet mechanisms. The MP1 specification
  shows no time variation whatsoever (β₃ ≈ 0).

  This null is notable given that:
  (1) Dollar funding stress increased post-2008,
  (2) External balance sheets expanded significantly,
  (3) Regulatory changes made dollar exposure more salient.

  Three explanations are consistent with this result:

  1. Offsetting channels: Post-GFC central bank interventions (swap lines,
     QE, forward guidance) may have dampened the valuation channel by
     stabilizing dollar funding markets, offsetting any amplification.

  2. Granular heterogeneity: The 8-currency G10 sample may mask important
     variation. Emerging markets with higher dollar debt shares might
     exhibit stronger post-GFC effects, but they are not included here.

  3. Non-linearities: The channel may operate only at extreme NFA values
     or during acute stress episodes (e.g., March 2020), which are averaged
     out in a linear specification with a single structural break.

══════════════════════════════════════════════════════════════════════════════════
NARRATIVE ARC
══════════════════════════════════════════════════════════════════════════════════

  Across specifications, we find strong transmission to U.S. yields (Section
  3.2) but weak and noisy daily FX responses. In Sections 3.3–3.4 we test
  whether cross-country external balance sheets (NFA/GDP) explain heterogeneity
  in FX responses and whether this channel strengthened after 2008.

  The estimated interaction is imprecise and sensitive to the shock definition:
  for STMT, the NFA slope shifts from negative pre-GFC to slightly positive
  post-GFC (β₃ > 0), consistent with—though not statistically supportive of—
  a post-crisis strengthening of balance-sheet mechanisms; for MP1, we detect
  no structural change.

  Overall, within a G10 daily-frequency framework, we do not find statistically
  robust evidence that NFA/GDP systematically mediates FX responses to U.S.
  monetary surprises. Extensions using intraday data, gross external positions,
  or expanded currency samples are warranted.
""")
