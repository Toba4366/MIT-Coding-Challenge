"""
Task 1: Generate Visualizations for Writeup
- Time series of monetary policy surprises
- Correlation heatmap
- Distribution plots
- STMT vs MP1 scatter
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

# Load merged data
merged = pd.read_csv('/Users/trentonobannontrenton/MIT Coding Challenge/Output/merged_fomc_data.csv')
merged['Date'] = pd.to_datetime(merged['Date'])

print("="*80)
print("GENERATING VISUALIZATIONS FOR TASK 1")
print("="*80)

# ============================================================================
# FIGURE 1: Time Series of Monetary Policy Surprises
# ============================================================================
print("\nCreating Figure 1: Time series of surprises...")

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Panel A: STMT over time
ax1 = axes[0]
ax1.bar(merged['Date'], merged['STMT']*100, width=20, alpha=0.7, color='steelblue', label='STMT')
ax1.axhline(0, color='black', linewidth=0.5, linestyle='-')
ax1.set_ylabel('Surprise (basis points)', fontsize=11)
ax1.set_title('Panel A: Statement Surprise (STMT)', fontsize=12, fontweight='bold')

# Add shaded regions for key periods
from matplotlib.patches import Rectangle
# Financial Crisis
ax1.axvspan(pd.Timestamp('2008-01-01'), pd.Timestamp('2009-12-31'), 
            alpha=0.2, color='red', label='Financial Crisis')
# COVID
ax1.axvspan(pd.Timestamp('2020-01-01'), pd.Timestamp('2021-12-31'), 
            alpha=0.2, color='orange', label='COVID-19')
ax1.legend(loc='upper left', fontsize=9)

# Panel B: MP1 vs MP2
ax2 = axes[1]
ax2.bar(merged['Date'], merged['MP1']*100, width=20, alpha=0.6, color='navy', label='MP1 (Target)')
ax2.bar(merged['Date'], merged['MP2']*100, width=20, alpha=0.6, color='crimson', label='MP2 (Path)')
ax2.axhline(0, color='black', linewidth=0.5, linestyle='-')
ax2.set_ylabel('Surprise (basis points)', fontsize=11)
ax2.set_xlabel('Date', fontsize=11)
ax2.set_title('Panel B: Target (MP1) vs Path (MP2) Surprises', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)

# Format x-axis
ax2.xaxis.set_major_locator(mdates.YearLocator(5))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure1_surprise_timeseries.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure1_surprise_timeseries.png")

# ============================================================================
# FIGURE 2: Correlation Heatmap
# ============================================================================
print("\nCreating Figure 2: Correlation heatmap...")

# Select key variables
corr_vars = ['STMT', 'MP1', 'MP2', 'd_UST_2Y', 'd_UST_5Y', 'd_UST_10Y', 
             'd_EUR', 'd_GBP', 'd_JPY', 'd_CHF']
corr_labels = ['STMT', 'MP1', 'MP2', 'UST 2Y', 'UST 5Y', 'UST 10Y',
               'EUR', 'GBP', 'JPY', 'CHF']

corr_matrix = merged[corr_vars].corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix), k=1)
sns.heatmap(corr_matrix, 
            mask=mask,
            annot=True, 
            fmt='.2f',
            cmap='RdBu_r', 
            center=0,
            vmin=-1, 
            vmax=1,
            square=True,
            linewidths=0.5,
            xticklabels=corr_labels,
            yticklabels=corr_labels,
            ax=ax,
            cbar_kws={'label': 'Correlation'})
ax.set_title('Correlation Matrix: Surprises and Asset Price Changes\n(FOMC Days Only)', 
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure2_correlation_heatmap.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure2_correlation_heatmap.png")

# ============================================================================
# FIGURE 3: Distribution of Surprise Measures
# ============================================================================
print("\nCreating Figure 3: Distribution plots...")

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

# STMT distribution
ax = axes[0]
ax.hist(merged['STMT']*100, bins=30, edgecolor='white', color='steelblue', alpha=0.7)
ax.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Zero')
ax.axvline(merged['STMT'].mean()*100, color='green', linestyle='-', linewidth=1.5, label='Mean')
ax.set_xlabel('Surprise (bps)', fontsize=10)
ax.set_ylabel('Frequency', fontsize=10)
ax.set_title('STMT Distribution', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)

# MP1 distribution
ax = axes[1]
ax.hist(merged['MP1']*100, bins=30, edgecolor='white', color='navy', alpha=0.7)
ax.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Zero')
ax.axvline(merged['MP1'].mean()*100, color='green', linestyle='-', linewidth=1.5, label='Mean')
ax.set_xlabel('Surprise (bps)', fontsize=10)
ax.set_ylabel('Frequency', fontsize=10)
ax.set_title('MP1 Distribution', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)

# MP2 distribution
ax = axes[2]
ax.hist(merged['MP2']*100, bins=30, edgecolor='white', color='royalblue', alpha=0.7)
ax.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Zero')
ax.axvline(merged['MP2'].mean()*100, color='green', linestyle='-', linewidth=1.5, label='Mean')
ax.set_xlabel('Surprise (bps)', fontsize=10)
ax.set_ylabel('Frequency', fontsize=10)
ax.set_title('MP2 Distribution', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure3_surprise_distributions.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure3_surprise_distributions.png")

# ============================================================================
# FIGURE 4: STMT vs MP1 Scatter (showing they capture similar variation)
# ============================================================================
print("\nCreating Figure 4: STMT vs MP1 scatter...")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# STMT vs MP1
ax = axes[0]
ax.scatter(merged['MP1']*100, merged['STMT']*100, alpha=0.5, s=30, color='steelblue')
# Add regression line
z = np.polyfit(merged['MP1']*100, merged['STMT']*100, 1)
p = np.poly1d(z)
x_line = np.linspace(merged['MP1'].min()*100, merged['MP1'].max()*100, 100)
ax.plot(x_line, p(x_line), 'r-', linewidth=2, label=f'Slope: {z[0]:.2f}')
ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
corr = merged['STMT'].corr(merged['MP1'])
ax.set_xlabel('MP1 (Target Surprise, bps)', fontsize=11)
ax.set_ylabel('STMT (Principal Component, bps)', fontsize=11)
ax.set_title(f'STMT vs MP1 (corr = {corr:.3f})', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)

# STMT vs Treasury 2Y change (validation)
ax = axes[1]
valid = merged[['STMT', 'd_UST_2Y']].dropna()
ax.scatter(valid['STMT']*100, valid['d_UST_2Y'], alpha=0.5, s=30, color='darkgreen')
z = np.polyfit(valid['STMT']*100, valid['d_UST_2Y'], 1)
p = np.poly1d(z)
x_line = np.linspace(valid['STMT'].min()*100, valid['STMT'].max()*100, 100)
ax.plot(x_line, p(x_line), 'r-', linewidth=2, label=f'Slope: {z[0]:.2f}')
ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
corr = valid['STMT'].corr(valid['d_UST_2Y'])
ax.set_xlabel('STMT (Principal Component, bps)', fontsize=11)
ax.set_ylabel('2Y Treasury Change (bps)', fontsize=11)
ax.set_title(f'Validation: STMT vs 2Y Treasury (corr = {corr:.3f})', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure4_stmt_validation.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure4_stmt_validation.png")

# ============================================================================
# FIGURE 5: Event-day Scatter - Δ2Y vs Δ10Y colored by STMT sign
# ============================================================================
print("\nCreating Figure 5: Event-day scatter (Δ2Y vs Δ10Y by STMT sign)...")

fig, ax = plt.subplots(figsize=(10, 8))

# Create color based on STMT sign
valid = merged[['STMT', 'd_UST_2Y', 'd_UST_10Y']].dropna()
colors = ['crimson' if s > 0 else 'steelblue' for s in valid['STMT']]
sizes = np.abs(valid['STMT']) * 100 * 30 + 20  # Size proportional to |STMT|

scatter = ax.scatter(valid['d_UST_2Y'], valid['d_UST_10Y'], 
                     c=colors, s=sizes, alpha=0.6, edgecolor='white', linewidth=0.5)

# Add 45-degree line
lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])]
ax.plot(lims, lims, 'k--', alpha=0.3, linewidth=1, label='45° line')

# Add zero lines
ax.axhline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
ax.axvline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

# Create custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='crimson', 
           markersize=10, label='Hawkish (STMT > 0)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', 
           markersize=10, label='Dovish (STMT < 0)'),
    Line2D([0], [0], linestyle='--', color='black', alpha=0.3, label='45° line')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

ax.set_xlabel('Δ 2Y Treasury Yield (bps)', fontsize=12)
ax.set_ylabel('Δ 10Y Treasury Yield (bps)', fontsize=12)
ax.set_title('Treasury Yield Changes on FOMC Days\n(Size = |STMT|, Color = STMT sign)', 
             fontsize=13, fontweight='bold')

# Add correlation annotation
corr_2y_10y = valid['d_UST_2Y'].corr(valid['d_UST_10Y'])
ax.annotate(f'Corr(Δ2Y, Δ10Y) = {corr_2y_10y:.3f}', 
            xy=(0.95, 0.05), xycoords='axes fraction',
            ha='right', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure5_event_scatter.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure5_event_scatter.png")

# ============================================================================
# FIGURE 6: Surprise Volatility by Period
# ============================================================================
print("\nCreating Figure 6: Volatility by period...")

merged['Year'] = merged['Date'].dt.year

periods = {
    'Pre-Crisis\n(1994-2007)': (1994, 2007),
    'Crisis\n(2008-2009)': (2008, 2009),
    'ZLB Era\n(2010-2015)': (2010, 2015),
    'Normalization\n(2016-2019)': (2016, 2019),
    'COVID\n(2020-2021)': (2020, 2021),
    'Tightening\n(2022-2024)': (2022, 2024)
}

period_stats = []
for name, (start, end) in periods.items():
    subset = merged[(merged['Year'] >= start) & (merged['Year'] <= end)]
    if len(subset) > 0:
        period_stats.append({
            'Period': name,
            'N': len(subset),
            'STMT_std': subset['STMT'].std() * 100,
            'MP1_std': subset['MP1'].std() * 100
        })

period_df = pd.DataFrame(period_stats)

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(period_df))
width = 0.35

bars1 = ax.bar(x - width/2, period_df['STMT_std'], width, label='STMT', color='steelblue', alpha=0.8)
bars2 = ax.bar(x + width/2, period_df['MP1_std'], width, label='MP1', color='navy', alpha=0.8)

ax.set_ylabel('Standard Deviation (bps)', fontsize=11)
ax.set_xlabel('Period', fontsize=11)
ax.set_title('Monetary Policy Surprise Volatility by Period', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(period_df['Period'], fontsize=9)
ax.legend(fontsize=10)

# Add N labels on top
for i, (n, s1, s2) in enumerate(zip(period_df['N'], period_df['STMT_std'], period_df['MP1_std'])):
    ax.annotate(f'N={n}', xy=(i, max(s1, s2) + 0.5), ha='center', fontsize=8, color='gray')

ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
plt.tight_layout()
plt.savefig('/Users/trentonobannontrenton/MIT Coding Challenge/Output/figure6_volatility_by_period.png', 
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved: Output/figure6_volatility_by_period.png")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("VISUALIZATIONS COMPLETE!")
print("="*80)
print("""
Created figures:
  1. figure1_surprise_timeseries.png   - Time series of STMT, MP1, MP2
  2. figure2_correlation_heatmap.png   - Correlation matrix
  3. figure3_surprise_distributions.png - Histograms
  4. figure4_stmt_validation.png       - STMT vs MP1, STMT vs 2Y Treasury
  5. figure5_event_scatter.png         - Δ2Y vs Δ10Y colored by STMT sign
  6. figure6_volatility_by_period.png  - Volatility across monetary regimes

All figures saved to: Output/
""")
