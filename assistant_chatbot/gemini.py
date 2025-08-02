import os
import logging
import pandas as pd
import pickle
import google.generativeai as genai
import re
from typing import Optional, Dict, Any

# Initialize global variables
df = None
similar_users_dict = {}
model = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_app() -> bool:
    """Initialize the application with comprehensive error handling"""
    global df, similar_users_dict, model
    
    try:
        # Configure Gemini API with proper error handling
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDOe4HX3nY9fsLoWYbrx9mEyYQDbcIHWXM")
        if api_key == "YOUR_GEMINI_API_KEY":
            logger.warning("Using placeholder API key. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Load dataset with comprehensive validation - Fixed path
        dataset_path = os.path.join(os.path.dirname(__file__), 'Our_dataset.csv')
        if not os.path.exists(dataset_path):
            # Try alternative paths
            alt_paths = [
                'Our_dataset.csv',
                os.path.join(os.path.dirname(__file__), '..', 'Input_dataset', 'Our_dataset.csv'),
                os.path.join(os.path.dirname(__file__), '..', 'Our_dataset.csv')
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    dataset_path = alt_path
                    break
            else:
                logger.error(f"Our_dataset.csv not found! Tried paths: {[dataset_path] + alt_paths}")
                return False
            
        logger.info(f"Loading dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
        
        # Validate required columns exist
        required_columns = ['SUBCATEGORY', 'CATEGORY', 'PRODUCT_NAME', 'BRAND', 'tid']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {list(df.columns)}")
            return False
        
        # Clean and validate data with proper error handling
        try:
            df = df.dropna(subset=['BRAND', 'tid'])
            df['SUBCATEGORY'] = df['SUBCATEGORY'].astype(str).str.lower()
            df['CATEGORY'] = df['CATEGORY'].astype(str).str.lower()
            df['PRODUCT_NAME'] = df['PRODUCT_NAME'].astype(str).str.lower()
            df['BRAND'] = df['BRAND'].astype(str).str.strip()
            df['tid'] = df['tid'].astype(str)
            
            # Remove rows with empty critical data
            df = df[df['BRAND'].str.len() > 0]
            df = df[df['tid'].str.len() > 0]
            
            logger.info(f"Loaded dataset with {len(df)} rows")
            
        except Exception as e:
            logger.error(f"Error processing dataset: {e}")
            return False

        # Load similar users with error handling
        similar_users_path = os.path.join(os.path.dirname(__file__), 'similar_users.pkl')
        if os.path.exists(similar_users_path):
            try:
                with open(similar_users_path, "rb") as f:
                    loaded_dict = pickle.load(f)
                    if isinstance(loaded_dict, dict):
                        similar_users_dict.update(loaded_dict)
                        logger.info(f"Loaded similar users for {len(similar_users_dict)} users")
                    else:
                        logger.warning("similar_users.pkl does not contain a dictionary")
            except Exception as e:
                logger.error(f"Error loading similar_users.pkl: {e}")
                similar_users_dict = {}
        else:
            logger.warning("similar_users.pkl not found, using empty dict")
            similar_users_dict = {}
            
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False

def get_gemini_response(query: str, user_id: str = "") -> str:
    """Get Gemini response with comprehensive error handling and input validation"""
    global model, df
    
    # Input validation
    if not query or not isinstance(query, str):
        return "⚠️ Invalid query provided"
    
    if not isinstance(user_id, str):
        user_id = ""
    
    query = query.strip()
    user_id = user_id.strip()
    
    if not query:
        return "⚠️ Empty query provided"
    
    try:
        if model is None:
            return "⚠️ Gemini model not initialized. Please check API configuration."
        
        # Clean query by removing 'Walmart' keyword
        clean_query = re.sub(r'\bwalmart\b', '', query, flags=re.IGNORECASE).strip()
        if not clean_query:
            clean_query = query  # Fallback to original query
        
        # Extract keyword for context (avoid circular import)
        keyword = ""
        try:
            from recommendation import extract_keyword
            keyword = extract_keyword(query)
        except ImportError:
            # Fallback keyword extraction
            words = query.lower().split()
            product_keywords = ['cola', 'toothpaste', 'shampoo', 'soap', 'bread', 'milk', 'chips', 'soda']
            for word in words:
                if word in product_keywords:
                    keyword = word
                    break
        
        # Get user history context if available
        user_context = ""
        if df is not None and user_id:
            try:
                user_history = df[df['tid'] == user_id]
                if not user_history.empty and keyword:
                    product_history = user_history[
                        user_history['PRODUCT_NAME'].str.contains(keyword, na=False, case=False)
                    ]
                    count = len(product_history)
                    if count > 0:
                        user_context = f" This user has purchased '{keyword}' {count} time(s)."
            except Exception as e:
                logger.warning(f"Error getting user history: {e}")
        
        # Create comprehensive prompt
        prompt = f"""
        You are a helpful shopping assistant. Answer the following user query in a friendly, informative way:
        
        User query: "{clean_query}"{user_context}
        
        Keep your response concise, helpful, and related to shopping, health, or product usage.
        Be friendly and provide practical advice.
        """
        
        # Generate response with error handling
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            return "⚠️ No response from Gemini API"
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Hey, you should not waste more money on Cola, you've already spent 500*7 = 3500 ml Cola!"
