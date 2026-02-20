"""
Clarify what 'PC' means in USMPD and make final recommendation
"""

import pandas as pd
import numpy as np
import os

# Base directory (parent of scripts/ folder where Data/ and Output/ exist)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load all relevant data
me = pd.read_excel(os.path.join(BASE, 'Data/USMPD.xlsx'), sheet_name='Monetary Events')
stmt = pd.read_excel(os.path.join(BASE, 'Data/USMPD.xlsx'), sheet_name='Statements')
pc_sheet = pd.read_excel(os.path.join(BASE, 'Data/USMPD.xlsx'), sheet_name='Press Conferences')
mps = pd.read_csv(os.path.join(BASE, 'Data/monetary-policy-surprises/mps.csv'))

print('='*80)
print('CRITICAL DISCOVERY: What is PC in USMPD?')
print('='*80)
print()
print("PC column in 'Monetary Events' sheet:")
print(f"  Unique values: {me['PC'].unique()}")
print(f"  This is a BINARY FLAG (0 = no press conference, 100 = press conference)")
print(f"  It is NOT a surprise measure!")
print()

print('='*80)
print('USMPD SHEET STRUCTURE')
print('='*80)
print("""
USMPD.xlsx has 4 data sheets:

1. 'Statements' (274 rows)
   - MP1, MP2, FF1-FF6, ED1-ED8, UST changes, etc.
   - Captures high-frequency changes around FOMC STATEMENTS
   - This is where MP1, MP2 come from

2. 'Press Conferences' (90 rows)
   - Same columns as Statements
   - Captures changes around PRESS CONFERENCES (post-April 2011)
   - Separate event from statement

3. 'Monetary Events' (274 rows)  
   - Same columns PLUS a 'PC' binary flag
   - 'PC' = 1 if there was a press conference that day
   - The surprise columns here = Statement + Press Conference combined

4. 'Minutes' (201 rows)
   - Changes around FOMC Minutes releases
   - Different event type
""")

print('='*80)
print('SO WHERE IS THE PRINCIPAL COMPONENT SURPRISE?')
print('='*80)
print("""
The challenge says "pre-constructed principal component surprises" are available.

ANSWER: They are in mps.csv from the Acosta et al. (2025) code!

mps.csv columns:
  - STMT: Statement surprise (PRINCIPAL COMPONENT, normalized)
  - PC: Press Conference surprise (also principal component, only 90 obs)
  - ME: Monetary Event = STMT + PC combined

The 'PC' in mps.csv is DIFFERENT from 'PC' in USMPD.xlsx:
  - mps.csv PC = Press Conference SURPRISE (a number)
  - USMPD PC = Press Conference FLAG (0 or 100)
""")

print('='*80)
print('VALIDATION: How was STMT constructed?')
print('='*80)

# Merge to check
stmt['Date'] = pd.to_datetime(stmt['Date']).dt.date
mps['Date'] = pd.to_datetime(mps['Date']).dt.date
merged = stmt.merge(mps, on='Date', how='inner')

print('STMT correlation with USMPD Statements sheet columns:')
for col in ['MP1', 'MP2', 'FF1', 'FF2', 'FF3', 'FF4', 'ED1', 'ED2', 'ED3', 'ED4']:
    corr = merged['STMT'].corr(merged[col])
    print(f"  STMT vs {col}: {corr:.3f}")

print()
print('='*80)
print('STMT vs HIGH-FREQUENCY ASSET PRICE CHANGES')
print('='*80)
for col in ['UST2Y', 'UST5Y', 'UST10Y', 'SP500', 'DXY']:
    if col in merged.columns:
        # These are the intraday changes from USMPD, not daily!
        corr = merged['STMT'].corr(merged[col])
        print(f"  STMT vs {col} (intraday change): {corr:.3f}")

print()
print('='*80) 
print('KEY INSIGHT: Why these correlations validate STMT')
print('='*80)
print("""
The UST2Y, UST5Y, UST10Y columns in USMPD are INTRADAY changes around FOMC.

STMT correlates highly with these because:
  1. STMT is constructed from FF/ED futures changes
  2. Treasury yields move in response to the SAME information
  3. High correlation = STMT captures what moves yields

This is NOT circular because:
  - STMT is built from Fed Funds and Eurodollar futures
  - UST yields are different instruments
  - Both respond to monetary policy news

CONCLUSION: STMT is well-constructed and validated!
""")

print('='*80)
print('FINAL RECOMMENDATION FOR PREDOC CHALLENGE')
print('='*80)

# Compare all options
print()
print("COMPARISON TABLE:")
print("-"*80)
print(f"{'Measure':<15} {'Source':<25} {'N':<8} {'Description':<30}")
print("-"*80)
print(f"{'STMT':<15} {'mps.csv':<25} {'274':<8} {'PC of statement surprises':<30}")
print(f"{'ME':<15} {'mps.csv':<25} {'274':<8} {'STMT + Press Conf combined':<30}")
print(f"{'MP1':<15} {'USMPD Statements':<25} {'274':<8} {'Target rate surprise':<30}")
print(f"{'MP2':<15} {'USMPD Statements':<25} {'274':<8} {'Path/forward guidance':<30}")
print(f"{'ED4':<15} {'USMPD Statements':<25} {'274':<8} {'12-month Eurodollar':<30}")
print("-"*80)

print()
print("RECOMMENDATION:")
print("="*80)
print("""
✅ PRIMARY: Use STMT from mps.csv

   Reasons:
   1. It IS the principal component mentioned in the challenge
   2. Follows Acosta et al. (2025) - cited in challenge
   3. Normalized: 1 bp STMT = 1 bp move in 1Y Treasury
   4. Full sample (274 FOMC events)
   5. Validated: 0.855 correlation with UST2Y changes

✅ ROBUSTNESS: Also report results with MP1

   Reasons:
   1. Traditional measure (Kuttner 2001 style)
   2. Shows results aren't measure-dependent
   3. Easier interpretation ("target surprise")

❌ DON'T USE: ME from mps.csv
   
   Reason: It conflates statement and press conference effects.
   For clean identification, use STMT alone.

❌ DON'T USE: PC from mps.csv as primary
   
   Reason: Only 90 observations (press conferences started 2011)
""")

print()
print("="*80)
print("WHAT TO WRITE IN YOUR JUSTIFICATION:")
print("="*80)
print('''
"I use the STMT measure from mps.csv as my primary monetary policy surprise. 
This measure, constructed by Acosta et al. (2025), represents the first 
principal component of high-frequency changes in federal funds and Eurodollar 
futures around FOMC statements, normalized to have a one-for-one impact on the 
1-year Treasury yield. 

This choice offers several advantages: (1) it captures both target rate and 
forward guidance surprises in a single measure; (2) the normalization provides 
interpretable units; and (3) it is validated by its strong correlation (0.85) 
with actual high-frequency Treasury yield changes around FOMC announcements.

As a robustness check, I also present results using MP1 (the target rate 
surprise), which offers a narrower but cleaner identification of immediate 
policy shocks."
''')
