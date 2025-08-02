import pandas as pd
from datetime import datetime
import logging
import os
from typing import Optional, Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

# Global variable to store predictions data
df_predictions = None

def initialize_restocking() -> bool:
    """Initialize the restocking module by loading prediction data"""
    global df_predictions
    
    try:
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
                logger.error(f"predicted_purchases.csv not found! Tried paths: {[predictions_path] + alt_paths}")
                return False
        
        logger.info(f"Loading restocking predictions from: {predictions_path}")
        df_predictions = pd.read_csv(predictions_path, parse_dates=["predicted_next_date"])
        logger.info(f"Loaded restocking predictions with {len(df_predictions)} records")
        return True
    except Exception as e:
        logger.error(f"Failed to load restocking predictions: {e}")
        return False

def get_restock_list(user_id: str, reference_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Returns the list of products a user should restock and their predicted restock dates.
    
    Parameters:
    - user_id: str, the user ID (e.g. 'T7444U658')
    - reference_date: datetime (optional), to check what's due as of a given date
    
    Returns:
    - List of dictionaries with product info and restock dates
    """
    global df_predictions
    
    if df_predictions is None:
        logger.error("Restocking predictions not loaded")
        return []
    
    try:
        # Input validation
        if not user_id or not isinstance(user_id, str):
            logger.warning("Invalid user_id provided")
            return []
        
        user_id = user_id.strip()
        if not user_id:
            return []
        
        # Filter data for the specific user
        user_data = df_predictions[df_predictions['tid'] == user_id].copy()
        
        if user_data.empty:
            logger.info(f"No restocking data found for user: {user_id}")
            return []
        
        # Use today's date or provided date to filter
        if reference_date is None:
            reference_date = datetime.today()
        
        # Filter only items whose restock date is due or past
        due_items = user_data[user_data['predicted_next_date'] <= reference_date]
        
        if due_items.empty:
            return []
        
        # Convert to list of dictionaries for easy JSON serialization
        restock_items = []
        for _, row in due_items.iterrows():
            restock_items.append({
                "product_name": row['PRODUCT_NAME'],
                "predicted_date": row['predicted_next_date'].strftime('%Y-%m-%d'),
                "days_overdue": (reference_date - row['predicted_next_date']).days
            })
        
        # Sort by predicted date (earliest first)
        restock_items.sort(key=lambda x: x['predicted_date'])
        
        return restock_items
        
    except Exception as e:
        logger.error(f"Error getting restock list for user {user_id}: {e}")
        return []

def format_restock_response(restock_items: List[Dict[str, Any]]) -> str:
    """Format the restock response in a user-friendly way"""
    if not restock_items:
        return "✅ Great news! You don't need to restock any products right now."
    
    response = "🛒 Products that need restocking:\n\n"
    
    for item in restock_items:
        product_name = item['product_name']
        predicted_date = item['predicted_date']
        days_overdue = item['days_overdue']
        
        if days_overdue > 0:
            response += f"⚠️ {product_name} - Due since {predicted_date} ({days_overdue} days overdue)\n"
        else:
            response += f"📦 {product_name} - Due on {predicted_date}\n"
    
    response += f"\n📊 Total items to restock: {len(restock_items)}"
    return response

def check_restock_status(user_id: str) -> str:
    """Main function to check restock status for a user"""
    try:
        restock_items = get_restock_list(user_id)
        return format_restock_response(restock_items)
    except Exception as e:
        logger.error(f"Error checking restock status: {e}")
        return "⚠️ Error checking restock status. Please try again." 