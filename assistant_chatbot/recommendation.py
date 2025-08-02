import re
import logging
from gemini import similar_users_dict
from typing import Optional, Dict, Any
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

def detect_intent(query: str) -> str:
    """Detect user intent with improved validation and logic"""
    if not query or not isinstance(query, str):
        return "general_query"
    
    query = query.lower().strip()
    if not query:
        return "general_query"
    
    # Check for restocking queries first
    restock_keywords = ['restock', 'restocking', 'check if to be restocked', 'need to restock', 'restock status']
    if any(keyword in query for keyword in restock_keywords):
        return "restock_check"
    
    # Check for gemini queries
    if 'walmart' in query:
        return "gemini_query"
    
    # Check for brand suggestion keywords
    suggest_keywords = ['suggest', 'recommend', 'brand', 'best', 'recommendation']
    if any(keyword in query for keyword in suggest_keywords):
        return "brand_suggestion"
    
    return "general_query"

def extract_keyword(text: str) -> str:
    """Extract keyword with improved regex patterns and validation"""
    if not text or not isinstance(text, str):
        return ""
    
    text = text.lower().strip()
    if not text:
        return ""
    
    # Try multiple patterns for keyword extraction
    patterns = [
        r"(?:for|about)\s+([\w\s]+)",
        r"(?:suggest|recommend)\s+(?:brands?\s+)?(?:for\s+)?([\w\s]+)",
        r"(?:best|top)\s+([\w\s]+)",
        r"([\w\s]+)\s+(?:brands?|products?)"
    ]
    
    for pattern in patterns:
        try:
            match = re.search(pattern, text)
            if match:
                keyword = match.group(1).strip()
                if keyword and len(keyword) > 1:  # Ensure keyword is meaningful
                    return keyword
        except Exception as e:
            logger.warning(f"Error in regex pattern {pattern}: {e}")
            continue
    
    # Fallback: extract any word that might be a product
    words = text.split()
    product_keywords = ['cola', 'toothpaste', 'shampoo', 'soap', 'bread', 'milk', 'chips', 'soda', 'cereal', 'juice']
    for word in words:
        if word in product_keywords:
            return word
    
    return ""

def format_response(data_dict: Dict[str, Any]) -> str:
    """Format response with comprehensive error handling and validation"""
    if not data_dict or not isinstance(data_dict, dict):
        return "⚠️ No recommendations found."
    
    try:
        msg = data_dict.get("message", "")
        product = data_dict.get("PRODUCT_NAME", "")
        primary = data_dict.get("Primary_Brand", "null")
        exploratory = data_dict.get("Exploratory_Brand", "null")
        
        # Validate all values are strings
        if not isinstance(msg, str):
            msg = ""
        if not isinstance(product, str):
            product = ""
        if not isinstance(primary, str):
            primary = "null"
        if not isinstance(exploratory, str):
            exploratory = "null"
        
        response = f"💡 {msg}\n\n📦 Product: {product}\n"
        
        if primary and primary != "null":
            response += f"🛍️ Your Preferred Brand: {primary}\n"
        
        if exploratory and exploratory != "null":
            if primary == "null":
                response += f"✨ Popular Brand: {exploratory}"
            else:
                response += f"✨ Try This Brand: {exploratory}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return "⚠️ Error formatting response"

def get_brand_recommendation(user_id: str, keyword: str, df: pd.DataFrame, top_n: int = 3) -> Optional[Dict[str, Any]]:
    """Get brand recommendations with comprehensive error handling and validation"""
    try:
        # Input validation
        if df is None or df.empty:
            logger.error("Dataset not available")
            return None
        
        if not user_id or not isinstance(user_id, str):
            logger.warning("Invalid user_id provided")
            return None
        
        if not keyword or not isinstance(keyword, str):
            logger.warning("Invalid keyword provided")
            return None
        
        user_id = user_id.strip()
        keyword = keyword.lower().strip()
        
        if not user_id or not keyword:
            return None
        
        # Search in multiple columns with error handling
        try:
            sub_df = df[
                df['SUBCATEGORY'].str.contains(keyword, na=False, case=False) |
                df['CATEGORY'].str.contains(keyword, na=False, case=False) |
                df['PRODUCT_NAME'].str.contains(keyword, na=False, case=False)
            ]
        except Exception as e:
            logger.error(f"Error searching dataset: {e}")
            return None
        
        if sub_df.empty:
            logger.info(f"No products found for keyword: {keyword}")
            return None
        
        # Check user's own history first
        user_df = sub_df[sub_df['tid'] == user_id]
        if not user_df.empty:
            try:
                primary_brands = user_df['BRAND'].value_counts().head(top_n).index.tolist()
                tried_brands = user_df['BRAND'].unique()
                
                # Get exploratory brands (not tried by user)
                exploratory_df = sub_df[~sub_df['BRAND'].isin(tried_brands)]
                exploratory_brands = exploratory_df['BRAND'].value_counts().head(top_n).index.tolist()
                
                return {
                    "PRODUCT_NAME": keyword.title(),
                    "Primary_Brand": primary_brands[0] if primary_brands else "null",
                    "Exploratory_Brand": exploratory_brands[0] if exploratory_brands else "null",
                    "message": "Based on your shopping history:"
                }
            except Exception as e:
                logger.error(f"Error processing user history: {e}")
        
        # Fallback to similar users
        try:
            similar_users = similar_users_dict.get(user_id, [])
            if similar_users:
                for sim_user in similar_users:
                    if not isinstance(sim_user, str):
                        continue
                    
                    sim_df = sub_df[sub_df['tid'] == sim_user]
                    if not sim_df.empty:
                        primary_brands = sim_df['BRAND'].value_counts().head(top_n).index.tolist()
                        return {
                            "PRODUCT_NAME": keyword.title(),
                            "Primary_Brand": "null",
                            "Exploratory_Brand": primary_brands[0] if primary_brands else "null",
                            "message": "Based on users similar to you:"
                        }
        except Exception as e:
            logger.warning(f"Error processing similar users: {e}")
        
        # Final fallback to general popular brands
        try:
            popular_brands = sub_df['BRAND'].value_counts().head(top_n).index.tolist()
            return {
                "PRODUCT_NAME": keyword.title(),
                "Primary_Brand": "null",
                "Exploratory_Brand": popular_brands[0] if popular_brands else "null",
                "message": f"Popular brands for {keyword.title()}:"
            }
        except Exception as e:
            logger.error(f"Error getting popular brands: {e}")
            return None
        
    except Exception as e:
        logger.error(f"Error in get_brand_recommendation: {e}")
        return None
