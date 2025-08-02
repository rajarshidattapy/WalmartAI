import os
import pandas as pd
from datetime import timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, '..', 'Input_dataset')
output_dir = os.path.join(base_dir, '..', 'Output_dataset')

# Load your datasets
df = pd.read_csv(os.path.join(input_dir, 'Our_dataset.csv'), parse_dates=["RunDate"])
consumption = pd.read_csv(os.path.join(input_dir, 'consumption_table.csv'))

# Step 1: Calculate avg days between orders per user-product
df.sort_values(by=["tid", "PRODUCT_NAME", "RunDate"], inplace=True)
grouped = df.groupby(['tid', 'PRODUCT_NAME'])

purchase_patterns = grouped['RunDate'].agg(['min', 'max', 'count']).reset_index()
purchase_patterns['avg_days_between_orders'] = (
    (purchase_patterns['max'] - purchase_patterns['min']).dt.days / (purchase_patterns['count'] - 1)
).fillna(0)

# Step 2: Estimate family size using consumption table
def match_family_size(product, avg_days):
    row = consumption[consumption['Product'] == product]
    if row.empty:
        return None, None
    diffs = {str(size): abs(avg_days - row[str(size)].values[0]) for size in ['1','2','3','4','5','6','6+']}
    best_fit = min(diffs, key=diffs.get)
    return best_fit, row[best_fit].values[0]

# Apply estimation
family_sizes = []
consumptions = []

for _, row in purchase_patterns.iterrows():
    est_size, consump = match_family_size(row['PRODUCT_NAME'], row['avg_days_between_orders'])
    family_sizes.append(est_size)
    consumptions.append(consump)

purchase_patterns['estimated_family_size'] = family_sizes
purchase_patterns['consumption_days'] = consumptions

# Step 3: Predict next purchase date (last known + estimated consumption)
last_dates = grouped['RunDate'].max().reset_index().rename(columns={'RunDate': 'last_purchase'})
purchase_patterns = pd.merge(purchase_patterns, last_dates, on=['tid', 'PRODUCT_NAME'])
purchase_patterns['predicted_next_date'] = purchase_patterns['last_purchase'] + purchase_patterns['consumption_days'].apply(lambda x: timedelta(days=x) if pd.notnull(x) else timedelta(days=0))

# Step 4: Final output
predicted_restock = purchase_patterns[['tid', 'PRODUCT_NAME', 'estimated_family_size', 'avg_days_between_orders', 'consumption_days', 'last_purchase', 'predicted_next_date']]
predicted_restock.to_csv(os.path.join(output_dir, 'predicted_purchases.csv'), index=False)
print("Working")