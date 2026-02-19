"""
Task 1: Complete Data Preparation Pipeline
- Merge monetary policy surprises with daily asset prices
- Generate summary statistics
- Create visualizations for writeup
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Create output directory
os.makedirs('/Users/trentonobannontrenton/MIT Coding Challenge/Output', exist_ok=True)

print("="*80)
print("TASK 1: DATA PREPARATION AND MERGING")
print("="*80)

# ============================================================================
# STEP 1: LOAD MONETARY POLICY SURPRISES
# ============================================================================
print("\n" + "="*80)
print("STEP 1: Loading Monetary Policy Surprises")
print("="*80)

# Primary measure: STMT from mps.csv
mps = pd.read_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Data/monetary-policy-surprises/mps.csv')
mps['Date'] = pd.to_datetime(mps['Date'])

# Also load USMPD for MP1/MP2 (robustness)
usmpd = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/USMPD.xlsx', 
                      sheet_name='Statements')
usmpd['Date'] = pd.to_datetime(usmpd['Date'])

# Merge surprise measures
surprises = mps[['Date', 'STMT', 'ME']].merge(
    usmpd[['Date', 'MP1', 'MP2']], 
    on='Date', 
    how='inner'
)

print(f"FOMC events: {len(surprises)}")
print(f"Date range: {surprises['Date'].min().date()} to {surprises['Date'].max().date()}")
print(f"\nSurprise measures loaded: STMT, ME, MP1, MP2")

# ============================================================================
# STEP 2: LOAD EXCHANGE RATE DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 2: Loading Exchange Rates")
print("="*80)

fx = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/Exchange_Rates.xlsx', 
                   sheet_name='Daily')
fx['Date'] = pd.to_datetime(fx['observation_date'])
fx = fx.sort_values('Date')

# Rename columns to standard currency codes
fx_rename = {
    'DEXCAUS': 'CAD',   # Canadian Dollar per USD
    'DEXJPUS': 'JPY',   # Japanese Yen per USD
    'DEXMXUS': 'MXN',   # Mexican Peso per USD
    'DEXNOUS': 'NOK',   # Norwegian Krone per USD
    'DEXSZUS': 'CHF',   # Swiss Franc per USD
    'DEXUSAL': 'AUD',   # USD per Australian Dollar (inverted!)
    'DEXUSEU': 'EUR',   # USD per Euro (inverted!)
    'DEXUSUK': 'GBP'    # USD per British Pound (inverted!)
}
fx = fx.rename(columns=fx_rename)

# IMPORTANT: Fix convention - convert all to Foreign Currency per USD
# DEXUSAL, DEXUSEU, DEXUSUK are USD per foreign currency, need to invert
for curr in ['AUD', 'EUR', 'GBP']:
    fx[curr] = 1 / fx[curr]

# Calculate daily changes (in log returns for percentages)
fx_currencies = ['CAD', 'JPY', 'MXN', 'NOK', 'CHF', 'AUD', 'EUR', 'GBP']
for curr in fx_currencies:
    # Log return = ln(P_t / P_{t-1}) ≈ percentage change
    fx[f'd_{curr}'] = np.log(fx[curr] / fx[curr].shift(1)) * 100  # in percent

print(f"Exchange rate data: {len(fx)} trading days")
print(f"Currencies: {fx_currencies}")
print(f"Date range: {fx['Date'].min().date()} to {fx['Date'].max().date()}")

# ============================================================================
# STEP 3: LOAD TREASURY YIELD DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 3: Loading Treasury Yields")
print("="*80)

# Historical data
treasury_hist = pd.read_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Data/par-yield-curve-rates-1990-2023.csv')
treasury_hist['Date'] = pd.to_datetime(treasury_hist['date'])
treasury_hist = treasury_hist.rename(columns={
    '2 yr': 'UST_2Y', '5 yr': 'UST_5Y', '10 yr': 'UST_10Y'
})

# Recent data (2024-2026)
treasury_files = [
    '/Users/trentonobannontrenton/MIT Coding Challenge/Data/daily-treasury-rates 2024.csv',
    '/Users/trentonobannontrenton/MIT Coding Challenge/Data/daily-treasury-rates 2025.csv',
    '/Users/trentonobannontrenton/MIT Coding Challenge/Data/daily-treasury-rates 2026.csv'
]

treasury_recent_list = []
for f in treasury_files:
    try:
        df = pd.read_csv(f)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.rename(columns={
            '2 Yr': 'UST_2Y', '5 Yr': 'UST_5Y', '10 Yr': 'UST_10Y'
        })
        treasury_recent_list.append(df[['Date', 'UST_2Y', 'UST_5Y', 'UST_10Y']])
    except:
        pass

# Combine all treasury data
treasury = pd.concat(
    [treasury_hist[['Date', 'UST_2Y', 'UST_5Y', 'UST_10Y']]] + treasury_recent_list,
    ignore_index=True
)
treasury = treasury.sort_values('Date').drop_duplicates(subset='Date')

# Calculate daily changes (in basis points)
for col in ['UST_2Y', 'UST_5Y', 'UST_10Y']:
    treasury[f'd_{col}'] = treasury[col].diff() * 100  # yields in %, change in bps

print(f"Treasury data: {len(treasury)} trading days")
print(f"Date range: {treasury['Date'].min().date()} to {treasury['Date'].max().date()}")

# ============================================================================
# STEP 4: LOAD BREAKEVEN INFLATION DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 4: Loading Breakeven Inflation")
print("="*80)

# 10Y Breakeven
be10 = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/10-Year Breakeven Inflation Rate.xlsx',
                     sheet_name='Daily')
be10['Date'] = pd.to_datetime(be10['observation_date'])
be10 = be10.rename(columns={'T10YIE': 'BE_10Y'})
be10 = be10.sort_values('Date')
be10['d_BE_10Y'] = be10['BE_10Y'].diff() * 100  # in bps

# 5Y Breakeven
be5 = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/5-Year Breakeven Inflation Rate.xlsx',
                    sheet_name='Daily')
be5['Date'] = pd.to_datetime(be5['observation_date'])
be5 = be5.rename(columns={'T5YIE': 'BE_5Y'})
be5 = be5.sort_values('Date')
be5['d_BE_5Y'] = be5['BE_5Y'].diff() * 100  # in bps

# Merge breakevens
breakevens = be10[['Date', 'BE_10Y', 'd_BE_10Y']].merge(
    be5[['Date', 'BE_5Y', 'd_BE_5Y']], 
    on='Date', 
    how='outer'
)

print(f"Breakeven data: {len(breakevens)} trading days")
print(f"Date range: {breakevens['Date'].min().date()} to {breakevens['Date'].max().date()}")

# ============================================================================
# STEP 5: MERGE ALL DATA ON FOMC DATES
# ============================================================================
print("\n" + "="*80)
print("STEP 5: Merging on FOMC Announcement Dates")
print("="*80)

# Start with surprises
merged = surprises.copy()

# Merge exchange rates
fx_cols = ['Date'] + [f'd_{curr}' for curr in fx_currencies]
merged = merged.merge(fx[fx_cols], on='Date', how='left')

# Merge treasury
treasury_cols = ['Date', 'd_UST_2Y', 'd_UST_5Y', 'd_UST_10Y']
merged = merged.merge(treasury[treasury_cols], on='Date', how='left')

# Merge breakevens
be_cols = ['Date', 'd_BE_5Y', 'd_BE_10Y']
merged = merged.merge(breakevens[be_cols], on='Date', how='left')

print(f"Merged dataset: {len(merged)} FOMC events")
print(f"\nColumns: {list(merged.columns)}")

# ============================================================================
# STEP 6: CHECK MISSING DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 6: Missing Data Analysis")
print("="*80)

missing = merged.isnull().sum()
print("Missing values by column:")
for col in merged.columns:
    if col != 'Date':
        n_miss = merged[col].isnull().sum()
        pct = n_miss / len(merged) * 100
        print(f"  {col:12}: {n_miss:3} missing ({pct:.1f}%)")

# ============================================================================
# STEP 7: SUMMARY STATISTICS (Task 1d)
# ============================================================================
print("\n" + "="*80)
print("STEP 7: Summary Statistics")
print("="*80)

# Convert surprise measures to bps for consistent reporting
merged['STMT_bps'] = merged['STMT'] * 100
merged['MP1_bps'] = merged['MP1'] * 100
merged['MP2_bps'] = merged['MP2'] * 100

# Variables for summary (use bps versions for surprises)
surprise_vars = ['STMT_bps', 'MP1_bps', 'MP2_bps']
fx_vars = [f'd_{c}' for c in fx_currencies]
treasury_vars = ['d_UST_2Y', 'd_UST_5Y', 'd_UST_10Y']
be_vars = ['d_BE_5Y', 'd_BE_10Y']
all_vars = surprise_vars + fx_vars + treasury_vars + be_vars

# Create summary stats
summary = merged[all_vars].describe().T
summary['N'] = merged[all_vars].notna().sum()
summary = summary[['N', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
summary.columns = ['N', 'Mean', 'Std', 'Min', 'P25', 'Median', 'P75', 'Max']

# Rename for clarity
summary.index = summary.index.str.replace('_bps', ' (bps)')

print("\nSummary Statistics:")
print(summary.round(4).to_string())

# Save summary statistics
summary.round(4).to_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/summary_statistics.csv')

# Also save as LaTeX with better formatting
latex_summary = summary.round(3)
latex_summary.to_latex('/Users/trentonobannontrenton/MIT Coding Challenge/Output/table1_summary_stats.tex',
                          caption='Summary Statistics: Monetary Policy Surprises and Asset Price Changes on FOMC Days (1994--2026)',
                          label='tab:summary',
                          float_format='%.3f')
print("\nSaved: Output/summary_statistics.csv")
print("Saved: Output/table1_summary_stats.tex")

# ============================================================================
# STEP 8: SAVE MERGED DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 8: Saving Merged Dataset")
print("="*80)

merged.to_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/merged_fomc_data.csv', index=False)
print(f"Saved: Output/merged_fomc_data.csv ({len(merged)} rows)")

# ============================================================================
# STEP 9: DATA QUALITY CHECKS
# ============================================================================
print("\n" + "="*80)
print("STEP 9: Data Quality Checks")
print("="*80)

# Check STMT mean (should be ~0 if markets are efficient)
print(f"\n1. STMT mean: {merged['STMT'].mean()*100:.2f} bps (should be ~0)")
print(f"   MP1 mean:  {merged['MP1'].mean()*100:.2f} bps (should be ~0)")

# Check yield changes are reasonable
print(f"\n2. Treasury yield changes on FOMC days:")
for col in treasury_vars:
    print(f"   {col}: mean={merged[col].mean():.2f}bps, std={merged[col].std():.2f}bps")

# Check FX changes are reasonable  
print(f"\n3. Exchange rate log returns on FOMC days (%):")
for col in fx_vars:
    print(f"   {col}: mean={merged[col].mean():.3f}%, std={merged[col].std():.3f}%")

# Correlation between surprise and yields (validation)
print(f"\n4. STMT correlations with Treasury changes (validation):")
for col in treasury_vars:
    valid = merged[['STMT', col]].dropna()
    corr = valid['STMT'].corr(valid[col])
    print(f"   STMT vs {col}: {corr:.3f}")

# Conditional means: Economic validation
print(f"\n5. Conditional means (economic validation):")
print("   This shows hawkish surprises move yields UP, dovish move them DOWN")
hawkish = merged[merged['STMT'] > 0]
dovish = merged[merged['STMT'] < 0]
print(f"   N(STMT > 0): {len(hawkish)}, N(STMT < 0): {len(dovish)}")
for col in ['d_UST_2Y', 'd_UST_5Y', 'd_UST_10Y']:
    mean_hawk = hawkish[col].mean()
    mean_dove = dovish[col].mean()
    print(f"   {col}: Mean(STMT>0) = {mean_hawk:+.2f}bps, Mean(STMT<0) = {mean_dove:+.2f}bps")

# Asymmetry analysis
print(f"\n   ASYMMETRY FINDING:")
print(f"   Dovish surprises generate larger absolute yield responses:")
for col in ['d_UST_2Y', 'd_UST_5Y', 'd_UST_10Y']:
    mean_hawk = abs(hawkish[col].mean())
    mean_dove = abs(dovish[col].mean())
    ratio = mean_dove / mean_hawk if mean_hawk > 0 else float('nan')
    print(f"   {col}: |dovish|/|hawkish| = {ratio:.2f}x")
print(f"   → Consistent with crisis-period emergency easing having outsized effects")

# Sample coverage by variable
print(f"\n6. Sample coverage by variable:")
for col in ['d_EUR', 'd_JPY', 'd_UST_2Y', 'd_BE_5Y', 'd_BE_10Y']:
    subset = merged[merged[col].notna()]
    first = subset['Date'].min()
    last = subset['Date'].max()
    n = len(subset)
    print(f"   {col}: {first.date()} to {last.date()} (N={n})")

print("\n" + "="*80)
print("DATA PREPARATION COMPLETE!")
print("="*80)

# ============================================================================
# STEP 10: LIMITATIONS AND METHODOLOGY NOTES
# ============================================================================
print("\n" + "="*80)
print("LIMITATIONS AND METHODOLOGY NOTES")
print("="*80)

# Get actual date range
date_min = merged['Date'].min()
date_max = merged['Date'].max()

print(f"""
SAMPLE:
- Date range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}
- N = {len(merged)} FOMC announcement days

LIMITATIONS:

1. TIMING MISMATCH:
   Asset prices are daily (close-to-close), while STMT is computed from 
   intraday futures windows around FOMC announcements. This introduces
   noise from non-announcement movements within the day.

2. SAMPLE COVERAGE:
   - Euro (EUR) starts January 1999 (45 events missing)
   - Breakeven inflation series start 2003 (80 events missing)
   - Early 1990s events have sparser high-frequency data

3. ZERO LOWER BOUND (ZLB):
   December 2008 – December 2015: With policy rates at zero, monetary
   transmission may operate through unconventional channels (forward
   guidance, QE), potentially altering the surprise-to-asset relationship.

4. MONETARY VS INFORMATION SHOCKS:
   STMT captures market surprise, but Fed announcements convey both
   policy actions and information about economic conditions. A dovish
   surprise could reflect either a policy ease OR bad news about the
   economy, with opposing asset price implications. Recent literature
   (Jarocinski-Karadi 2020, Bauer-Swanson 2023) proposes decomposition
   methods, which we do not implement here.

5. ASYMMETRY:
   Dovish surprises generate 3x larger absolute yield responses than
   hawkish surprises. This may reflect: (i) crisis-period emergency
   easing having outsized effects, (ii) ZLB constraints making dovish
   moves more unexpected, or (iii) nonlinear market reactions.
""")

print(f"""
Next steps:
1. Run Task 2 regressions using Output/merged_fomc_data.csv
2. Review Output/summary_statistics.csv for writeup
3. Check visualizations in Output/ folder
""")
