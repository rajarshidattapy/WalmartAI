import pandas as pd

# Load your dataset
df = pd.read_csv("../Input_dataset/Our_dataset.csv")

# Clean up in case there are extra spaces
df['PRODUCT_NAME'] = df['PRODUCT_NAME'].str.strip()
df['CATEGORY'] = df['CATEGORY'].str.strip()
df['BRAND'] = df['BRAND'].str.strip()

def recommend_brands(tid_input, product_name_input):
    # Step 1: Find the category of the given product
    '''
    row = df[df['PRODUCT_NAME'] == product_name_input]
    if row.empty:
        return f"❌ Product '{product_name_input}' not found in dataset."
    
    category = row.iloc[0]['CATEGORY']
    '''
    
    # Step 2: Get the user’s brand history in that category
    user_cat_df = df[(df['tid'] == tid_input) & (df['PRODUCT_NAME'] == product_name_input)]
    
    if user_cat_df.empty:
        return {
            "PRODUCT_NAME": product_name_input,
            "Primary_Brand": "(None)",
            "Exploratory_Brand": "BrandE",
            "Note": f"No past purchases in '{product_name_input}'. Recommend trying BrandE."
        }

    # Step 3: Count brand frequency
    brand_counts = user_cat_df['BRAND'].value_counts()
    primary_brand = brand_counts.idxmax()
    
    return {
        "PRODUCT_NAME": product_name_input,
        "Primary_Brand": primary_brand,
        
        "Exploratory_Brand": "BrandE"
    }


result = recommend_brands("T1005U0192", "Cola 500ml")
print(result)
