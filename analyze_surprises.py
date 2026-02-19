"""
USMPD Surprise Measures Analysis
Analyze monetary policy surprise measures to choose the best one for research
"""

import pandas as pd
import numpy as np

# Load the data
df = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/USMPD.xlsx', sheet_name='Statements')

print("="*80)
print("USMPD SURPRISE MEASURES - COMPREHENSIVE ANALYSIS")
print("="*80)

# Key surprise measures
surprise_cols = ['MP1', 'MP2', 'FF1', 'FF2', 'FF3', 'FF4', 'ED1', 'ED2', 'ED3', 'ED4']

print("\n" + "="*80)
print("1. BASIC INFO")
print("="*80)
print(f"Total FOMC events: {len(df)}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Scheduled meetings: {(df['Unscheduled']==0).sum()}")
print(f"Unscheduled meetings: {(df['Unscheduled']==1).sum()}")
print(f"Meetings with SEP (Summary of Economic Projections): {df['SEP'].sum()}")

print("\n" + "="*80)
print("2. SUMMARY STATISTICS - KEY SURPRISE MEASURES (in basis points)")
print("="*80)
# The measures are in percentage points, multiply by 100 for bps
print(df[surprise_cols].mul(100).describe().round(2).to_string())

print("\n" + "="*80)
print("3. NON-MISSING OBSERVATIONS BY MEASURE")
print("="*80)
for col in surprise_cols:
    n = df[col].notna().sum()
    print(f"{col}: {n} observations ({n/len(df)*100:.1f}%)")

print("\n" + "="*80)
print("4. CORRELATIONS BETWEEN SURPRISE MEASURES")
print("="*80)
corr = df[surprise_cols].corr().round(3)
print(corr.to_string())

print("\n" + "="*80)
print("5. SKEWNESS & KURTOSIS (important for monetary shocks)")
print("="*80)
skew_kurt = pd.DataFrame({
    'Skewness': df[surprise_cols].skew().round(3),
    'Kurtosis': df[surprise_cols].kurtosis().round(3)
})
print(skew_kurt.to_string())

print("\n" + "="*80)
print("6. EXTREME VALUES - Largest Positive & Negative Surprises")
print("="*80)
for col in ['MP1', 'MP2', 'ED1', 'ED4']:
    print(f"\n{col}:")
    # Top 3 positive
    top_pos = df.nlargest(3, col)[['Date', col]]
    print(f"  Largest positive: {top_pos[col].values[0]*100:.1f} bps on {top_pos['Date'].values[0]}")
    # Top 3 negative  
    top_neg = df.nsmallest(3, col)[['Date', col]]
    print(f"  Largest negative: {top_neg[col].values[0]*100:.1f} bps on {top_neg['Date'].values[0]}")

print("\n" + "="*80)
print("7. TIME PERIODS ANALYSIS")
print("="*80)
df['Year'] = pd.to_datetime(df['Date']).dt.year

# Pre-crisis, crisis, ZLB, normalization, COVID, recent
periods = {
    'Pre-crisis (1994-2007)': (1994, 2007),
    'Crisis (2008-2009)': (2008, 2009),
    'ZLB era (2010-2015)': (2010, 2015),
    'Normalization (2016-2019)': (2016, 2019),
    'COVID era (2020-2021)': (2020, 2021),
    'Tightening (2022-2024)': (2022, 2024)
}

for period_name, (start, end) in periods.items():
    subset = df[(df['Year'] >= start) & (df['Year'] <= end)]
    if len(subset) > 0:
        print(f"\n{period_name}:")
        print(f"  N = {len(subset)}")
        print(f"  MP1 std: {subset['MP1'].std()*100:.2f} bps")
        print(f"  MP2 std: {subset['MP2'].std()*100:.2f} bps")

print("\n" + "="*80)
print("8. CORRELATION WITH ASSET PRICES (built-in validation)")
print("="*80)
asset_cols = ['UST2Y', 'UST5Y', 'UST10Y', 'SP500', 'DXY']
for surprise in ['MP1', 'MP2']:
    print(f"\n{surprise} correlations:")
    for asset in asset_cols:
        if asset in df.columns:
            corr_val = df[[surprise, asset]].dropna().corr().iloc[0,1]
            print(f"  vs {asset}: {corr_val:.3f}")

print("\n" + "="*80)
print("9. CHECKING FOR PRINCIPAL COMPONENT IN DATA")
print("="*80)
all_cols = list(df.columns)
pc_candidates = [c for c in all_cols if 'PC' in c.upper() or 'PRINCIPAL' in c.upper() or 'FACTOR' in c.upper()]
if pc_candidates:
    print(f"Found PC-related columns: {pc_candidates}")
else:
    print("No pre-computed principal component found in USMPD.")
    print("If you want to use PC surprise, you'll need to compute it from ED1-ED4 or FF1-FF4")

print("\n" + "="*80)
print("10. MP1 vs MP2 COMPARISON (Target vs Path)")
print("="*80)
# When do they disagree?
df['MP1_sign'] = np.sign(df['MP1'])
df['MP2_sign'] = np.sign(df['MP2'])
same_sign = (df['MP1_sign'] == df['MP2_sign']).sum()
diff_sign = (df['MP1_sign'] != df['MP2_sign']).sum()
print(f"Same direction: {same_sign} times ({same_sign/len(df)*100:.1f}%)")
print(f"Opposite direction: {diff_sign} times ({diff_sign/len(df)*100:.1f}%)")
print("\nThis matters! When MP1 and MP2 have opposite signs:")
print("- Market interprets target change differently than forward guidance")
print("- Example: Rate hike (MP1>0) but dovish guidance (MP2<0)")

# Show examples of disagreement
disagree = df[df['MP1_sign'] != df['MP2_sign']][['Date', 'MP1', 'MP2']].dropna().head(5)
print("\nExamples of target/path disagreement:")
print(disagree.to_string())
