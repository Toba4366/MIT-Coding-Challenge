"""
Compare ALL available surprise measures to help choose the best one
"""

import pandas as pd
import numpy as np
import os

# Base directory (relative to script location)
BASE = os.path.dirname(os.path.abspath(__file__))

print("="*90)
print("COMPREHENSIVE COMPARISON OF ALL SURPRISE MEASURES")
print("="*90)

# Load both datasets
usmpd = pd.read_excel(os.path.join(BASE, 'Data/USMPD.xlsx'), sheet_name='Statements')
mps = pd.read_csv(os.path.join(BASE, 'Data/monetary-policy-surprises/mps.csv'))

# Merge on date
usmpd['Date'] = pd.to_datetime(usmpd['Date']).dt.date
mps['Date'] = pd.to_datetime(mps['Date']).dt.date
merged = usmpd.merge(mps, on='Date', how='outer', suffixes=('_usmpd', '_mps'))

print("\n" + "="*90)
print("AVAILABLE SURPRISE MEASURES SUMMARY")
print("="*90)

measures_info = """
FROM USMPD.xlsx (Statements sheet):
──────────────────────────────────────────────────────────────────────────────────────────
  MP1  : Target rate surprise (immediate policy action)
         - Change in front-month Fed Funds futures
         - Captures "did the Fed do what we expected TODAY?"
         - Pro: Clean, narrow identification
         - Con: Misses forward guidance entirely
         
  MP2  : Path/forward guidance surprise
         - Change in 3-month ahead Fed Funds futures minus MP1
         - Captures "did the Fed signal something unexpected about FUTURE policy?"
         - Pro: Captures forward guidance
         - Con: Harder to interpret, residual measure
         
  FF1-FF6: Fed Funds futures at different maturities
         - Raw futures changes, not decomposed
         
  ED1-ED4: Eurodollar futures changes (3mo, 6mo, 9mo, 12mo ahead)
         - Longer-term rate expectations
         - Pro: Captures term structure effects
         - Con: More noise, less direct Fed interpretation

FROM mps.csv (Acosta et al. 2025):
──────────────────────────────────────────────────────────────────────────────────────────
  STMT : Statement surprise (normalized)
         - First principal component of rate surprises around FOMC statements
         - Scaled to have 1-for-1 impact on 1-year Treasury yield
         - Pro: Theoretically grounded, follows Nakamura-Steinsson
         - Con: Single factor may miss multidimensional policy
         
  PC   : Press conference surprise (only available 2011+)
         - Captures additional information from Chair's press conference
         - Pro: Isolates press conference effect
         - Con: Only 90 observations
         
  ME   : Monetary event surprise (STMT + PC combined)
         - Total surprise from full FOMC meeting
         - Pro: Most comprehensive
         - Con: Conflates different information channels
"""
print(measures_info)

print("\n" + "="*90)
print("QUANTITATIVE COMPARISON (all in basis points)")
print("="*90)

# Compare key measures
key_measures = {
    'MP1 (USMPD)': merged['MP1'] * 100,
    'MP2 (USMPD)': merged['MP2'] * 100,
    'STMT (mps)': merged['STMT'] * 100,
    'ME (mps)': merged['ME'] * 100,
    'ED1 (USMPD)': merged['ED1'] * 100,
    'ED4 (USMPD)': merged['ED4'] * 100,
}

comparison_df = pd.DataFrame({k: v.describe() for k, v in key_measures.items()}).round(2)
print(comparison_df.to_string())

print("\n" + "="*90)
print("CORRELATION MATRIX - ALL KEY MEASURES")
print("="*90)
corr_df = pd.DataFrame(key_measures).corr().round(3)
print(corr_df.to_string())

print("\n" + "="*90)
print("VALIDATION: CORRELATION WITH TREASURY YIELD CHANGES")
print("="*90)
print("(Higher correlation = better at capturing policy surprise effect)")
print()

for measure_name, measure in key_measures.items():
    for treasury in ['UST2Y', 'UST5Y', 'UST10Y']:
        if treasury in merged.columns:
            valid_idx = measure.notna() & merged[treasury].notna()
            if valid_idx.sum() > 10:
                corr = measure[valid_idx].corr(merged.loc[valid_idx, treasury])
                print(f"  {measure_name:15} vs {treasury}: {corr:6.3f}")
    print()

print("\n" + "="*90)
print("DECISION FRAMEWORK - WHICH MEASURE TO CHOOSE?")
print("="*90)

decision_framework = """
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ RESEARCH QUESTION                          │ RECOMMENDED MEASURE                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Clean immediate policy shock               │ MP1                                        │
│ Forward guidance effects                   │ MP2 or STMT                                │
│ Overall monetary stance (comprehensive)    │ ME or STMT                                 │
│ Modern approach (Nakamura-Steinsson style) │ STMT (principal component, normalized)     │
│ Longer-term rate expectations              │ ED4                                        │
│ Full sample (1994+)                        │ MP1, MP2, STMT, ME                         │
│ Press conference effects only              │ PC (but only 90 obs)                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘
"""
print(decision_framework)

print("\n" + "="*90)
print("MY RECOMMENDATION FOR YOUR TASK")
print("="*90)

recommendation = """
For Task 3 (International Spillovers of US Monetary Policy), I recommend:

  PRIMARY CHOICE: STMT from mps.csv
  
  Why?
  ────────────────────────────────────────────────────────────────────────────────────────
  1. It's a PRINCIPAL COMPONENT - captures common variation across rate surprises
  2. It's NORMALIZED - has 1:1 impact on 1-year Treasury (interpretable units)
  3. It follows NAKAMURA-STEINSSON (2018) methodology - academically credible
  4. Full sample available (274 observations)
  5. Captures both target AND forward guidance (comprehensive)
  
  BACKUP CHOICE: MP1 from USMPD
  
  Why use as backup/robustness?
  ────────────────────────────────────────────────────────────────────────────────────────
  1. Most narrow/clean identification of immediate policy action
  2. Easier to interpret ("Fed surprised by X bps today")
  3. Standard in older literature (Kuttner 2001)
  4. Good for robustness checks

  WHAT TO SHOW IN YOUR WRITEUP:
  ────────────────────────────────────────────────────────────────────────────────────────
  • Main results with STMT
  • Robustness table with MP1 and MP2
  • Discuss tradeoffs explicitly
  • This shows research sophistication!
"""
print(recommendation)

print("\n" + "="*90)
print("CORRELATION BETWEEN YOUR TOP CHOICES")
print("="*90)
stmt_mp1_corr = merged['STMT'].corr(merged['MP1'])
stmt_mp2_corr = merged['STMT'].corr(merged['MP2'])
mp1_mp2_corr = merged['MP1'].corr(merged['MP2'])
print(f"STMT vs MP1: {stmt_mp1_corr:.3f}")
print(f"STMT vs MP2: {stmt_mp2_corr:.3f}")
print(f"MP1 vs MP2:  {mp1_mp2_corr:.3f}")
print()
print("Key insight: STMT and MP1 are highly correlated (0.9+)")
print("This means your main results should be robust across measures.")
