import re
import logging
import pandas as pd
from typing import Optional, Dict, Any, Tuple
import os

# Configure logging
logger = logging.getLogger(__name__)

def get_predicted_purchases_dataset():
    """Get the predicted purchases dataset from CSV file"""
    try:
        # Get the path to the predicted_purchases.csv file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, '..', 'Output_dataset', 'predicted_purchases.csv')
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            logger.info(f"Successfully loaded predicted purchases dataset with {len(df)} records")
            return df
        else:
            logger.error(f"Predicted purchases CSV file not found at: {csv_path}")
            return None
    except Exception as e:
        logger.error(f"Error loading predicted purchases dataset: {e}")
        return None

def get_dataset():
    """Get the dataset dynamically to avoid circular imports"""
    try:
        from gemini import df
        return df
    except ImportError:
        logger.error("Could not import dataset from gemini module")
        return None

def get_model():
    """Get the Gemini model dynamically to avoid circular imports"""
    try:
        from gemini import model
        return model
    except ImportError:
        logger.error("Could not import model from gemini module")
        return None

def extract_product_from_query(query: str) -> Optional[str]:
    """Extract product name from query using improved regex patterns"""
    if not query or not isinstance(query, str):
        return None
    
    query = query.lower().strip()
    
    # Enhanced patterns to extract product from different query formats
    patterns = [
        r"too much\s+([\w\s]+)",  # "am I having too much {product}"
        r"number of\s+([\w\s]+)",  # "what is the number of {product}"
        r"bought the most\s+([\w\s]+)",  # "what have I bought the most {product}"
        r"consumed\s+([\w\s]+)",  # "how much {product} have I consumed"
        r"purchased\s+([\w\s]+)",  # "how much {product} have I purchased"
        r"how much\s+([\w\s]+)",  # "how much {product}"
        r"quantity of\s+([\w\s]+)",  # "quantity of {product}"
        r"having\s+([\w\s]+)",  # "am I having {product}"
        r"consuming\s+([\w\s]+)",  # "am I consuming {product}"
        r"buying\s+([\w\s]+)",  # "am I buying {product}"
        r"purchasing\s+([\w\s]+)",  # "am I purchasing {product}"
        r"(\w+)\s+consumption",  # "{product} consumption"
        r"(\w+)\s+usage",  # "{product} usage"
        r"(\w+)\s+intake",  # "{product} intake"
    ]
    
    for pattern in patterns:
        try:
            match = re.search(pattern, query)
            if match:
                product = match.group(1).strip()
                if product and len(product) > 1:
                    return product
        except Exception as e:
            logger.warning(f"Error in regex pattern {pattern}: {e}")
            continue
    
    # Enhanced fallback: extract any word that might be a product
    words = query.split()
    product_keywords = [
        'cola', 'toothpaste', 'shampoo', 'soap', 'bread', 'milk', 'chips', 
        'soda', 'cereal', 'juice', 'water', 'coffee', 'tea', 'snacks',
        'chocolate', 'candy', 'cookies', 'nuts', 'fruits', 'vegetables',
        'meat', 'fish', 'eggs', 'cheese', 'yogurt', 'butter', 'oil',
        'sauce', 'ketchup', 'mayonnaise', 'mustard', 'salt', 'pepper',
        'sugar', 'flour', 'rice', 'pasta', 'noodles', 'beans', 'lentils',
        'beer', 'wine', 'alcohol', 'cigarettes', 'tobacco', 'energy', 'drink',
        'vitamin', 'supplement', 'medicine', 'drug', 'painkiller', 'aspirin'
    ]
    
    for word in words:
        if word in product_keywords:
            return word
    
    return None

def get_user_product_data_from_predictions(user_id: str, product: str) -> Dict[str, Any]:
    """Get specific product data from predicted_purchases.csv for a user"""
    df = get_predicted_purchases_dataset()
    if df is None:
        return {"error": "Predicted purchases dataset not available"}
    
    try:
        # Filter user's data for the specific product
        user_product_data = df[
            (df['tid'] == user_id) & 
            (df['PRODUCT_NAME'].str.contains(product, na=False, case=False))
        ]
        
        if user_product_data.empty:
            return {
                "product": product,
                "found": False,
                "message": f"No data found for {product} for user {user_id}"
            }
        
        # Get the first (and should be only) record for this user-product combination
        record = user_product_data.iloc[0]
        
        return {
            "product": record['PRODUCT_NAME'],
            "found": True,
            "estimated_family_size": record['estimated_family_size'],
            "avg_days_between_orders": record['avg_days_between_orders'],
            "consumption_days": record['consumption_days'],
            "last_purchase": record['last_purchase'],
            "predicted_next_date": record['predicted_next_date'],
            "message": f"Found data for {record['PRODUCT_NAME']}"
        }
        
    except Exception as e:
        logger.error(f"Error getting user product data from predictions: {e}")
        return {"error": f"Error retrieving data: {str(e)}"}

def calculate_product_usage(user_id: str, product: str) -> Dict[str, Any]:
    """Calculate user's product usage statistics with improved error handling"""
    # First try to get data from predicted_purchases.csv
    prediction_data = get_user_product_data_from_predictions(user_id, product)
    
    if prediction_data.get("found", False):
        # Use the prediction data to provide specific information
        avg_days = prediction_data['avg_days_between_orders']
        consumption_days = prediction_data['consumption_days']
        last_purchase = prediction_data['last_purchase']
        predicted_next = prediction_data['predicted_next_date']
        
        # Determine if consumption is excessive based on the data
        if avg_days < 1:
            frequency = "Very frequent (daily or multiple times per day)"
            consumption_level = "High"
        elif avg_days < 7:
            frequency = "Frequent (weekly)"
            consumption_level = "Moderate to High"
        elif avg_days < 30:
            frequency = "Occasional (monthly)"
            consumption_level = "Moderate"
        else:
            frequency = "Infrequent (rarely)"
            consumption_level = "Low"
        
        return {
            "product": prediction_data['product'],
            "total_purchases": "Data available",  # We don't have exact count in predictions
            "avg_days_between_orders": avg_days,
            "consumption_days": consumption_days,
            "last_purchase": last_purchase,
            "predicted_next_date": predicted_next,
            "frequency": frequency,
            "consumption_level": consumption_level,
            "message": f"Based on prediction data for {prediction_data['product']}",
            "source": "predicted_purchases.csv"
        }
    
    # Fallback to original dataset if prediction data not found
    df = get_dataset()
    if not user_id or not product or df is None:
        return {"error": "Invalid input or dataset not available"}
    
    try:
        # Filter user's purchases of the specific product with improved matching
        user_product_data = df[
            (df['tid'] == user_id) & 
            (df['PRODUCT_NAME'].str.contains(product, na=False, case=False))
        ]
        
        if user_product_data.empty:
            return {
                "product": product,
                "total_purchases": 0,
                "total_quantity": 0,
                "average_quantity": 0,
                "last_purchase": None,
                "usage_ml": 0,
                "message": f"No purchases found for {product}",
                "source": "original_dataset"
            }
        
        # Calculate statistics
        total_purchases = len(user_product_data)
        
        # Extract quantity from WEIGHT column if available
        total_quantity = 0
        if 'WEIGHT' in user_product_data.columns:
            try:
                # Extract numeric values from WEIGHT column with improved parsing
                weight_values = user_product_data['WEIGHT'].str.extract(r'(\d+(?:\.\d+)?)').astype(float)
                total_quantity = weight_values.sum().values[0] if not weight_values.empty else 0
            except Exception as e:
                logger.warning(f"Error extracting weight values: {e}")
                total_quantity = total_purchases  # Fallback to purchase count
        else:
            # If no WEIGHT column, estimate based on product type
            total_quantity = total_purchases * 100  # Default estimate
        
        average_quantity = total_quantity / total_purchases if total_purchases > 0 else 0
        
        # Get last purchase date if available
        last_purchase = None
        if 'DATE' in user_product_data.columns:
            try:
                last_purchase = user_product_data['DATE'].max()
            except Exception as e:
                logger.warning(f"Error getting last purchase date: {e}")
        
        # Calculate frequency (purchases per month if date available)
        frequency = "Unknown"
        if 'DATE' in user_product_data.columns and last_purchase:
            try:
                # Calculate average days between purchases
                dates = pd.to_datetime(user_product_data['DATE'], errors='coerce')
                if len(dates.dropna()) > 1:
                    date_diff = (dates.max() - dates.min()).days
                    if date_diff > 0:
                        avg_days = date_diff / (total_purchases - 1)
                        if avg_days <= 7:
                            frequency = "Very frequent (weekly)"
                        elif avg_days <= 30:
                            frequency = "Frequent (monthly)"
                        elif avg_days <= 90:
                            frequency = "Occasional (quarterly)"
                        else:
                            frequency = "Infrequent (rarely)"
            except Exception as e:
                logger.warning(f"Error calculating frequency: {e}")
        
        return {
            "product": product,
            "total_purchases": total_purchases,
            "total_quantity": total_quantity,
            "average_quantity": average_quantity,
            "last_purchase": last_purchase,
            "usage_ml": total_quantity,  # Assuming quantity is in ml for beverages
            "frequency": frequency,
            "message": f"Found {total_purchases} purchases of {product}",
            "source": "original_dataset"
        }
        
    except Exception as e:
        logger.error(f"Error calculating product usage: {e}")
        return {"error": f"Error calculating usage: {str(e)}"}

def get_most_purchased_products(user_id: str, limit: int = 5) -> Dict[str, Any]:
    """Get user's most purchased products with improved error handling"""
    # First try to get data from predicted_purchases.csv
    df_predictions = get_predicted_purchases_dataset()
    if df_predictions is not None:
        try:
            user_predictions = df_predictions[df_predictions['tid'] == user_id]
            if not user_predictions.empty:
                # Get unique products for this user
                user_products = user_predictions[['PRODUCT_NAME', 'avg_days_between_orders', 'consumption_days']].drop_duplicates()
                
                # Sort by consumption frequency (lower avg_days = more frequent)
                user_products = user_products.sort_values('avg_days_between_orders')
                
                products = []
                for _, row in user_products.head(limit).iterrows():
                    products.append({
                        "product": row['PRODUCT_NAME'],
                        "avg_days_between_orders": row['avg_days_between_orders'],
                        "consumption_days": row['consumption_days']
                    })
                
                return {
                    "user_id": user_id,
                    "products": products,
                    "message": f"Top {len(products)} most frequently purchased products (based on prediction data):",
                    "source": "predicted_purchases.csv"
                }
        except Exception as e:
            logger.warning(f"Error getting predictions data: {e}")
    
    # Fallback to original dataset
    df = get_dataset()
    if not user_id or df is None:
        return {"error": "Invalid input or dataset not available"}
    
    try:
        # Get user's purchase history
        user_data = df[df['tid'] == user_id]
        
        if user_data.empty:
            return {
                "user_id": user_id,
                "products": [],
                "message": "No purchase history found for this user.",
                "source": "original_dataset"
            }
        
        # Count products by name with improved handling
        product_counts = user_data['PRODUCT_NAME'].value_counts().head(limit)
        
        products = []
        for product, count in product_counts.items():
            products.append({
                "product": product,
                "purchase_count": int(count)
            })
        
        return {
            "user_id": user_id,
            "products": products,
            "message": f"Top {len(products)} most purchased products:",
            "source": "original_dataset"
        }
        
    except Exception as e:
        logger.error(f"Error getting most purchased products: {e}")
        return {"error": f"Error retrieving purchase history: {str(e)}"}

def generate_health_advice(product: str, usage_data: Dict[str, Any]) -> str:
    """Generate health advice using Gemini AI based on product usage with improved prompts"""
    model = get_model()
    if not product or not usage_data or "error" in usage_data:
        return "⚠️ Unable to generate health advice due to insufficient data."
    
    try:
        usage_ml = usage_data.get("usage_ml", 0)
        total_purchases = usage_data.get("total_purchases", 0)
        total_quantity = usage_data.get("total_quantity", 0)
        average_quantity = usage_data.get("average_quantity", 0)
        frequency = usage_data.get("frequency", "Unknown")
        
        # Create comprehensive prompt for Gemini
        prompt = f"""
        As a health and nutrition expert, analyze this user's consumption pattern and provide personalized advice:
        
        Product: {product}
        Total purchases: {total_purchases}
        Total quantity consumed: {total_quantity} ml
        Average per purchase: {average_quantity:.1f} ml
        Purchase frequency: {frequency}
        Estimated weekly consumption: {usage_ml} ml
        
        Please provide:
        1. An assessment of whether this consumption level is healthy or concerning
        2. Specific health implications of this consumption pattern
        3. Personalized recommendations for healthier alternatives or moderation
        4. Practical tips for reducing consumption if needed
        5. Alternative products they might consider
        
        Keep your response friendly, informative, and actionable. Focus on practical advice that the user can implement.
        Limit your response to 4-5 sentences for clarity.
        """
        
        # Call Gemini for personalized advice
        model = get_model()
        if model is not None:
            try:
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text'):
                    return response.text.strip()
                else:
                    return "⚠️ Unable to generate personalized health advice at this time."
            except Exception as e:
                logger.error(f"Gemini API error in health advice: {e}")
                # Fallback to basic advice based on consumption patterns
                return generate_fallback_advice(product, usage_data)
        else:
            return generate_fallback_advice(product, usage_data)
        
    except Exception as e:
        logger.error(f"Error generating health advice: {e}")
        return "⚠️ Error generating health advice."

def generate_fallback_advice(product: str, usage_data: Dict[str, Any]) -> str:
    """Generate fallback health advice when Gemini is not available"""
    total_purchases = usage_data.get("total_purchases", 0)
    frequency = usage_data.get("frequency", "Unknown")
    
    if total_purchases == 0:
        return f"📊 You haven't purchased any {product} yet. This is actually good for your health!"
    
    # Basic health advice based on product type and consumption
    if product in ['cola', 'soda', 'energy', 'drink']:
        if total_purchases > 10:
            return f"📊 You've purchased {product} {total_purchases} times ({frequency}). Consider reducing sugary drink consumption and switching to water or unsweetened beverages for better health."
        else:
            return f"📊 Your {product} consumption is moderate ({total_purchases} purchases). Keep it occasional and consider healthier alternatives like water or herbal tea."
    
    elif product in ['beer', 'wine', 'alcohol']:
        if total_purchases > 5:
            return f"📊 You've purchased {product} {total_purchases} times ({frequency}). Consider moderating alcohol consumption and exploring non-alcoholic alternatives for better health."
        else:
            return f"📊 Your {product} consumption appears moderate. Remember to drink responsibly and in moderation."
    
    elif product in ['cigarettes', 'tobacco']:
        return f"📊 You've purchased {product} {total_purchases} times. Consider quitting smoking for significant health benefits. Consult healthcare professionals for support."
    
    elif product in ['vitamin', 'supplement', 'medicine']:
        return f"📊 You've purchased {product} {total_purchases} times ({frequency}). Ensure you're following recommended dosages and consult with healthcare providers about supplement use."
    
    else:
        if total_purchases > 20:
            return f"📊 You've purchased {product} {total_purchases} times ({frequency}). This seems like a high consumption level. Consider diversifying your purchases and consulting a nutritionist for personalized advice."
        elif total_purchases > 10:
            return f"📊 You've purchased {product} {total_purchases} times ({frequency}). This is moderate consumption. Consider balancing your diet with a variety of healthy options."
        else:
            return f"📊 You've purchased {product} {total_purchases} times ({frequency}). This appears to be reasonable consumption. Keep up the balanced approach!"

def rag_product_analysis(user_id: str, query: str) -> str:
    """Main RAG function for product analysis with improved error handling"""
    if not user_id or not query:
        return "⚠️ Please provide both user ID and query."
    
    try:
        query = query.lower().strip()
        
        # Check if it's a "too much" query
        if "too much" in query or "excessive" in query or "overconsumption" in query:
            product = extract_product_from_query(query)
            if not product:
                return "⚠️ Please specify what product you're asking about. Try: 'am I having too much cola' or 'is my cola consumption excessive'"
            
            usage_data = calculate_product_usage(user_id, product)
            if "error" in usage_data:
                return f"⚠️ {usage_data['error']}"
            
            # Provide specific data from predictions instead of generic advice
            if usage_data.get("source") == "predicted_purchases.csv":
                avg_days = usage_data['avg_days_between_orders']
                consumption_days = usage_data['consumption_days']
                last_purchase = usage_data['last_purchase']
                predicted_next = usage_data['predicted_next_date']
                consumption_level = usage_data['consumption_level']
                
                response = f"📊 **Your {usage_data['product']} consumption analysis:**\n\n"
                response += f"• **Average days between orders:** {avg_days:.2f} days\n"
                response += f"• **Consumption days:** {consumption_days:.1f} days\n"
                response += f"• **Last purchase:** {last_purchase}\n"
                response += f"• **Predicted next purchase:** {predicted_next}\n"
                response += f"• **Consumption level:** {consumption_level}\n\n"
                
                if consumption_level == "High":
                    response += "⚠️ **Analysis:** Your consumption appears to be high. "
                    if avg_days < 1:
                        response += f"You're purchasing {usage_data['product']} almost daily, which may be excessive."
                    else:
                        response += f"You're purchasing every {avg_days:.1f} days on average."
                    response += " Consider reducing frequency for better health and cost management."
                elif consumption_level == "Moderate to High":
                    response += "💡 **Analysis:** Your consumption is moderate to high. "
                    response += f"You purchase {usage_data['product']} every {avg_days:.1f} days on average. "
                    response += "This might be reasonable depending on your needs, but monitor if it's necessary."
                elif consumption_level == "Moderate":
                    response += "✅ **Analysis:** Your consumption appears moderate. "
                    response += f"You purchase {usage_data['product']} every {avg_days:.1f} days on average. "
                    response += "This seems like a reasonable consumption pattern."
                else:
                    response += "✅ **Analysis:** Your consumption is low. "
                    response += f"You purchase {usage_data['product']} every {avg_days:.1f} days on average. "
                    response += "This is a healthy, controlled consumption pattern."
                
                return response
            else:
                # Fallback to original health advice for non-prediction data
                advice = generate_health_advice(product, usage_data)
                return advice
        
        # Check if it's a "most bought" query
        elif "bought the most" in query or "purchased the most" in query or "top purchases" in query:
            purchase_data = get_most_purchased_products(user_id)
            if "error" in purchase_data:
                return f"⚠️ {purchase_data['error']}"
            
            if not purchase_data["products"]:
                return purchase_data["message"]
            
            # Provide specific data from predictions
            if purchase_data.get("source") == "predicted_purchases.csv":
                response = f"📊 **{purchase_data['message']}**\n\n"
                response += "**Based on your actual purchase prediction data:**\n\n"
                
                for i, product_info in enumerate(purchase_data["products"], 1):
                    avg_days = product_info['avg_days_between_orders']
                    consumption_days = product_info['consumption_days']
                    
                    response += f"{i}. **{product_info['product']}**\n"
                    response += f"   • Average days between orders: {avg_days:.2f} days\n"
                    response += f"   • Consumption days: {consumption_days:.1f} days\n"
                    
                    if avg_days < 1:
                        response += f"   • Frequency: Very frequent (almost daily)\n"
                    elif avg_days < 7:
                        response += f"   • Frequency: Weekly\n"
                    elif avg_days < 30:
                        response += f"   • Frequency: Monthly\n"
                    else:
                        response += f"   • Frequency: Rarely\n"
                    response += "\n"
                
                response += "💡 **Insight:** This data shows your actual purchasing patterns based on Walmart's prediction algorithms. "
                response += "Products with lower average days between orders are purchased more frequently."
                
                return response
            else:
                # Fallback to original analysis for non-prediction data
                return generate_purchase_analysis_fallback(purchase_data)
        
        # Check if it's a "number of" or "how much" query
        elif "number of" in query or "how much" in query or "quantity" in query:
            product = extract_product_from_query(query)
            if not product:
                return "⚠️ Please specify what product you're asking about. Try: 'what is the number of cola that I have bought?' or 'how much toothpaste have I purchased?'"
            
            usage_data = calculate_product_usage(user_id, product)
            if "error" in usage_data:
                return f"⚠️ {usage_data['error']}"
            
            # Provide specific data from predictions
            if usage_data.get("source") == "predicted_purchases.csv":
                avg_days = usage_data['avg_days_between_orders']
                consumption_days = usage_data['consumption_days']
                last_purchase = usage_data['last_purchase']
                predicted_next = usage_data['predicted_next_date']
                
                response = f"📊 **Your {usage_data['product']} purchase details:**\n\n"
                response += f"• **Average days between orders:** {avg_days:.2f} days\n"
                response += f"• **Consumption days:** {consumption_days:.1f} days\n"
                response += f"• **Last purchase:** {last_purchase}\n"
                response += f"• **Predicted next purchase:** {predicted_next}\n\n"
                
                # Calculate estimated annual consumption
                if avg_days > 0:
                    annual_purchases = 365 / avg_days
                    response += f"• **Estimated annual purchases:** {annual_purchases:.1f} times\n"
                
                response += f"\n💡 **Analysis:** Based on Walmart's prediction data, you purchase {usage_data['product']} "
                if avg_days < 1:
                    response += "almost daily, which is very frequent consumption."
                elif avg_days < 7:
                    response += f"every {avg_days:.1f} days on average, which is weekly consumption."
                elif avg_days < 30:
                    response += f"every {avg_days:.1f} days on average, which is monthly consumption."
                else:
                    response += f"every {avg_days:.1f} days on average, which is infrequent consumption."
                
                return response
            else:
                # Fallback to original analysis for non-prediction data
                if usage_data["total_purchases"] == 0:
                    return f"📊 You haven't purchased any {product} yet."
                
                return generate_usage_analysis_fallback(product, usage_data)
        
        # Check for general health/consumption queries
        elif "health" in query or "consumption" in query or "diet" in query:
            return "💡 For health analysis, try specific queries like:\n• 'am I having too much cola'\n• 'what is the number of soda I have bought'\n• 'what have I bought the most'"
        
        else:
            return "💡 Try these RAG queries:\n• 'am I having too much cola'\n• 'what have I bought the most'\n• 'what is the number of toothpaste that I have bought'\n• 'how much shampoo have I consumed'"
    
    except Exception as e:
        logger.error(f"Error in RAG product analysis: {e}")
        return "⚠️ An error occurred while analyzing your data. Please try again."

def generate_purchase_analysis_fallback(purchase_data: Dict[str, Any]) -> str:
    """Generate fallback analysis for purchase patterns"""
    response = f"📊 {purchase_data['message']}\n\n"
    
    # Check if we have prediction data
    if purchase_data.get("source") == "predicted_purchases.csv":
        for i, product_info in enumerate(purchase_data["products"], 1):
            avg_days = product_info.get('avg_days_between_orders', 'N/A')
            consumption_days = product_info.get('consumption_days', 'N/A')
            
            response += f"{i}. **{product_info['product']}**\n"
            response += f"   • Average days between orders: {avg_days}\n"
            response += f"   • Consumption days: {consumption_days}\n\n"
    else:
        # Original format for non-prediction data
        for i, product_info in enumerate(purchase_data["products"], 1):
            response += f"{i}. {product_info['product'].title()}: {product_info['purchase_count']} purchases\n"
    
    response += "\n💡 **Basic Analysis:**\n"
    response += "Consider diversifying your purchases and exploring healthier alternatives. "
    response += "High consumption of certain products might indicate areas where you could make healthier choices."
    
    return response

def generate_usage_analysis_fallback(product: str, usage_data: Dict[str, Any]) -> str:
    """Generate fallback analysis for product usage"""
    response = f"📊 Your {product} purchase summary:\n"
    
    # Check if we have prediction data
    if usage_data.get("source") == "predicted_purchases.csv":
        avg_days = usage_data.get('avg_days_between_orders', 'N/A')
        consumption_days = usage_data.get('consumption_days', 'N/A')
        last_purchase = usage_data.get('last_purchase', 'N/A')
        predicted_next = usage_data.get('predicted_next_date', 'N/A')
        
        response += f"• Average days between orders: {avg_days}\n"
        response += f"• Consumption days: {consumption_days}\n"
        response += f"• Last purchase: {last_purchase}\n"
        response += f"• Predicted next purchase: {predicted_next}\n"
        
        response += f"\n💡 **Basic Insights:**\n"
        if isinstance(avg_days, (int, float)) and avg_days < 1:
            response += f"Your {product} consumption appears very frequent (almost daily). Consider if this is necessary."
        elif isinstance(avg_days, (int, float)) and avg_days < 7:
            response += f"Your {product} consumption is weekly. This seems reasonable for most products."
        elif isinstance(avg_days, (int, float)) and avg_days < 30:
            response += f"Your {product} consumption is monthly. This is a healthy consumption pattern."
        else:
            response += f"Your {product} consumption is infrequent. This is a controlled consumption pattern."
    else:
        # Original format for non-prediction data
        response += f"• Total purchases: {usage_data['total_purchases']}\n"
        response += f"• Total quantity: {usage_data['total_quantity']} ml\n"
        response += f"• Average per purchase: {usage_data['average_quantity']:.1f} ml\n"
        response += f"• Purchase frequency: {usage_data.get('frequency', 'Unknown')}\n"
        if usage_data["last_purchase"]:
            response += f"• Last purchase: {usage_data['last_purchase']}\n"
        
        response += f"\n💡 **Basic Insights:**\n"
        if usage_data['total_purchases'] > 15:
            response += f"Your {product} consumption appears high. Consider reducing frequency and exploring alternatives."
        elif usage_data['total_purchases'] > 5:
            response += f"Your {product} consumption is moderate. Consider balancing with other products."
        else:
            response += f"Your {product} consumption is reasonable. Keep up the balanced approach!"
    
    return response

def detect_rag_intent(query: str) -> str:
    """Detect if query is a RAG-related query with improved keyword detection"""
    if not query or not isinstance(query, str):
        return "not_rag"
    
    query = query.lower().strip()
    
    rag_keywords = [
        "too much", "bought the most", "purchased the most", 
        "number of", "how much", "consumed", "purchased",
        "quantity", "amount", "frequency", "excessive", "overconsumption",
        "consumption", "usage", "intake", "health", "diet", "lifestyle",
        "top purchases", "most bought", "frequently bought", "regular purchases",
        "consumption pattern", "buying habit", "purchase history", "shopping pattern"
    ]
    
    if any(keyword in query for keyword in rag_keywords):
        return "rag_query"
    
    return "not_rag" 