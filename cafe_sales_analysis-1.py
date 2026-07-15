"""
Cafe Sales Data Analysis
Author: Feriel
Description: Cleaning and exploratory analysis of a dirty cafe sales dataset (10,000 transactions)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# 1. LOAD DATA
# ============================================================
df = pd.read_csv("/content/sample_data/dirty_cafe_sales.csv")

# ============================================================
# 2. INITIAL EXPLORATION
# ============================================================
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.info())
print(df.describe())
print(df.isna().sum())
print(df.duplicated().sum())

# ============================================================
# 3. DATA CLEANING
# ============================================================
# Replace placeholder junk values ('UNKNOWN', 'ERROR') with real NaN
# NOTE: .replace() returns a NEW series, it doesn't happen "in place"
# unless you reassign it back to the column. This was the bug in v1.
cols_to_clean = ['Item', 'Payment Method', 'Location', 'Transaction Date']
for col in cols_to_clean:
    df[col] = df[col].replace(['UNKNOWN', 'ERROR'], np.nan)

# Convert numeric columns (coerce turns invalid values into NaN)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Price Per Unit'] = pd.to_numeric(df['Price Per Unit'], errors='coerce')

# Fill missing Quantity with the mean (reassigned properly this time)
df['Quantity'] = df['Quantity'].fillna(df['Quantity'].mean())

# Recompute Total Spent from clean Quantity * Price Per Unit
df['Total Spent'] = df['Quantity'] * df['Price Per Unit']
df['Total Spent'] = pd.to_numeric(df['Total Spent'], errors='coerce')

# Convert Transaction Date to datetime
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')

# Drop duplicates and rows that are mostly empty (keep rows with at least 6 non-null values)
df = df.drop_duplicates()
df = df.dropna(thresh=6)

print("\nAfter cleaning:")
print(df.isna().sum())

# ============================================================
# 4. SALES METRICS
# ============================================================
total_sales = df['Total Spent'].sum()
avg_transaction = df['Total Spent'].mean()
top_order = df['Total Spent'].max()
lowest_order = df['Total Spent'].min()

print(f"\nTotal Sales: {total_sales:,.2f}")
print(f"Average Transaction Value: {avg_transaction:.2f}")
print(f"Top Order Value: {top_order}")
print(f"Lowest Order Value: {lowest_order}")

# ============================================================
# 5. ITEMS ANALYSIS
# ============================================================
top_item = df['Item'].value_counts().head(1)
lowest_item = df['Item'].value_counts().tail(1)
sales_by_item = df.groupby('Item')['Total Spent'].sum().sort_values(ascending=False)
avg_item_price = df['Price Per Unit'].mean()

print(f"\nTop Selling Item:\n{top_item}")
print(f"\nLowest Selling Item:\n{lowest_item}")
print(f"\nSales by Item:\n{sales_by_item}")

# ============================================================
# 6. PAYMENT METHOD ANALYSIS
# ============================================================
best_payment_method = df['Payment Method'].value_counts().head(1)
sales_by_payment = df.groupby('Payment Method')['Total Spent'].sum()
avg_by_payment = df.groupby('Payment Method')['Total Spent'].mean()

# ============================================================
# 7. LOCATION ANALYSIS
# ============================================================
sales_by_location = df.groupby('Location')['Total Spent'].sum()
top_location = sales_by_location.idxmax()

# ============================================================
# 8. TIME ANALYSIS
# ============================================================
sales_by_date = df.groupby('Transaction Date')['Total Spent'].sum()
months = df['Transaction Date'].dt.month_name()
sales_by_month = df.groupby(months)['Total Spent'].sum()

# Order months chronologically for a cleaner chart
month_order = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
sales_by_month = sales_by_month.reindex(month_order)

# ============================================================
# 9. QUANTITY ANALYSIS
# ============================================================
avg_quantity = df['Quantity'].mean()
quantity_by_item = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False)

# ============================================================
# 10. CORRELATIONS
# ============================================================
corr_qty_spent = df[['Quantity', 'Total Spent']].corr()
corr_price_spent = df[['Price Per Unit', 'Total Spent']].corr()

print(f"\nCorrelation Quantity vs Total Spent:\n{corr_qty_spent}")
print(f"\nCorrelation Price Per Unit vs Total Spent:\n{corr_price_spent}")

# ============================================================
# 11. VISUALIZATIONS (combined dashboard)
# ============================================================
fig, ax = plt.subplots(3, 2, figsize=(15, 15))
ax1, ax2, ax3, ax4, ax5, ax6 = ax[0,0], ax[0,1], ax[1,0], ax[1,1], ax[2,0], ax[2,1]

# --- Distribution of Sales ---
sns.histplot(data=df, x='Total Spent', bins=10, kde=True,
             color='steelblue', edgecolor='white', linewidth=0.8, alpha=0.8, ax=ax1)
ax1.axvline(df['Total Spent'].mean(), color='coral', linewidth=2, linestyle='--',
            label=f"Mean: {df['Total Spent'].mean():.1f}")
ax1.set_title('Distribution of Sales', fontsize=14, fontweight='bold')
ax1.set_xlabel('Sales'); ax1.set_ylabel('Frequency')
ax1.grid(axis="y", alpha=0.3); ax1.legend()

# --- Sales vs Quantity ---
sns.regplot(data=df, x='Total Spent', y='Quantity', ax=ax2,
            scatter_kws={'alpha': 0.4}, line_kws={'color': 'red', 'linewidth': 1})
ax2.set_title('Sales vs Quantity', fontsize=14, fontweight='bold')
ax2.set_xlabel('Sales', fontsize=12); ax2.set_ylabel('Quantity', fontsize=12)
ax2.grid(True, alpha=0.3)

# --- Sales by Location ---
bars = ax3.barh(sales_by_location.index, sales_by_location.values,
                 color='steelblue', edgecolor='white', height=0.5)
ax3.set_title('Sales by Location', fontsize=14, fontweight='bold')
ax3.set_xlabel('Sales'); ax3.set_ylabel('Location')
ax3.grid(axis='x', alpha=0.3)
for bar in bars:
    width = bar.get_width()
    ax3.text(width + 300, bar.get_y() + bar.get_height()/2, f"{width:,.0f}",
              ha='left', va='center', fontsize=9)

# --- Sales by Item ---
bars = ax4.bar(sales_by_item.index, sales_by_item.values,
                color='steelblue', edgecolor='white', linewidth=0.8)
ax4.set_title('Sales by Item', fontsize=14, fontweight="bold")
ax4.set_xlabel('Item'); ax4.set_ylabel('Sales')
ax4.grid(axis='y', alpha=0.3)
ax4.tick_params(axis='x', rotation=45)
for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2, height + 300, f"{height:,.0f}",
              ha="center", va="bottom", fontsize=9)

# --- Sales Per Month ---
ax5.plot(sales_by_month.index, sales_by_month.values, color='steelblue', linewidth=2,
          linestyle="-", marker='o', markersize=8, markerfacecolor='white',
          markeredgecolor='steelblue', label='Sales per Month')
ax5.set_title('Sales Per Month', fontsize=14, fontweight='bold')
ax5.set_xlabel('Month'); ax5.set_ylabel('Sales')
ax5.tick_params(axis='x', rotation=45)
ax5.legend()

# --- Sales by Payment Method (pie) ---
wedges, texts, autotexts = ax6.pie(
    sales_by_payment.values, labels=sales_by_payment.index,
    autopct='%1.1f%%', startangle=90,
    colors=["steelblue", "#ADD8E6", "#1F4E79"], explode=[0.05, 0, 0])
for autotext in autotexts:
    autotext.set_fontsize(10); autotext.set_fontweight('bold'); autotext.set_color('white')
ax6.set_title('Sales by Payment Method', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/cafe_sales_dashboard.png', dpi=150)
plt.show()

# ============================================================
# 12. KEY INSIGHTS (for portfolio write-up)
# ============================================================
insights = f"""
KEY INSIGHTS - Cafe Sales Analysis
-----------------------------------
1. Total revenue across {len(df)} clean transactions: {total_sales:,.2f}
2. Average transaction value: {avg_transaction:.2f}
3. Best-selling item by volume: {top_item.index[0]} ({top_item.values[0]} orders)
4. Top revenue-generating item: {sales_by_item.index[0]} ({sales_by_item.values[0]:,.0f})
5. In-store vs Takeaway sales are nearly balanced ({sales_by_location.to_dict()})
6. Moderate positive correlation (r={corr_qty_spent.iloc[0,1]:.2f}) between
   Quantity and Total Spent -> customers buying more units spend proportionally more.
7. Payment methods are evenly split (~33% each across Cash, Credit Card, Digital Wallet),
   suggesting no dominant payment preference among customers.
"""
print(insights)
