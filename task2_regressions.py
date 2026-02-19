"""
Task 2: Asset Price Response Regressions
=========================================
LEAN VERSION - Core results only

Using the STMT high-frequency surprise measure constructed in Task 1,
estimate responses of Treasuries, breakeven inflation, and exchange rates
to U.S. monetary policy surprises.

Methodology:
- OLS with robust (HC1) standard errors
- FOMC days only (event-study design)
- One regression per asset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

# Create output directory
os.makedirs('/Users/trentonobannontrenton/MIT Coding Challenge/Output', exist_ok=True)

print("="*80)
print("TASK 2: ASSET PRICE RESPONSES TO MONETARY POLICY SURPRISES")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================

merged = pd.read_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/merged_fomc_data.csv')
merged['Date'] = pd.to_datetime(merged['Date'])

print(f"\nLoaded: {len(merged)} FOMC events")
print(f"Date range: {merged['Date'].min().strftime('%Y-%m-%d')} to {merged['Date'].max().strftime('%Y-%m-%d')}")

# ============================================================================
# STEP 1: VERIFY STMT SCALING
# ============================================================================

print("\n" + "="*80)
print("STEP 1: Verify STMT Scaling")
print("="*80)

print(f"\nSTMT summary:")
print(f"  Mean: {merged['STMT'].mean():.6f}")
print(f"  Std:  {merged['STMT'].std():.6f}")
print(f"  Min:  {merged['STMT'].min():.6f}")
print(f"  Max:  {merged['STMT'].max():.6f}")

print(f"""
INTERPRETATION:
  STMT is in decimal form (std ≈ 0.037)
  A 1 standard deviation surprise = 0.037
  We scale STMT by 100 so coefficients are interpretable as:
  "β = bps change per 1 bps surprise"
""")

# Scale STMT to basis points for interpretability
merged['STMT_bps'] = merged['STMT'] * 100

# ============================================================================
# STEP 2: REGRESSION FUNCTION
# ============================================================================

def run_regression(y, X, asset_name):
    """
    Run OLS regression with robust standard errors (HC1)
    
    Model: Δy_t = α + β * STMT_t + ε_t
    
    Returns dict with beta, se, tstat, pval, N, R2
    """
    # Drop missing values
    valid = pd.DataFrame({'y': y, 'X': X}).dropna()
    
    if len(valid) < 30:
        return {
            'asset': asset_name, 'beta': np.nan, 'se': np.nan, 
            'tstat': np.nan, 'pval': np.nan, 'const': np.nan,
            'N': len(valid), 'R2': np.nan
        }
    
    # Manual OLS: y = α + β*X + ε
    n = len(valid)
    X_val = valid['X'].values
    y_val = valid['y'].values
    
    # Design matrix with constant
    X_mat = np.column_stack([np.ones(n), X_val])
    
    # OLS: β = (X'X)^{-1} X'y
    XtX_inv = np.linalg.inv(X_mat.T @ X_mat)
    beta_hat = XtX_inv @ X_mat.T @ y_val
    
    # Residuals and R-squared
    y_pred = X_mat @ beta_hat
    resid = y_val - y_pred
    ss_res = np.sum(resid**2)
    ss_tot = np.sum((y_val - np.mean(y_val))**2)
    r2 = 1 - ss_res / ss_tot
    
    # Robust standard errors (HC1)
    k = 2
    e2 = resid**2
    meat = X_mat.T @ np.diag(e2) @ X_mat
    robust_var = XtX_inv @ meat @ XtX_inv * (n / (n - k))
    robust_se = np.sqrt(np.diag(robust_var))
    
    # t-statistics and p-values
    t_stats = beta_hat / robust_se
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n-k))
    
    return {
        'asset': asset_name,
        'beta': beta_hat[1],
        'se': robust_se[1],
        'tstat': t_stats[1],
        'pval': p_vals[1],
        'const': beta_hat[0],
        'N': n,
        'R2': r2
    }

# ============================================================================
# STEP 3: RUN ALL REGRESSIONS
# ============================================================================

results = []

# Panel A: Treasury Yields
print("\n" + "="*80)
print("PANEL A: TREASURY YIELDS (Δ in bps)")
print("="*80)
print(f"{'Asset':<12} {'β':>8} {'SE':>8} {'t-stat':>8} {'N':>6} {'R²':>8}")
print("-"*52)

for mat in ['2Y', '5Y', '10Y']:
    col = f'd_UST_{mat}'
    result = run_regression(merged[col], merged['STMT_bps'], f'UST {mat}')
    results.append(result)
    print(f"{result['asset']:<12} {result['beta']:>8.3f} {result['se']:>8.3f} "
          f"{result['tstat']:>8.2f} {result['N']:>6} {result['R2']:>8.3f}")

# Panel B: Breakeven Inflation
print("\n" + "="*80)
print("PANEL B: BREAKEVEN INFLATION (Δ in bps)")
print("="*80)
print(f"{'Asset':<12} {'β':>8} {'SE':>8} {'t-stat':>8} {'N':>6} {'R²':>8}")
print("-"*52)

for mat in ['5Y', '10Y']:
    col = f'd_BE_{mat}'
    result = run_regression(merged[col], merged['STMT_bps'], f'BE {mat}')
    results.append(result)
    print(f"{result['asset']:<12} {result['beta']:>8.3f} {result['se']:>8.3f} "
          f"{result['tstat']:>8.2f} {result['N']:>6} {result['R2']:>8.3f}")

# Panel C: Exchange Rates
print("\n" + "="*80)
print("PANEL C: EXCHANGE RATES (Δ in % log returns)")
print("="*80)
print(f"{'Currency':<12} {'β':>8} {'SE':>8} {'t-stat':>8} {'N':>6} {'R²':>8}")
print("-"*52)

fx_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'MXN', 'NOK']
for curr in fx_currencies:
    col = f'd_{curr}'
    if col in merged.columns:
        result = run_regression(merged[col], merged['STMT_bps'], curr)
        results.append(result)
        print(f"{result['asset']:<12} {result['beta']:>8.4f} {result['se']:>8.4f} "
              f"{result['tstat']:>8.2f} {result['N']:>6} {result['R2']:>8.3f}")

# ============================================================================
# STEP 4: CREATE RESULTS DATAFRAME
# ============================================================================

results_df = pd.DataFrame(results)

# Add metadata
def classify_asset(asset):
    if 'UST' in asset:
        return 'Treasury'
    elif 'BE' in asset:
        return 'Breakeven'
    return 'FX'

results_df['asset_class'] = results_df['asset'].apply(classify_asset)

# Add significance stars
def get_stars(pval):
    if pd.isna(pval): return ''
    if pval < 0.01: return '***'
    if pval < 0.05: return '**'
    if pval < 0.1: return '*'
    return ''

results_df['stars'] = results_df['pval'].apply(get_stars)

# Save
results_df.to_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/task2_regression_results.csv', 
                  index=False)
print("\n\nSaved: Output/task2_regression_results.csv")

# ============================================================================
# STEP 5: CREATE LATEX TABLE
# ============================================================================

def create_latex_table(df):
    latex = []
    latex.append("\\begin{table}[htbp]")
    latex.append("\\centering")
    latex.append("\\caption{Asset Price Responses to Monetary Policy Surprises}")
    latex.append("\\label{tab:responses}")
    latex.append("\\begin{tabular}{lcccccc}")
    latex.append("\\hline\\hline")
    latex.append(" & $\\hat{\\beta}$ & Robust SE & $t$-stat & $N$ & $R^2$ \\\\")
    latex.append("\\hline")
    
    for panel, title in [('Treasury', 'Panel A: Treasury Yields (bps)'),
                         ('Breakeven', 'Panel B: Breakeven Inflation (bps)'),
                         ('FX', 'Panel C: Exchange Rates (\\% log return)')]:
        latex.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{{title}}}}} \\\\[2pt]")
        subset = df[df['asset_class'] == panel]
        for _, row in subset.iterrows():
            fmt = '.3f' if panel != 'FX' else '.4f'
            latex.append(f"\\quad {row['asset']} & {row['beta']:{fmt}}{row['stars']} & "
                        f"({row['se']:{fmt}}) & {row['tstat']:.2f} & {row['N']} & {row['R2']:.3f} \\\\")
        latex.append("\\\\")
    
    latex.append("\\hline")
    latex.append("\\multicolumn{6}{p{11cm}}{\\footnotesize \\textit{Notes:} "
                "Robust (HC1) standard errors in parentheses. "
                "STMT is expressed in basis points; $\\beta$ represents the asset response to a 1 bp statement surprise. "
                "Exchange rate responses are small and imprecisely estimated in daily data. "
                "Sample: FOMC announcement days, 1994--2026. "
                "*** $p<0.01$, ** $p<0.05$, * $p<0.10$.} \\\\")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")
    return "\n".join(latex)

latex_table = create_latex_table(results_df)
with open('/Users/trentonobannontrenton/MIT Coding Challenge/Output/table2_regression_results.tex', 'w') as f:
    f.write(latex_table)
print("Saved: Output/table2_regression_results.tex")

# ============================================================================
# STEP 6: INTERPRETATION
# ============================================================================

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

tsy = results_df[results_df['asset_class'] == 'Treasury']
be = results_df[results_df['asset_class'] == 'Breakeven']
fx = results_df[results_df['asset_class'] == 'FX']

print(f"""
📊 TREASURY YIELDS:
   • 2Y: β = {tsy.iloc[0]['beta']:.3f} → 1 bps hawkish surprise raises 2Y yield by {tsy.iloc[0]['beta']:.2f} bps
   • 5Y: β = {tsy.iloc[1]['beta']:.3f}
   • 10Y: β = {tsy.iloc[2]['beta']:.3f}
   → Response DECLINES with maturity (Fed controls short end more)
   → High R² ({tsy['R2'].mean():.2f} avg) validates STMT as genuine policy shock

📈 BREAKEVEN INFLATION:
   • 5Y: β = {be.iloc[0]['beta']:.3f}
   • 10Y: β = {be.iloc[1]['beta']:.3f}
   → Smaller response than nominal yields
   → Most yield response comes through REAL rates, not inflation expectations

💱 EXCHANGE RATES:
   • Range: β = {fx['beta'].min():.4f} to {fx['beta'].max():.4f}
   • Strongest: {fx.loc[fx['beta'].idxmax(), 'asset']} (β = {fx['beta'].max():.4f})
   • Weakest: {fx.loc[fx['beta'].idxmin(), 'asset']} (β = {fx['beta'].min():.4f})
   → SUBSTANTIAL HETEROGENEITY across currencies
   → Low R² ({fx['R2'].mean():.3f} avg) → other factors drive FX beyond policy

🎯 KEY FINDING FOR TASK 3:
   Exchange rate responses vary substantially across countries.
   This heterogeneity motivates Task 3: can NFA/GDP explain the variation?
""")

# ============================================================================
# FIGURE 7: TERM STRUCTURE OF INTEREST RATE RESPONSES
# ============================================================================

print("\n" + "="*80)
print("GENERATING FIGURES")
print("="*80)

fig, ax = plt.subplots(figsize=(10, 6))

# Treasury data
treasury = results_df[results_df['asset_class'] == 'Treasury'].copy()
treasury['maturity'] = [2, 5, 10]
treasury = treasury.sort_values('maturity')

# Breakeven data
breakeven = results_df[results_df['asset_class'] == 'Breakeven'].copy()
breakeven['maturity'] = [5, 10]
breakeven = breakeven.sort_values('maturity')

# Plot Treasury yields
ax.errorbar(treasury['maturity'], treasury['beta'], 
            yerr=1.96*treasury['se'],
            fmt='o-', linewidth=2.5, markersize=12, capsize=6, capthick=2,
            color='steelblue', label='Nominal Treasury Yields')

# Plot Breakevens
ax.errorbar(breakeven['maturity'], breakeven['beta'], 
            yerr=1.96*breakeven['se'],
            fmt='s--', linewidth=2.5, markersize=12, capsize=6, capthick=2,
            color='crimson', label='Breakeven Inflation')

ax.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
ax.set_xlabel('Maturity (years)', fontsize=13, fontweight='bold')
ax.set_ylabel('Response Coefficient (β)\nbps per 1 bps surprise', fontsize=12)
ax.set_title('Figure 7: Term Structure of Interest Rate Responses\nto Monetary Policy Surprises',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11, loc='upper right', frameon=True)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xlim(0, 12)
ax.set_xticks([2, 5, 10])

# Annotate key finding
ax.annotate('Short rates respond\nmore than long rates', 
            xy=(2, treasury.iloc[0]['beta']), 
            xytext=(4, treasury.iloc[0]['beta'] + 0.15),
            fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure7_term_structure.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure7_term_structure.png")

# ============================================================================
# FIGURE 8: FX RESPONSE HETEROGENEITY
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 7))

# Sort by beta
fx_sorted = fx.sort_values('beta', ascending=True)
y_pos = np.arange(len(fx_sorted))

# Color by magnitude (gradient)
colors = plt.cm.Blues(np.linspace(0.35, 0.85, len(fx_sorted)))

# Horizontal bar plot with error bars
bars = ax.barh(y_pos, fx_sorted['beta'], xerr=1.96*fx_sorted['se'],
               height=0.65, color=colors, capsize=5,
               error_kw={'linewidth': 1.5, 'ecolor': 'black'},
               label='Response coefficient (β)')

ax.axvline(0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(fx_sorted['asset'], fontsize=12, fontweight='bold')
ax.set_xlabel('Response Coefficient (β)\n% depreciation per 1 bps hawkish surprise', fontsize=11)
ax.set_title('Figure 8: Exchange Rate Responses to U.S. Monetary Policy Surprises\n'
             'Substantial Cross-Country Heterogeneity → Motivates Task 3',
             fontsize=13, fontweight='bold', pad=15)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Add value labels - RAISED ABOVE BARS
for i, (_, row) in enumerate(fx_sorted.iterrows()):
    sign = '+' if row['beta'] > 0 else ''
    # Position text above the bar (y offset of 0.16)
    ax.text(row['beta'], i + 0.16, 
            f"{sign}{row['beta']:.3f}{row['stars']}", 
            va='bottom', ha='center', fontsize=9, fontweight='bold')

# Add legend for error bars
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='black', linewidth=1.5, label='95% Confidence Interval')
]
ax.legend(handles=legend_elements, fontsize=10, loc='lower right', frameon=True)

# Add note about interpretation
ax.annotate('Positive β → USD appreciates\n(foreign currency depreciates)', 
            xy=(0.012, 6.5), fontsize=9, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure8_fx_heterogeneity.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure8_fx_heterogeneity.png")

# ============================================================================
# FIGURE 9: COEFFICIENT PLOT (ALL ASSETS)
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Interest Rates (Treasury + Breakeven)
ax = axes[0]
ir_results = results_df[results_df['asset_class'].isin(['Treasury', 'Breakeven'])].copy()
ir_results = ir_results.sort_values('beta', ascending=True)
y_pos = np.arange(len(ir_results))

colors = ['steelblue' if 'UST' in a else 'crimson' for a in ir_results['asset']]
ax.barh(y_pos, ir_results['beta'], xerr=1.96*ir_results['se'],
        color=colors, alpha=0.7, capsize=4, height=0.6,
        error_kw={'linewidth': 1.5, 'ecolor': 'black'})
ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(ir_results['asset'], fontsize=11)
ax.set_xlabel('Response Coefficient (β)', fontsize=11)
ax.set_title('Panel A: Interest Rates\n(bps per 1 bps surprise)', fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='steelblue', alpha=0.7, label='Treasury Yields'),
    Patch(facecolor='crimson', alpha=0.7, label='Breakeven Inflation'),
    Line2D([0], [0], color='black', linewidth=1.5, label='95% CI')
]
ax.legend(handles=legend_elements, fontsize=9, loc='lower right')

# Panel B: Exchange Rates
ax = axes[1]
fx_results = results_df[results_df['asset_class'] == 'FX'].copy()
fx_results = fx_results.sort_values('beta', ascending=True)
y_pos = np.arange(len(fx_results))

ax.barh(y_pos, fx_results['beta'], xerr=1.96*fx_results['se'],
        color='navy', alpha=0.7, capsize=4, height=0.6,
        error_kw={'linewidth': 1.5, 'ecolor': 'black'})
ax.axvline(0, color='red', linestyle='--', linewidth=1.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(fx_results['asset'], fontsize=11)
ax.set_xlabel('Response Coefficient (β)', fontsize=11)
ax.set_title('Panel B: Exchange Rates\n(% per 1 bps surprise)', fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add legend
legend_elements = [
    Line2D([0], [0], color='black', linewidth=1.5, label='95% CI')
]
ax.legend(handles=legend_elements, fontsize=9, loc='lower right')

plt.suptitle('Figure 9: Coefficient Plot - All Asset Responses', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure9_coefficient_plot.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: Output/figure9_coefficient_plot.png")

# ============================================================================
# STEP 7: SAVE COUNTRY-SPECIFIC FX BETAS (for Task 3.3)
# ============================================================================

print("\n" + "="*80)
print("SAVING COUNTRY-SPECIFIC FX BETAS FOR TASK 3.3")
print("="*80)

fx_betas = results_df[results_df['asset_class'] == 'FX'][['asset', 'beta', 'se', 'tstat', 'pval', 'N', 'R2']].copy()
fx_betas = fx_betas.rename(columns={'asset': 'currency'})
fx_betas = fx_betas.set_index('currency')
fx_betas.to_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/task2_country_betas.csv')
print("Saved: Output/task2_country_betas.csv")
print(fx_betas.to_string())

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TASK 2 COMPLETE!")
print("="*80)
print(f"""
OUTPUT FILES:
  • Output/task2_regression_results.csv
  • Output/table2_regression_results.tex  
  • Output/figure7_term_structure.png
  • Output/figure8_fx_heterogeneity.png
  • Output/figure9_coefficient_plot.png

KEY RESULTS:
  • Treasury yields: Strong positive response, declining with maturity
  • Breakevens: Smaller response → real rates drive transmission
  • Exchange rates: Magnitudes vary substantially across currencies

BRIDGE TO TASK 3:
  "The substantial heterogeneity in exchange rate responses raises a natural
  question: what determines why some currencies respond more to U.S. monetary
  shocks? I test whether countries' Net Foreign Asset positions can explain
  this cross-sectional variation in Task 3."
""")
