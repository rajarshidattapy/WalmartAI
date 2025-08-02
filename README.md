# 🛒 Walmart AI – Intelligent Shopping & Supply Chain System

## Overview
**SmartCart AI** is a comprehensive retail intelligence platform that combines AI-powered shopping assistance with supply chain optimization. Built on real Walmart product data, this system offers an integrated web application with multiple AI features for both customers and retailers.

---

## 🔍 Core Features

### 🤖 1. AI-Powered Shopping Assistant (Chatbot)
**Problem**: Customers need personalized shopping guidance and product recommendations.

**Solution**:  
A sophisticated chatbot with multiple AI capabilities:
- **Restock Status Check**: "Check if to be restocked" - Shows products due for restocking
- **Brand Recommendations**: "Suggest brands for cola" - Personalized brand suggestions based on purchase history
- **Gemini AI Integration**: "walmart am I having too much cola" - AI-powered health and shopping advice
- **Product Analysis**: "what have I bought the most" - Detailed purchase pattern analysis
- **RAG (Retrieval-Augmented Generation)**: Advanced product usage analysis and health recommendations

**Example Interactions**:
- "Check if to be restocked" → Shows overdue products with restock dates
- "Suggest brands for shampoo" → Returns preferred + exploratory brand recommendations
- "walmart what have I bought the most" → AI analysis of shopping patterns

---

### 📦 2. AI Predictive Restocking Model
**Problem**: Customers frequently forget to restock essentials, leading to last-minute store visits.

**Solution**:  
Advanced ML model that predicts **when customers will run out of products**:
- Analyzes historical purchase patterns per user-product combination
- Estimates family size based on consumption patterns
- Calculates average days between orders
- Predicts next purchase dates using consumption tables
- Provides personalized refill schedules

**Technical Implementation**:
- Uses `AIpredictive.py` for core prediction logic
- Processes `Our_dataset.csv` with purchase history
- References `consumption_table.csv` for family size estimation
- Outputs `predicted_purchases.csv` with restock dates

**Example Output**:
```
User: T7444U658
Product: 1L Milk
Predicted Restock Date: 2024-01-15
Estimated Family Size: 3
Days Between Orders: 5
```

---

### 🛍️ 3. AI-Powered Brand Recommendation Engine
**Problem**: Customers are overwhelmed with brand choices and need personalized recommendations.

**Solution**:  
Intelligent brand recommendation system with:
- **Primary Recommendations**: Most frequently purchased brands by the user
- **Exploratory Brands**: New brands aligned with user preferences
- **Similar User Analysis**: Recommendations based on users with similar patterns
- **Fallback to Popular Brands**: General recommendations when no history exists

**Features**:
- Keyword extraction from natural language queries
- Multi-column product matching (SUBCATEGORY, CATEGORY, PRODUCT_NAME)
- Similar user clustering using `similar_users.pkl`
- 3-tier recommendation system

---

### 🏬 4. AI-Driven Supply Chain Forecasting
**Problem**: Retailers struggle with inventory management due to unpredictable demand.

**Solution**:  
Monthly demand forecasting system that:
- Aggregates predicted purchases by **location**, **product**, and **month**
- Identifies high-demand products for restocking prioritization
- Flags low-demand items to reduce excess inventory
- Provides actionable insights for warehouse planning

**Output Example**:
```
SHIPPING_LOCATION | PRODUCT_NAME | MONTH   | Expected_Units
Los Angeles       | 1L Milk      | 2024-01 | 42
New York          | Cola         | 2024-01 | 28
```

---

## 🚀 Tech Stack

### Backend
- **Flask 2.3.3** - Web framework for API endpoints
- **Pandas 2.2.2** - Data processing and analysis
- **NumPy 1.26.4** - Numerical computations
- **Google Generative AI 0.4.1** - Gemini AI integration
- **Scikit-learn 1.4.1** - Machine learning algorithms

### Frontend
- **HTML5/CSS3** - Modern responsive UI
- **JavaScript** - Interactive chat interface
- **Walmart-themed Design** - Professional retail aesthetic

### Data Pipeline
- **CSV-based Processing** - Efficient data handling
- **Pickle Serialization** - Similar user clustering
- **Modular Architecture** - Separated concerns for maintainability

---

## 📁 Project Structure

```
Walmart_AI/
├── app.py                          # Main Flask application
├── requirements.txt                 # Python dependencies
├── assistant_chatbot/              # Core AI modules
│   ├── gemini.py                  # Gemini AI integration
│   ├── recommendation.py          # Brand recommendation engine
│   ├── restocking.py              # Restock prediction logic
│   ├── RAG.py                     # Advanced product analysis
│   ├── getdata.py                 # Data loading utilities
│   └── Our_dataset.csv            # Main product dataset
├── AI_predictions/                 # ML prediction modules
│   ├── AIpredictive.py           # Core prediction algorithm
│   ├── getdata.py                 # Data preprocessing
│   └── Repeating.py               # Pattern analysis
├── Warehouse_Prediction/           # Supply chain forecasting
│   └── warehouse.py               # Monthly demand forecasting
├── UI/                            # Frontend interface
│   ├── index.html                 # Main web interface
│   └── public/                    # Static assets
├── Input_dataset/                  # Source data
│   ├── Our_dataset.csv            # Product purchase history
│   └── consumption_table.csv      # Family size consumption data
└── Output_dataset/                 # Generated predictions
    ├── predicted_purchases.csv    # Restock predictions
    └── warehouse_forecast.csv     # Supply chain forecasts
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (optional, for enhanced AI features)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Walmart_AI

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
export GEMINI_API_KEY="your_api_key_here"
```

### Running the Application
```bash
# Start the Flask server
python app.py

# Access the application
# Open http://localhost:5000 in your browser
```

### Health Check
```bash
# Check system status
curl http://localhost:5000/health
```

---

## 💬 API Endpoints

### Chat Interface
- **POST** `/chat` - Main chatbot endpoint
  - Requires: `user_id`, `query`
  - Supports: Restock checks, brand recommendations, AI queries

### Health Monitoring
- **GET** `/health` - System health status
  - Returns: Dataset status, AI model status, predictions status

### Static Assets
- **GET** `/UI/public/<filename>` - Serve UI assets

---

## 📊 Data Flow

1. **Input Processing**: `Our_dataset.csv` → Purchase history analysis
2. **ML Prediction**: `AIpredictive.py` → `predicted_purchases.csv`
3. **Supply Chain**: `warehouse.py` → `warehouse_forecast.csv`
4. **Real-time Chat**: User queries → AI processing → Personalized responses

---

## 🎯 Use Cases

### For Customers
- **Smart Restocking**: Never run out of essentials
- **Brand Discovery**: Find new products aligned with preferences
- **Health Insights**: AI-powered shopping advice
- **Purchase Analysis**: Understand spending patterns

### For Retailers
- **Demand Forecasting**: Optimize inventory levels
- **Regional Planning**: Location-based demand insights
- **Product Performance**: Identify high/low demand items
- **Supply Chain Optimization**: Reduce waste and stockouts

---

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key for enhanced AI features
- Default API key provided for demo purposes

### Data Sources
- **Our_dataset.csv**: Main product purchase dataset
- **consumption_table.csv**: Family size consumption patterns
- **similar_users.pkl**: Pre-computed user similarity clusters

---

## 📈 Performance Metrics

- **Prediction Accuracy**: Based on historical purchase patterns
- **Response Time**: < 2 seconds for chat queries
- **Scalability**: Modular architecture supports data growth
- **Reliability**: Comprehensive error handling and logging

---

## 🚀 Future Enhancements

- **Real-time Inventory Integration**: Live stock level monitoring
- **Advanced ML Models**: Deep learning for better predictions
- **Mobile App**: Native iOS/Android applications
- **Multi-language Support**: International market expansion
- **Advanced Analytics Dashboard**: Business intelligence features
- **API Rate Limiting**: Production-ready scaling
- **User Authentication**: Secure user management
- **A/B Testing Framework**: Feature optimization

---

## 🧠 Created For
Walmart Sparkathon hackathon to demonstrate the power of intelligent personalization and operational optimization using machine learning on structured datasets.

### Team:
- **Rajarshi Datta** (Team Leader): created RAG model and chatbot features
- **Rahil Masood**: handled data analysis and exploration
- **Abhay Singh**: handled the UI
- **Gautam Sharma**: handled warehouse backend

---

## 📝 License
This project was created for educational and demonstration purposes as part of the Walmart Sparkathon hackathon.
