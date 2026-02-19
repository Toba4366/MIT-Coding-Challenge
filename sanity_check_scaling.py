"""
Sanity Check: Verify STMT scaling by comparing biggest shocks to 2Y Treasury response
"""
import pandas as pd
import numpy as np

# Load merged data
merged = pd.read_csv('Output/merged_fomc_data.csv')

# Use existing STMT_bps column, or create if needed
if 'STMT_bps' not in merged.columns:
    merged['STMT_bps'] = merged['STMT'] * 100

# Find the most extreme STMT shocks
print('='*60)
print('SANITY CHECK: STMT Scaling vs 2Y Treasury Response')
print('='*60)

# Top 5 most dovish (negative) STMT shocks
print('\n--- Top 5 Most DOVISH Shocks (largest negative STMT) ---')
dovish = merged.nsmallest(5, 'STMT_bps')[['Date', 'STMT_bps', 'd_UST_2Y']]
for _, row in dovish.iterrows():
    predicted = row['STMT_bps'] * 1.058
    print(f"{row['Date']}: STMT={row['STMT_bps']:+.2f} bps, Actual 2Y={row['d_UST_2Y']:+.2f} bps, Predicted={predicted:+.2f} bps")

# Top 5 most hawkish (positive) STMT shocks
print('\n--- Top 5 Most HAWKISH Shocks (largest positive STMT) ---')
hawkish = merged.nlargest(5, 'STMT_bps')[['Date', 'STMT_bps', 'd_UST_2Y']]
for _, row in hawkish.iterrows():
    predicted = row['STMT_bps'] * 1.058
    print(f"{row['Date']}: STMT={row['STMT_bps']:+.2f} bps, Actual 2Y={row['d_UST_2Y']:+.2f} bps, Predicted={predicted:+.2f} bps")

# Summary stats
print('\n--- STMT Distribution (bps) ---')
print(f"Min:  {merged['STMT_bps'].min():.2f} bps")
print(f"Max:  {merged['STMT_bps'].max():.2f} bps")
print(f"Std:  {merged['STMT_bps'].std():.2f} bps")
print(f"Mean: {merged['STMT_bps'].mean():.2f} bps")

# Check the biggest shock in detail
print('\n--- Detailed Check: Biggest Dovish Shock ---')
biggest_dovish = merged.loc[merged['STMT_bps'].idxmin()]
print(f"Date: {biggest_dovish['Date']}")
print(f"STMT: {biggest_dovish['STMT_bps']:.2f} bps")
print(f"2Y actual: {biggest_dovish['d_UST_2Y']:.2f} bps")
print(f"2Y predicted (β=1.058): {biggest_dovish['STMT_bps'] * 1.058:.2f} bps")
print(f"Residual: {biggest_dovish['d_UST_2Y'] - biggest_dovish['STMT_bps'] * 1.058:.2f} bps")

# Check correlation between STMT and 2Y
print('\n--- Correlation Check ---')
valid = merged.dropna(subset=['STMT_bps', 'd_UST_2Y'])
corr = valid['STMT_bps'].corr(valid['d_UST_2Y'])
print(f"Correlation(STMT, 2Y): {corr:.3f}")
print(f"R² = {corr**2:.3f} (should match regression R² ≈ 0.27)")

# Check if prediction roughly matches for extreme events
print('\n--- VERDICT ---')
biggest_actual = biggest_dovish['d_UST_2Y']
biggest_predicted = biggest_dovish['STMT_bps'] * 1.058
ratio = biggest_actual / biggest_predicted if biggest_predicted != 0 else float('inf')
print(f"Actual/Predicted ratio for biggest shock: {ratio:.2f}")
if 0.5 < ratio < 2.0:
    print("✅ SCALING IS CORRECT - actual 2Y move is in the ballpark of predicted")
else:
    print("⚠️  SCALING MAY BE OFF - ratio is outside expected range")
