"""
FX Convention Deep Dive - What's actually happening?
"""
import pandas as pd
import numpy as np

# Load the raw FX data
fx = pd.read_excel('/Users/trentonobannontrenton/MIT Coding Challenge/Data/Exchange_Rates.xlsx', 
                   sheet_name='Daily')
fx['Date'] = pd.to_datetime(fx['observation_date'])

print("="*60)
print("RAW FRED DATA DEFINITIONS")
print("="*60)
print("""
FRED convention:
- DEXCAUS = CAD per USD (e.g., 1.35 means 1 USD = 1.35 CAD)
- DEXJPUS = JPY per USD (e.g., 110 means 1 USD = 110 JPY)  
- DEXMXUS = MXN per USD
- DEXNOUS = NOK per USD
- DEXSZUS = CHF per USD
- DEXUSAL = USD per AUD (e.g., 0.75 means 1 AUD = 0.75 USD) ← INVERTED!
- DEXUSEU = USD per EUR (e.g., 1.10 means 1 EUR = 1.10 USD) ← INVERTED!
- DEXUSUK = USD per GBP (e.g., 1.30 means 1 GBP = 1.30 USD) ← INVERTED!
""")

print("="*60)
print("WHAT THE LOG RETURN MEANS")
print("="*60)
print("""
For CAD/JPY/MXN/NOK/CHF (already Foreign per USD):
  d = ln(P_t / P_{t-1}) * 100
  If d > 0: It takes MORE foreign currency to buy 1 USD
            → USD APPRECIATED → Foreign DEPRECIATED
  
For AUD/EUR/GBP (after inverting to Foreign per USD):
  Same logic applies after inversion.

So positive d_XXX SHOULD mean USD strengthened.
BUT the data shows negative d on hawkish days!

CONCLUSION: Either:
1. The inversion was done wrong, OR
2. The economic relationship is weaker/different than expected
""")

print("="*60)
print("CHECK A SPECIFIC BIG HAWKISH DAY")
print("="*60)

# June 25, 2003 - biggest hawkish surprise
# Check what happened to USD
date_check = '2003-06-25'
fx_check = fx[fx['Date'] == date_check]
fx_prev = fx[fx['Date'] < date_check].tail(1)

if len(fx_check) > 0 and len(fx_prev) > 0:
    print(f"\nDate: {date_check} (STMT = +0.090, biggest hawkish surprise)")
    print()
    
    for col, name in [('DEXUSAL', 'AUD (USD per AUD)'), 
                      ('DEXMXUS', 'MXN (MXN per USD)')]:
        prev_val = fx_prev[col].values[0]
        curr_val = fx_check[col].values[0]
        pct_change = (curr_val / prev_val - 1) * 100
        print(f"{name}:")
        print(f"  Previous: {prev_val:.4f}")
        print(f"  Current:  {curr_val:.4f}")
        print(f"  Change:   {pct_change:+.2f}%")
        print()

print("="*60)
print("INTERPRETATION")
print("="*60)
print("""
If DEXUSAL (USD per AUD) FELL on hawkish day:
  → AUD weakened vs USD (correct!)
  → After inverting (AUD per USD), value ROSE
  → Log return is POSITIVE
  
But we see NEGATIVE d_AUD. Let me check the math...
""")

# Recompute manually
merged = pd.read_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/merged_fomc_data.csv')
merged['Date'] = pd.to_datetime(merged['Date'])
row = merged[merged['Date'] == date_check]
print(f"\nIn merged data for {date_check}:")
print(f"  d_AUD = {row['d_AUD'].values[0]:.4f}%")
print(f"  d_MXN = {row['d_MXN'].values[0]:.4f}%")
print(f"  d_JPY = {row['d_JPY'].values[0]:.4f}%")
