import pandas as pd

# Load both datasets
pred = pd.read_csv("Output_dataset/predicted_purchases.csv", parse_dates=["predicted_next_date"])
df_main = pd.read_csv("Input_dataset/Our_dataset.csv")

# Get latest known shipping location and category per (tid, PRODUCT_NAME)
df_main_sorted = df_main.sort_values(by="RunDate")
df_main_latest = df_main_sorted.drop_duplicates(subset=["tid", "PRODUCT_NAME"], keep='last')[
    ['tid', 'PRODUCT_NAME', 'SHIPPING_LOCATION', 'CATEGORY']
]

# Merge prediction with latest location/category info
merged = pd.merge(
    pred,
    df_main_latest,
    on=['tid', 'PRODUCT_NAME'],
    how='left'
)

# Extract month from predicted date
merged['MONTH'] = merged['predicted_next_date'].dt.to_period('M').astype(str)

# Group by location, product, and month
monthly_forecast = (
    merged.groupby(['SHIPPING_LOCATION', 'PRODUCT_NAME', 'MONTH'])
    .size()
    .reset_index(name='Expected_Units')
    .sort_values(['MONTH', 'SHIPPING_LOCATION', 'Expected_Units'], ascending=[True, True, False])
)

# Save to CSV
monthly_forecast.to_csv("Output_dataset/warehouse_forecast.csv", index=False)

print("Monthly forecast saved to 'warehouse_forecast.csv'")
