"""
Quick diagnostic checks for Task 2
"""
import pandas as pd
import numpy as np
import os

# Base directory (relative to script location)
BASE = os.path.dirname(os.path.abspath(__file__))

merged = pd.read_csv(os.path.join(BASE, 'Output/merged_fomc_data.csv'))
merged['Date'] = pd.to_datetime(merged['Date'])

print('='*60)
print('1. DATE RANGE CHECK')
print('='*60)
print(f'First event: {merged["Date"].min().strftime("%Y-%m-%d")}')
print(f'Last event:  {merged["Date"].max().strftime("%Y-%m-%d")}')

print()
print('='*60)
print('2. STMT UNITS CHECK')
print('='*60)
print(f'STMT (raw) std: {merged["STMT"].std():.6f}')
print(f'STMT (bps) std: {merged["STMT"].std()*100:.3f} bps')
print('In regression: used STMT*100 (bps)')

print()
print('='*60)
print('3. AUD/MXN SPOT-CHECK ON BIG HAWKISH DAYS')
print('='*60)

# Find biggest hawkish surprises
merged_sorted = merged.sort_values('STMT', ascending=False)
top5_hawkish = merged_sorted.head(5)[['Date', 'STMT', 'd_AUD', 'd_MXN', 'd_JPY', 'd_EUR']]
print('Top 5 HAWKISH surprises (STMT > 0):')
print(top5_hawkish.to_string(index=False))

print()
# Check: On hawkish days, do AUD/MXN depreciate (positive d_)?
print('Interpretation:')
print('  Positive d_XXX = foreign currency depreciated (USD strengthened)')
print('  On hawkish days, we EXPECT d_XXX > 0')
print()
for curr in ['d_AUD', 'd_MXN', 'd_JPY', 'd_EUR']:
    hawkish = merged[merged['STMT'] > 0][curr].mean()
    dovish = merged[merged['STMT'] < 0][curr].mean()
    print(f'  {curr}: Mean(hawkish)={hawkish:+.4f}%, Mean(dovish)={dovish:+.4f}%')
