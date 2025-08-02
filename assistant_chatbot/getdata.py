import pandas as pd
from datetime import datetime
import os

# Load prediction results with robust path handling
predictions_path = os.path.join(os.path.dirname(__file__), 'predicted_purchases.csv')
if not os.path.exists(predictions_path):
    # Try alternative paths
    alt_paths = [
        'predicted_purchases.csv',
        os.path.join(os.path.dirname(__file__), '..', 'Output_dataset', 'predicted_purchases.csv'),
        os.path.join(os.path.dirname(__file__), '..', 'predicted_purchases.csv')
    ]
    
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            predictions_path = alt_path
            break
    else:
        raise FileNotFoundError(f"predicted_purchases.csv not found! Tried paths: {[predictions_path] + alt_paths}")

df_predictions = pd.read_csv(predictions_path, parse_dates=["predicted_next_date"])

def get_restock_list(tid_input, reference_date=None):
    """
    Returns the list of products a user should restock and their predicted restock dates.
    
    Parameters:
    - tid_input: str, the user ID (e.g. 'T7444U658')
    - reference_date: datetime.date (optional), to check what’s due as of a given date
    
    Returns:
    - DataFrame with PRODUCT_NAME and predicted_next_date
    """
    user_data = df_predictions[df_predictions['tid'] == tid_input].copy()
    
    if user_data.empty:
        print(f"No data found for user: {tid_input}")
        return pd.DataFrame(columns=["PRODUCT_NAME", "predicted_next_date"])
    
    # Use today's date or provided date to filter
    if reference_date is None:
        reference_date = datetime.today().date()
    
    # Filter only items whose restock date is due or past
    due_items = user_data[user_data['predicted_next_date'].dt.date <= reference_date]
    
    return due_items[['PRODUCT_NAME', 'predicted_next_date']].sort_values(by='predicted_next_date')

# Example for userID: T1005U0192
restock_list = get_restock_list("T1005U0192")
print(restock_list)
