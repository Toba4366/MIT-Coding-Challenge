"""
Task 3.3: The Role of External Positions
=========================================
Panel regression testing whether Net Foreign Asset (NFA) positions
moderate currency responses to U.S. monetary policy surprises.

Specification:
    Δe_{i,t} = α_i + β1·STMT_t + β2·(STMT_t × NFA_{i,t-1}) + γ·NFA_{i,t-1} + ε_{i,t}

Identification:
    Cross-country differences in predetermined balance sheet positions
    interacting with exogenous high-frequency U.S. monetary shocks.

Data:
    - FOMC surprises: Output/merged_fomc_data.csv (from Task 1)
    - NFA/GDP: Lane & Milesi-Ferretti External Wealth of Nations (2024 update)
    - Country betas from Task 3.2: Output/task2_country_betas.csv

References:
    - Antolín-Díaz et al. (2023)
    - Lane & Milesi-Ferretti (2018)
    - Petersen (2009) on clustering
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from linearmodels.panel import PanelOLS
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

BASE = '/Users/trentonobannontrenton/MIT Coding Challenge'
os.makedirs(f'{BASE}/Output', exist_ok=True)

print("=" * 80)
print("TASK 3.3: THE ROLE OF EXTERNAL POSITIONS")
print("=" * 80)

# ============================================================================
# STEP 0: GENERATE COUNTRY BETAS FROM TASK 3.2 (if not already saved)
# ============================================================================

merged = pd.read_csv(f'{BASE}/Output/merged_fomc_data.csv')
merged['Date'] = pd.to_datetime(merged['Date'])

betas_path = f'{BASE}/Output/task2_country_betas.csv'

fx_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'MXN', 'NOK']

if not os.path.exists(betas_path):
    print("\nGenerating country-specific FX betas from Task 3.2...")
    country_betas = {}
    merged['STMT_bps'] = merged['STMT'] * 100

    for curr in fx_currencies:
        col = f'd_{curr}'
        if col not in merged.columns:
            continue
        valid = merged[['STMT_bps', col]].dropna()
        if len(valid) < 30:
            continue
        n = len(valid)
        X = np.column_stack([np.ones(n), valid['STMT_bps'].values])
        y = valid[col].values
        XtX_inv = np.linalg.inv(X.T @ X)
        b = XtX_inv @ X.T @ y
        resid = y - X @ b
        meat = X.T @ np.diag(resid ** 2) @ X
        robust_var = XtX_inv @ meat @ XtX_inv * (n / (n - 2))
        robust_se = np.sqrt(np.diag(robust_var))
        t_stat = b / robust_se
        p_val = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=n - 2))
        country_betas[curr] = {
            'beta': b[1], 'se': robust_se[1],
            'tstat': t_stat[1], 'pval': p_val[1],
            'N': n, 'R2': 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
        }

    betas_df = pd.DataFrame(country_betas).T
    betas_df.index.name = 'currency'
    betas_df.to_csv(betas_path)
    print(f"  Saved: {betas_path}")
else:
    betas_df = pd.read_csv(betas_path, index_col=0)
    print(f"\nLoaded country betas from: {betas_path}")

print("\nCountry-specific FX betas (from Task 3.2):")
print(betas_df[['beta', 'se', 'tstat', 'pval']].to_string(float_format='%.4f'))

# Also generate MP1 country betas for robustness scatter
mp1_betas_path = f'{BASE}/Output/task2_country_betas_mp1.csv'
if not os.path.exists(mp1_betas_path):
    print("\nGenerating MP1-based country betas...")
    mp1_country_betas = {}
    merged['MP1_bps'] = merged['MP1'] * 100
    for curr in fx_currencies:
        col = f'd_{curr}'
        if col not in merged.columns:
            continue
        valid = merged[['MP1_bps', col]].dropna()
        if len(valid) < 30:
            continue
        n = len(valid)
        X = np.column_stack([np.ones(n), valid['MP1_bps'].values])
        y = valid[col].values
        XtX_inv = np.linalg.inv(X.T @ X)
        b = XtX_inv @ X.T @ y
        resid = y - X @ b
        meat = X.T @ np.diag(resid ** 2) @ X
        robust_var = XtX_inv @ meat @ XtX_inv * (n / (n - 2))
        robust_se = np.sqrt(np.diag(robust_var))
        t_stat = b / robust_se
        p_val = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=n - 2))
        mp1_country_betas[curr] = {
            'beta': b[1], 'se': robust_se[1],
            'tstat': t_stat[1], 'pval': p_val[1],
            'N': n, 'R2': 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
        }
    mp1_betas_df = pd.DataFrame(mp1_country_betas).T
    mp1_betas_df.index.name = 'currency'
    mp1_betas_df.to_csv(mp1_betas_path)
    print(f"  Saved: {mp1_betas_path}")
else:
    mp1_betas_df = pd.read_csv(mp1_betas_path, index_col=0)
    print(f"\nLoaded MP1 country betas from: {mp1_betas_path}")

# ============================================================================
# STEP 1: LOAD NFA DATA FROM EWN DATABASE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Load NFA/GDP from External Wealth of Nations Database")
print("=" * 80)

ewn = pd.read_excel(f'{BASE}/Data/EWN-dataset-year-end-2024_feb06.xlsx',
                     sheet_name='Dataset')

# NFA/GDP column (in decimal: 0.60 = 60% of GDP)
nfa_col = 'net IIP excl gold / GDP domestic currency'

# Map EWN country names → currency codes
country_to_currency = {
    'Canada': 'CAD',
    'Japan': 'JPY',
    'Mexico': 'MXN',
    'Norway': 'NOK',
    'Switzerland': 'CHF',
    'Australia': 'AUD',
    'Euro Area': 'EUR',
    'United Kingdom': 'GBP'
}

# Extract NFA/GDP for our countries
nfa_rows = []
for country_name, curr in country_to_currency.items():
    subset = ewn[ewn['Country'] == country_name][['Year', nfa_col]].copy()
    subset = subset.rename(columns={nfa_col: 'NFA_GDP_raw'})
    subset['currency'] = curr
    # Convert to percentage points (0.60 → 60.0)
    subset['NFA_GDP'] = subset['NFA_GDP_raw'] * 100
    nfa_rows.append(subset[['currency', 'Year', 'NFA_GDP']].dropna())

nfa = pd.concat(nfa_rows, ignore_index=True)

# Use LAGGED NFA: shift year forward by 1 so year=2015 NFA is used for 2016 events
nfa['year_for_merge'] = nfa['Year'] + 1

print(f"\nNFA data loaded: {len(nfa)} country-year observations")
print(f"Year range: {nfa['Year'].min()} - {nfa['Year'].max()}")
print(f"Currencies: {sorted(nfa['currency'].unique())}")

print("\nSample NFA/GDP (lagged, % of GDP) — latest available:")
latest = nfa.sort_values('Year').groupby('currency').last()
print(latest[['Year', 'NFA_GDP']].sort_values('NFA_GDP').to_string(float_format='%.1f'))

# ============================================================================
# STEP 2: RESHAPE FOMC DATA TO PANEL (LONG FORMAT)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: Reshape to Panel Format")
print("=" * 80)

fx_cols = [f'd_{c}' for c in fx_currencies]

# Keep relevant columns
panel = merged[['Date', 'STMT', 'MP1'] + fx_cols].copy()

# Melt wide → long
panel_long = pd.melt(
    panel,
    id_vars=['Date', 'STMT', 'MP1'],
    value_vars=fx_cols,
    var_name='currency',
    value_name='d_e'
)

# Clean currency names: d_CAD → CAD
panel_long['currency'] = panel_long['currency'].str.replace('d_', '', regex=False)

# Drop missing
panel_long = panel_long.dropna(subset=['d_e', 'STMT'])

# Add year for merge (using lagged NFA)
panel_long['year_for_merge'] = panel_long['Date'].dt.year

print(f"Panel observations (before NFA merge): {len(panel_long)}")
print(f"FOMC events: {panel_long['Date'].nunique()}")
print(f"Currencies: {panel_long['currency'].nunique()}")

# ============================================================================
# STEP 3: MERGE NFA/GDP DATA
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: Merge NFA/GDP (Lagged)")
print("=" * 80)

panel_long = panel_long.merge(
    nfa[['currency', 'year_for_merge', 'NFA_GDP']],
    on=['currency', 'year_for_merge'],
    how='left'
)

n_total = len(panel_long)
n_missing = panel_long['NFA_GDP'].isna().sum()
print(f"NFA merge: {n_total - n_missing}/{n_total} matched ({n_missing} missing)")

# Show missing by currency
missing_by_curr = panel_long.groupby('currency')['NFA_GDP'].apply(lambda x: x.isna().sum())
print("\nMissing NFA by currency:")
print(missing_by_curr.to_string())

# Drop observations without NFA
panel_long = panel_long.dropna(subset=['NFA_GDP'])
print(f"\nFinal panel: {len(panel_long)} observations")
print(f"  FOMC events: {panel_long['Date'].nunique()}")
print(f"  Currencies: {panel_long['currency'].nunique()}")
print(f"  Date range: {panel_long['Date'].min().strftime('%Y-%m-%d')} to "
      f"{panel_long['Date'].max().strftime('%Y-%m-%d')}")

# ============================================================================
# STEP 4: CREATE INTERACTION TERMS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: Create Interaction Terms")
print("=" * 80)

# Demean NFA so β1 = effect at average NFA
nfa_mean = panel_long['NFA_GDP'].mean()
panel_long['NFA_GDP_dm'] = panel_long['NFA_GDP'] - nfa_mean

# Interaction: STMT × demeaned NFA
panel_long['STMT_x_NFA'] = panel_long['STMT'] * panel_long['NFA_GDP_dm']

print(f"NFA/GDP mean: {nfa_mean:.1f}% of GDP")
print(f"NFA/GDP range: {panel_long['NFA_GDP'].min():.1f}% to {panel_long['NFA_GDP'].max():.1f}%")
print(f"NFA/GDP std: {panel_long['NFA_GDP'].std():.1f}%")

# Summary by currency
nfa_summary = panel_long.groupby('currency')['NFA_GDP'].agg(['mean', 'std', 'min', 'max'])
print("\nNFA/GDP by currency (% of GDP):")
print(nfa_summary.sort_values('mean').to_string(float_format='%.1f'))

# ============================================================================
# STEP 5: RUN PANEL REGRESSIONS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: Panel Regressions with Country Fixed Effects")
print("=" * 80)

# Set panel index
panel_reg = panel_long.set_index(['currency', 'Date'])

# Dependent variable
dep = panel_reg['d_e']

# Regressors: STMT, STMT×NFA (demeaned), NFA (demeaned)
exog = panel_reg[['STMT', 'STMT_x_NFA', 'NFA_GDP_dm']]

# Build model with entity (country) fixed effects
model = PanelOLS(
    dependent=dep,
    exog=exog,
    entity_effects=True,
    drop_absorbed=True,
    check_rank=False
)

# ---- Main specification: clustered by FOMC date ----
print("\n--- Main Specification: Clustered by FOMC Date ---")
result_date = model.fit(cov_type='clustered', cluster_time=True)
print(result_date.summary)

# ---- Robustness: Two-way clustering (country + date) ----
print("\n--- Robustness: Two-Way Clustering (Country + Date) ---")
result_twoway = model.fit(cov_type='clustered', cluster_entity=True, cluster_time=True)
print(result_twoway.summary)

# ---- Robustness: Clustered by country only ----
print("\n--- Robustness: Clustered by Country ---")
result_country = model.fit(cov_type='clustered', cluster_entity=True)
print(result_country.summary)

# ---- Robustness: MP1 instead of STMT ----
print("\n--- Robustness: MP1 as Alternative Surprise Measure ---")
panel_reg_mp1 = panel_long.copy()
panel_reg_mp1['MP1_x_NFA'] = panel_reg_mp1['MP1'] * panel_reg_mp1['NFA_GDP_dm']
panel_reg_mp1 = panel_reg_mp1.dropna(subset=['MP1']).set_index(['currency', 'Date'])

model_mp1 = PanelOLS(
    dependent=panel_reg_mp1['d_e'],
    exog=panel_reg_mp1[['MP1', 'MP1_x_NFA', 'NFA_GDP_dm']],
    entity_effects=True,
    drop_absorbed=True,
    check_rank=False
)
result_mp1 = model_mp1.fit(cov_type='clustered', cluster_time=True)
print(result_mp1.summary)

# ---- Robustness: Z-score standardized NFA ----
print("\n--- Robustness: Z-Score Standardized NFA ---")
panel_reg_z = panel_long.copy()
nfa_std = panel_reg_z['NFA_GDP'].std()
panel_reg_z['NFA_GDP_z'] = (panel_reg_z['NFA_GDP'] - nfa_mean) / nfa_std
panel_reg_z['STMT_x_NFA_z'] = panel_reg_z['STMT'] * panel_reg_z['NFA_GDP_z']
panel_reg_z = panel_reg_z.set_index(['currency', 'Date'])

model_z = PanelOLS(
    dependent=panel_reg_z['d_e'],
    exog=panel_reg_z[['STMT', 'STMT_x_NFA_z', 'NFA_GDP_z']],
    entity_effects=True,
    drop_absorbed=True,
    check_rank=False
)
result_z = model_z.fit(cov_type='clustered', cluster_time=True)
print(result_z.summary)
print(f"\n  Z-score interpretation: 1 SD of NFA/GDP = {nfa_std:.1f} pp")
print(f"  β2(z) = {result_z.params['STMT_x_NFA_z']:.4f}")
print(f"  → A 1 SD increase in NFA/GDP changes the STMT effect by {result_z.params['STMT_x_NFA_z']:.4f} pp")

# ============================================================================
# STEP 6: COLLECT RESULTS FOR TABLE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: Results Summary")
print("=" * 80)

def extract_results(res, labels):
    """Extract params, SEs, p-values from a PanelOLS result."""
    out = {}
    for lab in labels:
        out[f'{lab}_coef'] = res.params.get(lab, np.nan)
        out[f'{lab}_se'] = res.std_errors.get(lab, np.nan)
        out[f'{lab}_pval'] = res.pvalues.get(lab, np.nan)
    out['N'] = int(res.nobs)
    out['R2'] = res.rsquared
    return out

labels_main = ['STMT', 'STMT_x_NFA', 'NFA_GDP_dm']
labels_mp1 = ['MP1', 'MP1_x_NFA', 'NFA_GDP_dm']

r1 = extract_results(result_date, labels_main)
r2 = extract_results(result_twoway, labels_main)
r3 = extract_results(result_country, labels_main)
r4 = extract_results(result_mp1, labels_mp1)

def stars(p):
    if pd.isna(p): return ''
    if p < 0.01: return '***'
    if p < 0.05: return '**'
    if p < 0.10: return '*'
    return ''

print(f"\n{'':30s} {'(1) Date':>14s} {'(2) Two-Way':>14s} {'(3) Country':>14s} {'(4) MP1':>14s}")
print(f"{'':30s} {'Cluster':>14s} {'Cluster':>14s} {'Cluster':>14s} {'(Date Cl.)':>14s}")
print("-" * 90)

# STMT row
print(f"{'STMT':30s} {r1['STMT_coef']:>10.4f}{stars(r1['STMT_pval']):4s} "
      f"{r2['STMT_coef']:>10.4f}{stars(r2['STMT_pval']):4s} "
      f"{r3['STMT_coef']:>10.4f}{stars(r3['STMT_pval']):4s} {'':>14s}")
print(f"{'':30s} ({r1['STMT_se']:>8.4f})    ({r2['STMT_se']:>8.4f})    "
      f"({r3['STMT_se']:>8.4f})    {'':>14s}")

# MP1 row
print(f"{'MP1':30s} {'':>14s} {'':>14s} {'':>14s} "
      f"{r4['MP1_coef']:>10.4f}{stars(r4['MP1_pval']):4s}")
print(f"{'':30s} {'':>14s} {'':>14s} {'':>14s} "
      f"({r4['MP1_se']:>8.4f})   ")

# Interaction row (STMT × NFA)
print(f"{'Surprise × NFA/GDP':30s} {r1['STMT_x_NFA_coef']:>10.4f}{stars(r1['STMT_x_NFA_pval']):4s} "
      f"{r2['STMT_x_NFA_coef']:>10.4f}{stars(r2['STMT_x_NFA_pval']):4s} "
      f"{r3['STMT_x_NFA_coef']:>10.4f}{stars(r3['STMT_x_NFA_pval']):4s} "
      f"{r4['MP1_x_NFA_coef']:>10.4f}{stars(r4['MP1_x_NFA_pval']):4s}")
print(f"{'':30s} ({r1['STMT_x_NFA_se']:>8.4f})    ({r2['STMT_x_NFA_se']:>8.4f})    "
      f"({r3['STMT_x_NFA_se']:>8.4f})    ({r4['MP1_x_NFA_se']:>8.4f})   ")

# NFA row
print(f"{'NFA/GDP (demeaned)':30s} {r1['NFA_GDP_dm_coef']:>10.4f}{stars(r1['NFA_GDP_dm_pval']):4s} "
      f"{r2['NFA_GDP_dm_coef']:>10.4f}{stars(r2['NFA_GDP_dm_pval']):4s} "
      f"{r3['NFA_GDP_dm_coef']:>10.4f}{stars(r3['NFA_GDP_dm_pval']):4s} "
      f"{r4['NFA_GDP_dm_coef']:>10.4f}{stars(r4['NFA_GDP_dm_pval']):4s}")
print(f"{'':30s} ({r1['NFA_GDP_dm_se']:>8.4f})    ({r2['NFA_GDP_dm_se']:>8.4f})    "
      f"({r3['NFA_GDP_dm_se']:>8.4f})    ({r4['NFA_GDP_dm_se']:>8.4f})   ")

print("-" * 90)
print(f"{'Country FE':30s} {'Yes':>14s} {'Yes':>14s} {'Yes':>14s} {'Yes':>14s}")
print(f"{'Date Cluster':30s} {'Yes':>14s} {'Yes':>14s} {'No':>14s} {'Yes':>14s}")
print(f"{'Country Cluster':30s} {'No':>14s} {'Yes':>14s} {'Yes':>14s} {'No':>14s}")
print(f"{'Observations':30s} {r1['N']:>14d} {r2['N']:>14d} {r3['N']:>14d} {r4['N']:>14d}")
print(f"{'R-squared':30s} {r1['R2']:>14.4f} {r2['R2']:>14.4f} {r3['R2']:>14.4f} {r4['R2']:>14.4f}")

# ============================================================================
# STEP 7: ECONOMIC INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: Economic Interpretation")
print("=" * 80)

b1 = result_date.params['STMT']
b2 = result_date.params['STMT_x_NFA']
cov = result_date.cov

# ---- MARGINAL EFFECT TABLE AT KEY PERCENTILES ----
percentiles = [10, 25, 50, 75, 90]
nfa_pctiles = {p: panel_long['NFA_GDP'].quantile(p / 100) for p in percentiles}

# Also add actual country averages
nfa_avg = panel_long.groupby('currency')['NFA_GDP'].mean()

shock = 0.10  # 10 bps in decimal (the natural macro unit)

print(f"\nKEY COEFFICIENT: β2 (STMT × NFA/GDP) = {b2:.6f}")
print(f"  Expected sign: Positive (higher NFA → less depreciation)")
print(f"  Actual sign: {'Positive ✓' if b2 > 0 else 'Negative ✗'}")
print(f"  p-value (date-clustered): {result_date.pvalues['STMT_x_NFA']:.4f}")
print(f"  p-value (two-way):        {result_twoway.pvalues['STMT_x_NFA']:.4f}")

# Z-score interpretation
b2_z = result_z.params['STMT_x_NFA_z']
print(f"\n  Z-score specification: β2(z) = {b2_z:.4f}")
print(f"  → A 1 SD increase in NFA/GDP ({nfa_std:.1f} pp) changes the STMT")
print(f"    marginal effect by {b2_z:.4f} pp")
print(f"  → For a 10bp shock: {b2_z * shock:.4f}% difference in FX response")

print(f"\n{'─'*80}")
print(f"  TABLE: Marginal Effects at Key NFA/GDP Percentiles")
print(f"  All effects expressed as FX response to a 10bp hawkish surprise")
print(f"{'─'*80}")
print(f"  {'NFA Percentile':<18s} {'NFA/GDP':>10s} {'Marginal Eff.':>14s} {'10bp Response':>14s} {'95% CI':>24s}")
print(f"  {'':─<18s} {'':─>10s} {'':─>14s} {'':─>14s} {'':─>24s}")

me_table_rows = []
for p in percentiles:
    nfa_val = nfa_pctiles[p]
    me = b1 + b2 * (nfa_val - nfa_mean)
    resp_10bp = me * shock
    se = np.sqrt(
        cov.loc['STMT', 'STMT']
        + (nfa_val - nfa_mean) ** 2 * cov.loc['STMT_x_NFA', 'STMT_x_NFA']
        + 2 * (nfa_val - nfa_mean) * cov.loc['STMT', 'STMT_x_NFA']
    )
    ci_lo = (me - 1.96 * se) * shock
    ci_hi = (me + 1.96 * se) * shock
    print(f"  P{p:<17d} {nfa_val:>9.1f}% {me:>13.4f} {resp_10bp:>13.4f}%  [{ci_lo:>9.4f}%, {ci_hi:>9.4f}%]")
    me_table_rows.append({'percentile': p, 'NFA_GDP': nfa_val, 'marginal_effect': me,
                          'response_10bp': resp_10bp, 'ci_lower': ci_lo, 'ci_upper': ci_hi})

print(f"{'─'*80}")

# Country-specific marginal effects
print(f"\n{'─'*80}")
print(f"  TABLE: Country-Specific Marginal Effects (10bp Hawkish Surprise)")
print(f"{'─'*80}")
print(f"  {'Currency':<10s} {'Avg NFA/GDP':>12s} {'Marginal Eff.':>14s} {'10bp Response':>14s} {'Category':>14s}")
print(f"  {'':─<10s} {'':─>12s} {'':─>14s} {'':─>14s} {'':─>14s}")

for curr in nfa_avg.sort_values().index:
    nfa_val = nfa_avg[curr]
    me = b1 + b2 * (nfa_val - nfa_mean)
    resp_10bp = me * shock
    cat = 'Net debtor' if nfa_val < 0 else 'Net creditor'
    print(f"  {curr:<10s} {nfa_val:>11.1f}% {me:>13.4f} {resp_10bp:>13.4f}%  {cat:>14s}")

print(f"{'─'*80}")

# Store key values for figures
nfa_25 = nfa_pctiles[25]
nfa_75 = nfa_pctiles[75]
me_25 = b1 + b2 * (nfa_25 - nfa_mean)
me_75 = b1 + b2 * (nfa_75 - nfa_mean)
resp_debtor = me_25 * shock
resp_creditor = me_75 * shock

# Save marginal effect table
me_df = pd.DataFrame(me_table_rows)
me_df.to_csv(f'{BASE}/Output/task3_marginal_effects.csv', index=False)
print("\nSaved: Output/task3_marginal_effects.csv")

# ============================================================================
# FIGURE 10: MOTIVATION — 3.2 BETAS vs NFA
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING FIGURES")
print("=" * 80)

plt.style.use('seaborn-v0_8-whitegrid')

# Merge with betas from 3.2
comparison = betas_df[['beta']].copy()
comparison = comparison.join(nfa_avg)
comparison = comparison.dropna()

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(comparison['NFA_GDP'], comparison['beta'], s=180, alpha=0.8,
           color='steelblue', edgecolors='navy', linewidths=1.5, zorder=5)

# Country labels
for curr in comparison.index:
    offset_y = comparison.loc[curr, 'beta'] * 0.08
    if abs(offset_y) < 0.0003:
        offset_y = 0.0003
    ax.annotate(curr,
                (comparison.loc[curr, 'NFA_GDP'], comparison.loc[curr, 'beta']),
                fontsize=11, fontweight='bold', ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')

# Fitted line
slope, intercept, r_val, p_val, se_slope = stats.linregress(
    comparison['NFA_GDP'], comparison['beta'])
x_line = np.linspace(comparison['NFA_GDP'].min() - 10,
                     comparison['NFA_GDP'].max() + 10, 100)
ax.plot(x_line, slope * x_line + intercept, 'r--', alpha=0.7, linewidth=2,
        label=f'Fitted line (slope={slope:.5f}, R²={r_val**2:.2f})')

ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.4)
ax.set_xlabel('Average Net Foreign Assets (% of GDP)', fontsize=12, fontweight='bold')
ax.set_ylabel('FX Sensitivity to STMT (β from Task 3.2)', fontsize=12, fontweight='bold')
ax.set_title('Figure 10: Motivating the Panel Regression\n'
             'Country FX Sensitivity vs. Net Foreign Asset Position',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=10, loc='best', frameon=True)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure10_betas_vs_nfa.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure10_betas_vs_nfa.png")

# ---- FIGURE 10b: MP1 BETAS vs NFA (robustness scatter) ----
comparison_mp1 = mp1_betas_df[['beta']].copy()
comparison_mp1 = comparison_mp1.join(nfa_avg)
comparison_mp1 = comparison_mp1.dropna()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax_i, (comp, title_lab, surprise_lab) in enumerate([
    (comparison, 'STMT', 'STMT (Statement Surprise)'),
    (comparison_mp1, 'MP1', 'MP1 (Target Surprise)')
]):
    ax = axes[ax_i]
    ax.scatter(comp['NFA_GDP'], comp['beta'], s=160, alpha=0.8,
               color='steelblue' if ax_i == 0 else 'darkorange',
               edgecolors='navy' if ax_i == 0 else 'saddlebrown',
               linewidths=1.5, zorder=5)
    for curr in comp.index:
        ax.annotate(curr, (comp.loc[curr, 'NFA_GDP'], comp.loc[curr, 'beta']),
                    fontsize=10, fontweight='bold', ha='center', va='bottom',
                    xytext=(0, 8), textcoords='offset points')
    sl, ic, rv, pv, _ = stats.linregress(comp['NFA_GDP'], comp['beta'])
    xl = np.linspace(comp['NFA_GDP'].min() - 10, comp['NFA_GDP'].max() + 10, 100)
    ax.plot(xl, sl * xl + ic, 'r--', alpha=0.7, linewidth=2,
            label=f'Fitted (slope={sl:.5f}, R\u00b2={rv**2:.2f})')
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.4)
    ax.set_xlabel('Average NFA (% of GDP)', fontsize=11, fontweight='bold')
    ax.set_ylabel(f'FX Sensitivity to {title_lab}', fontsize=11, fontweight='bold')
    ax.set_title(f'Panel {chr(65+ax_i)}: {surprise_lab}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='best', frameon=True)
    ax.grid(alpha=0.3)

plt.suptitle('Figure 10b: Country FX Sensitivity vs. NFA\n'
             'Comparing STMT and MP1 Surprise Measures',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure10b_betas_vs_nfa_both.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure10b_betas_vs_nfa_both.png")

# ============================================================================
# FIGURE 11: MARGINAL EFFECT PLOT (KEY FIGURE)
# ============================================================================

nfa_range = np.linspace(panel_long['NFA_GDP'].min() - 5,
                        panel_long['NFA_GDP'].max() + 5, 200)

# Marginal effect: ∂(Δe)/∂STMT = β1 + β2 × (NFA - NFA_mean)
marginal_effect = b1 + b2 * (nfa_range - nfa_mean)

# Standard errors via delta method
se_me = np.sqrt(
    cov.loc['STMT', 'STMT']
    + (nfa_range - nfa_mean) ** 2 * cov.loc['STMT_x_NFA', 'STMT_x_NFA']
    + 2 * (nfa_range - nfa_mean) * cov.loc['STMT', 'STMT_x_NFA']
)
ci_lower = marginal_effect - 1.96 * se_me
ci_upper = marginal_effect + 1.96 * se_me

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(nfa_range, marginal_effect, 'b-', linewidth=2.5, label='Marginal Effect')
ax.fill_between(nfa_range, ci_lower, ci_upper, alpha=0.2, color='blue',
                label='95% Confidence Interval')

# Zero line
ax.axhline(0, color='black', linestyle='--', linewidth=1)

# Mark actual country average NFA positions
country_me = b1 + b2 * (nfa_avg - nfa_mean)
colors_map = {
    'AUD': '#e41a1c', 'MXN': '#ff7f00', 'CAD': '#984ea3',
    'GBP': '#377eb8', 'EUR': '#4daf4a', 'NOK': '#a65628',
    'JPY': '#f781bf', 'CHF': '#999999'
}

for curr in nfa_avg.index:
    if curr in country_me.index:
        color = colors_map.get(curr, 'gray')
        ax.scatter(nfa_avg[curr], country_me[curr], s=120, color=color,
                   edgecolors='black', linewidths=1, zorder=5)
        ax.annotate(curr, (nfa_avg[curr], country_me[curr]),
                    fontsize=10, fontweight='bold', ha='center',
                    xytext=(0, 10), textcoords='offset points')

ax.set_xlabel('Net Foreign Assets (% of GDP)', fontsize=12, fontweight='bold')
ax.set_ylabel('Marginal Effect of STMT on FX (%)', fontsize=12, fontweight='bold')
ax.set_title('Figure 11: How Currency Response to U.S. Monetary Policy\n'
             'Varies with Net Foreign Asset Position',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=10, loc='upper left', frameon=True)
ax.grid(alpha=0.3)

# Zoom y-axis to actual data range (avoid extending to 400)
all_y_vals = np.concatenate([marginal_effect, ci_lower, ci_upper,
                             country_me.values])
y_min, y_max = np.min(all_y_vals), np.max(all_y_vals)
y_pad = (y_max - y_min) * 0.3
ax.set_ylim(y_min - y_pad, y_max + y_pad)

# Zoom x-axis to actual NFA data range with padding
x_min, x_max = nfa_avg.min(), nfa_avg.max()
x_pad = (x_max - x_min) * 0.25
ax.set_xlim(x_min - x_pad, x_max + x_pad)

# Annotation — larger text, more offset for visibility
ax.annotate('Debtor countries\n(more exposed)',
            xy=(nfa_avg.min(), country_me[nfa_avg.idxmin()]),
            xytext=(-30, -40), textcoords='offset points',
            fontsize=11, fontstyle='italic', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            color='red')

ax.annotate('Creditor countries\n(less exposed)',
            xy=(nfa_avg.max(), country_me[nfa_avg.idxmax()]),
            xytext=(-60, 30), textcoords='offset points',
            fontsize=11, fontstyle='italic', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            color='green')

plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure11_marginal_effects.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure11_marginal_effects.png")

# ============================================================================
# FIGURE 12: PREDICTED RESPONSES — DEBTOR vs CREDITOR
# ============================================================================

# Calculate predicted responses at 25th and 75th percentile NFA
shock_size = 0.10  # 10 bps

# Standard errors (delta method) for predicted responses
var_debtor = (cov.loc['STMT', 'STMT']
              + (nfa_25 - nfa_mean) ** 2 * cov.loc['STMT_x_NFA', 'STMT_x_NFA']
              + 2 * (nfa_25 - nfa_mean) * cov.loc['STMT', 'STMT_x_NFA']) * shock_size ** 2
se_debtor = np.sqrt(abs(var_debtor))

var_creditor = (cov.loc['STMT', 'STMT']
                + (nfa_75 - nfa_mean) ** 2 * cov.loc['STMT_x_NFA', 'STMT_x_NFA']
                + 2 * (nfa_75 - nfa_mean) * cov.loc['STMT', 'STMT_x_NFA']) * shock_size ** 2
se_creditor = np.sqrt(abs(var_creditor))

fig, ax = plt.subplots(figsize=(8, 6))

categories = [f'Debtor\n(25th %ile NFA\n= {nfa_25:.0f}% GDP)',
              f'Creditor\n(75th %ile NFA\n= {nfa_75:.0f}% GDP)']
responses = [resp_debtor, resp_creditor]
errors = [1.96 * se_debtor, 1.96 * se_creditor]

bars = ax.bar(categories, responses, yerr=errors,
              capsize=8, alpha=0.75, width=0.5,
              color=['#d62728', '#2ca02c'],
              edgecolor=['darkred', 'darkgreen'], linewidth=1.5,
              error_kw={'linewidth': 2, 'ecolor': 'black'})

ax.axhline(0, color='black', linestyle='-', linewidth=1)
ax.set_ylabel('FX Response to 10bp Hawkish Surprise (%)', fontsize=11, fontweight='bold')
ax.set_title('Figure 12: Predicted Currency Response\nby Net Foreign Asset Position',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='y', alpha=0.3)

# Add values on bars — offset right to avoid CI line overlap
for bar, val, err in zip(bars, responses, errors):
    height = bar.get_height()
    sign = '+' if val > 0 else ''
    ax.text(bar.get_x() + bar.get_width() * 0.85, height + 0.003,
            f'{sign}{val:.4f}%', ha='left', va='bottom',
            fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{BASE}/Output/figure12_predicted_responses.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure12_predicted_responses.png")

# ============================================================================
# STEP 8: LATEX TABLE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 8: Generate LaTeX Table")
print("=" * 80)

def fmt_coef(val, pval, dec=4):
    s = f"{val:.{dec}f}"
    s += stars(pval)
    return s

latex = r"""\begin{table}[htbp]
\centering
\caption{Exchange Rate Responses and Net Foreign Assets}
\label{tab:nfa_panel}
\begin{tabular}{lcccc}
\hline\hline
 & (1) & (2) & (3) & (4) \\
 & Main & Two-Way & Country & MP1 \\
 & (Date Cl.) & (Two-Way Cl.) & (Country Cl.) & (Date Cl.) \\
\hline
"""

# STMT
latex += f"STMT & {fmt_coef(r1['STMT_coef'], r1['STMT_pval'])} & "
latex += f"{fmt_coef(r2['STMT_coef'], r2['STMT_pval'])} & "
latex += f"{fmt_coef(r3['STMT_coef'], r3['STMT_pval'])} & \\\\\n"
latex += f" & ({r1['STMT_se']:.4f}) & ({r2['STMT_se']:.4f}) & ({r3['STMT_se']:.4f}) & \\\\\n"

# MP1
latex += f"MP1 & & & & {fmt_coef(r4['MP1_coef'], r4['MP1_pval'])} \\\\\n"
latex += f" & & & & ({r4['MP1_se']:.4f}) \\\\\n"

# Interaction
latex += f"Surprise $\\times$ NFA/GDP & {fmt_coef(r1['STMT_x_NFA_coef'], r1['STMT_x_NFA_pval'])} & "
latex += f"{fmt_coef(r2['STMT_x_NFA_coef'], r2['STMT_x_NFA_pval'])} & "
latex += f"{fmt_coef(r3['STMT_x_NFA_coef'], r3['STMT_x_NFA_pval'])} & "
latex += f"{fmt_coef(r4['MP1_x_NFA_coef'], r4['MP1_x_NFA_pval'])} \\\\\n"
latex += f" & ({r1['STMT_x_NFA_se']:.4f}) & ({r2['STMT_x_NFA_se']:.4f}) & "
latex += f"({r3['STMT_x_NFA_se']:.4f}) & ({r4['MP1_x_NFA_se']:.4f}) \\\\\n"

# NFA
latex += f"NFA/GDP & {fmt_coef(r1['NFA_GDP_dm_coef'], r1['NFA_GDP_dm_pval'])} & "
latex += f"{fmt_coef(r2['NFA_GDP_dm_coef'], r2['NFA_GDP_dm_pval'])} & "
latex += f"{fmt_coef(r3['NFA_GDP_dm_coef'], r3['NFA_GDP_dm_pval'])} & "
latex += f"{fmt_coef(r4['NFA_GDP_dm_coef'], r4['NFA_GDP_dm_pval'])} \\\\\n"
latex += f" & ({r1['NFA_GDP_dm_se']:.4f}) & ({r2['NFA_GDP_dm_se']:.4f}) & "
latex += f"({r3['NFA_GDP_dm_se']:.4f}) & ({r4['NFA_GDP_dm_se']:.4f}) \\\\\n"

latex += r"""\hline
Country FE & Yes & Yes & Yes & Yes \\
Date Cluster & Yes & Yes & No & Yes \\
Country Cluster & No & Yes & Yes & No \\
"""

latex += f"Observations & {r1['N']} & {r2['N']} & {r3['N']} & {r4['N']} \\\\\n"
latex += f"$R^2$ & {r1['R2']:.4f} & {r2['R2']:.4f} & {r3['R2']:.4f} & {r4['R2']:.4f} \\\\\n"

latex += r"""\hline\hline
\end{tabular}
\begin{tablenotes}
\small
\item \textit{Notes:} Panel regression of daily FX log changes on FOMC event dates.
NFA/GDP is from Lane \& Milesi-Ferretti (EWN, 2024 update), lagged one year.
NFA/GDP is demeaned so $\beta_1$ represents the effect at average NFA.
Column (4) uses MP1 (target surprise) instead of STMT (statement surprise) as robustness.
*** $p<0.01$, ** $p<0.05$, * $p<0.10$.
\end{tablenotes}
\end{table}
"""

with open(f'{BASE}/Output/table3_nfa_panel.tex', 'w') as f:
    f.write(latex)
print("Saved: Output/table3_nfa_panel.tex")

# Also save results as CSV for reference
results_csv = pd.DataFrame({
    'Specification': ['(1) Date Cluster', '(2) Two-Way', '(3) Country Cluster', '(4) MP1 Date Cluster'],
    'Surprise_coef': [r1['STMT_coef'], r2['STMT_coef'], r3['STMT_coef'], r4['MP1_coef']],
    'Surprise_se': [r1['STMT_se'], r2['STMT_se'], r3['STMT_se'], r4['MP1_se']],
    'Interaction_coef': [r1['STMT_x_NFA_coef'], r2['STMT_x_NFA_coef'], r3['STMT_x_NFA_coef'], r4['MP1_x_NFA_coef']],
    'Interaction_se': [r1['STMT_x_NFA_se'], r2['STMT_x_NFA_se'], r3['STMT_x_NFA_se'], r4['MP1_x_NFA_se']],
    'NFA_coef': [r1['NFA_GDP_dm_coef'], r2['NFA_GDP_dm_coef'], r3['NFA_GDP_dm_coef'], r4['NFA_GDP_dm_coef']],
    'NFA_se': [r1['NFA_GDP_dm_se'], r2['NFA_GDP_dm_se'], r3['NFA_GDP_dm_se'], r4['NFA_GDP_dm_se']],
    'N': [r1['N'], r2['N'], r3['N'], r4['N']],
    'R2': [r1['R2'], r2['R2'], r3['R2'], r4['R2']]
})
results_csv.to_csv(f'{BASE}/Output/task3_nfa_panel_results.csv', index=False)
print("Saved: Output/task3_nfa_panel_results.csv")

# Save the panel dataset for reproducibility
panel_long.to_csv(f'{BASE}/Output/task3_panel_data.csv', index=False)
print("Saved: Output/task3_panel_data.csv")

# ============================================================================
# STEP 9: Z-SCORE REGRESSION TABLE (ADDITIONAL ROBUSTNESS)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 9: Z-Score Standardized NFA Robustness")
print("=" * 80)

r5 = extract_results(result_z, ['STMT', 'STMT_x_NFA_z', 'NFA_GDP_z'])
print(f"\n  STMT (β1):            {r5['STMT_coef']:.4f}  (SE: {r5['STMT_se']:.4f})")
print(f"  STMT × NFA/GDP (z):   {r5['STMT_x_NFA_z_coef']:.4f}  (SE: {r5['STMT_x_NFA_z_se']:.4f})")
print(f"  NFA/GDP (z):          {r5['NFA_GDP_z_coef']:.4f}  (SE: {r5['NFA_GDP_z_se']:.4f})")
print(f"\n  Interpretation: A 1 standard deviation increase in NFA/GDP ({nfa_std:.1f} pp)")
print(f"  changes the FX sensitivity to STMT by {r5['STMT_x_NFA_z_coef']:.4f} pp.")
print(f"  For a 10bp hawkish surprise: {r5['STMT_x_NFA_z_coef'] * shock:.4f}% difference in FX response.")

# ============================================================================
# SUMMARY WITH STRENGTHENED INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3.3 COMPLETE!")
print("=" * 80)

pval_main = result_date.pvalues['STMT_x_NFA']
pval_mp1 = result_mp1.pvalues['MP1_x_NFA']
sig_label = 'statistically significant' if pval_main < 0.05 else 'not statistically significant at the 5% level'

print(f"""
OUTPUT FILES:
  Tables:
    • Output/table3_nfa_panel.tex             (LaTeX regression table)
    • Output/task3_nfa_panel_results.csv      (regression results CSV)
    • Output/task3_marginal_effects.csv       (marginal effects at percentiles)
  
  Figures:
    • Output/figure10_betas_vs_nfa.png        (Motivation: 3.2 STMT betas vs NFA)
    • Output/figure10b_betas_vs_nfa_both.png  (STMT & MP1 betas vs NFA)
    • Output/figure11_marginal_effects.png    (Marginal effect across NFA)
    • Output/figure12_predicted_responses.png (Debtor vs creditor bar chart)
  
  Data:
    • Output/task2_country_betas.csv          (STMT FX betas from 3.2)
    • Output/task2_country_betas_mp1.csv      (MP1 FX betas from 3.2)
    • Output/task3_panel_data.csv             (Panel dataset)

══════════════════════════════════════════════════════════════════════════════════
KEY RESULTS
══════════════════════════════════════════════════════════════════════════════════

  β2 (STMT × NFA/GDP) = {b2:.6f}  [{sig_label}]
  Sign: {'Positive (consistent with Antolín-Díaz et al. 2023)' if b2 > 0 else 'Negative (opposite prediction)'}
  p-value (date-clustered):  {pval_main:.4f}
  p-value (two-way cluster): {result_twoway.pvalues['STMT_x_NFA']:.4f}
  
  Z-score specification: β2(z) = {b2_z:.4f}
    → 1 SD of NFA/GDP = {nfa_std:.1f} pp
    → For a 10bp shock: {b2_z * shock:.4f}% difference per 1 SD

  Economic magnitude (10bp hawkish surprise):
    Debtor    (P25: NFA = {nfa_25:.0f}% GDP): {resp_debtor:+.4f}% FX change
    Creditor  (P75: NFA = {nfa_75:.0f}% GDP): {resp_creditor:+.4f}% FX change
    Difference: {resp_creditor - resp_debtor:+.4f}%

  Robustness:
    MP1 interaction β2 = {result_mp1.params['MP1_x_NFA']:.6f} (p = {pval_mp1:.4f})
    {'Marginally significant with MP1 — stronger for target rate surprises' if pval_mp1 < 0.10 else 'Also insignificant with MP1'}

══════════════════════════════════════════════════════════════════════════════════
INTERPRETATION & DISCUSSION
══════════════════════════════════════════════════════════════════════════════════

  The interaction coefficient β2 is positive, directionally consistent with the
  hypothesis that creditor countries experience smaller currency depreciations
  in response to hawkish Fed surprises (Antolín-Díaz et al. 2023). However,
  the coefficient is {sig_label} with date-clustered 
  standard errors (p = {pval_main:.3f}).

  A 10 basis point hawkish surprise leads to a {resp_debtor:.4f}% USD appreciation
  against a country at the 25th percentile of NFA (debtor), compared to
  {resp_creditor:.4f}% for a country at the 75th percentile (creditor).

  POSSIBLE EXPLANATIONS FOR IMPRECISION:

  1. High-frequency noise: Daily FX data contains substantial non-monetary
     noise. The R² of ~{r1['R2']:.3f} confirms that FOMC surprises explain very
     little of daily FX variation. Intraday data (as in Antolín-Díaz et al.)
     would improve signal-to-noise.

  2. Information channel: FOMC statements may simultaneously convey
     information about the economic outlook, offsetting the pure rate
     channel. This dual signal dilutes the clean mapping from surprises
     to FX movements.

  3. NFA may not be the right margin: Gross foreign asset and liability
     positions, or the currency denomination of external debt ("original
     sin"), may matter more than net positions. A country with large gross
     positions but NFA ≈ 0 is still highly exposed.

  4. Time-varying exposure: NFA-based exposure may have changed structurally
     (e.g., post-GFC balance sheet expansion, post-2020 reserve accumulation),
     creating parameter instability that a single β2 cannot capture.

  5. Small cross-section: With only 8 currencies, the cross-sectional
     variation in NFA may be insufficient to identify β2 precisely.
     This is a fundamental limitation of the G10-based sample.

  Despite the lack of statistical significance, the economic direction is
  consistent with theory, and the MP1 specification provides marginal
  supporting evidence (p = {pval_mp1:.3f}).

══════════════════════════════════════════════════════════════════════════════════
NARRATIVE ARC
══════════════════════════════════════════════════════════════════════════════════

  Section 3.1 established STMT as a valid monetary policy shock measure.
  Section 3.2 documented heterogeneous FX responses across countries.
  Section 3.3 tests whether NFA/GDP explains this heterogeneity.
  
  Identification: Cross-country differences in predetermined balance sheet
  positions interacting with exogenous high-frequency U.S. monetary shocks.
""")
