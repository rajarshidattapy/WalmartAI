import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Load the original dataset
df = pd.read_csv('Our_dataset.csv')

# Consumption patterns from your table
consumption_data = {
    'Baby Wipes 80pcs': [30, 25, 20, 15, 12, 10, 8],
    'Wet Cat Food': [7, 6, 5, 4, 4, 3, 3],
    '1L Milk': [3, 2, 1.5, 1.2, 1, 0.8, 0.7],
    'Powder Detergent': [45, 30, 22, 18, 15, 12, 10],
    'Orange Juice': [5, 3, 2.5, 2, 1.8, 1.5, 1.3],
    'Anti-dandruff': [60, 45, 35, 30, 25, 22, 20],
    'Glass Cleaner': [90, 60, 45, 35, 30, 25, 22],
    'Dry Cat Food': [21, 18, 15, 12, 10, 9, 8],
    'Cookies': [7, 5, 4, 3, 2.5, 2, 1.8],
    'Wet Dog Food': [5, 4, 3.5, 3, 2.5, 2.2, 2],
    'Spray Deo': [30, 25, 20, 18, 15, 13, 12],
    'Roll-on Deo': [45, 35, 28, 25, 22, 20, 18],
    'Yogurt Cup': [3, 2, 1.5, 1.2, 1, 0.9, 0.8],
    'Size M Diapers': [7, 6, 5, 4, 3.5, 3, 2.8],
    'Liquid Detergent': [35, 25, 20, 16, 14, 12, 10],
    'Size L Diapers': [8, 7, 6, 5, 4.5, 4, 3.5],
    'Charcoal Paste': [90, 60, 45, 40, 35, 30, 28],
    'Energy Drink': [2, 1.5, 1.2, 1, 0.9, 0.8, 0.7],
    'Herbal Shampoo': [45, 30, 25, 20, 18, 15, 14],
    'Dry Dog Food': [28, 24, 20, 18, 15, 13, 12],
    'Chips': [4, 3, 2.5, 2, 1.8, 1.5, 1.3],
    'Floor Cleaner': [60, 45, 35, 28, 25, 22, 20],
    'Granola Bar': [5, 4, 3, 2.5, 2, 1.8, 1.5],
    'Cheese 200g': [8, 6, 4, 3.5, 3, 2.5, 2.2],
    'Mint Toothpaste': [75, 50, 40, 35, 30, 25, 22],
    'Cola 500ml': [2, 1.5, 1.2, 1, 0.9, 0.8, 0.7]
}

# Function to generate additional purchases
def generate_additional_purchases(row, consumption_days):
    new_rows = []
    product_name = row['PRODUCT_NAME']
    
    if product_name in consumption_data:
        days_pattern = consumption_data[product_name]
        avg_days = days_pattern[0]  # First consumption rate
        
        # Determine how many additional purchases to create (1-3)
        num_additions = random.randint(1, 3)
        
        for i in range(num_additions):
            # Calculate days until next purchase with some randomness
            days_until_next = avg_days * (0.8 + random.random() * 0.4)
            
            # Create new date
            original_date = datetime.strptime(row['RunDate'], '%Y-%m-%d')
            new_date = original_date + timedelta(days=days_until_next)
            
            # Only create if still in 2022
            if new_date.year == 2022:
                new_row = row.copy()
                new_row['RunDate'] = new_date.strftime('%Y-%m-%d')
                
                # Adjust price slightly (within 5%)
                price_change = 0.95 + random.random() * 0.1
                new_row['PRICE_CURRENT'] = round(new_row['PRICE_CURRENT'] * price_change, 2)
                
                # Adjust size slightly (within 10%)
                size_change = 0.9 + random.random() * 0.2
                if 'g' in str(new_row['PRODUCT_SIZE']):
                    size_num = float(str(new_row['PRODUCT_SIZE']).replace('g',''))
                    new_row['PRODUCT_SIZE'] = f"{round(size_num * size_change)}g"
                elif 'ml' in str(new_row['PRODUCT_SIZE']):
                    size_num = float(str(new_row['PRODUCT_SIZE']).replace('ml',''))
                    new_row['PRODUCT_SIZE'] = f"{round(size_num * size_change)}ml"
                
                new_rows.append(new_row)
    
    return new_rows

# Generate additional purchases
additional_rows = []
for _, row in df.iterrows():
    additional_rows.extend(generate_additional_purchases(row, consumption_data))

# Create new DataFrame with additional purchases
additional_df = pd.DataFrame(additional_rows)

# Combine with original data
combined_df = pd.concat([df, additional_df], ignore_index=True)

# Save to new CSV
combined_df.to_csv('Our_dataset_with_repeats.csv', index=False)