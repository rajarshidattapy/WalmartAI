from flask import Flask, request, jsonify, send_from_directory
import logging
import os
import pandas as pd
import sys

# Add assistant_chatbot directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'assistant_chatbot'))

from gemini import initialize_app, get_gemini_response
from recommendation import detect_intent, extract_keyword, format_response, get_brand_recommendation
from restocking import initialize_restocking, check_restock_status
from RAG import rag_product_analysis, detect_rag_intent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="UI", static_url_path="")

if not initialize_app():
    logger.error("❌ Failed to initialize Gemini application")

if not initialize_restocking():
    logger.error("❌ Failed to initialize restocking module")

from gemini import df, model
from restocking import df_predictions

UI_PUBLIC_FOLDER = os.path.join(os.path.dirname(__file__), "UI", "public")

# ---------------------------- Routes ----------------------------

@app.route("/")
def home():
    try:
        return app.send_static_file("index.html")
    except Exception as e:
        logger.error(f"Error serving UI: {e}")
        return "⚠️ Error loading UI. Check logs.", 500

@app.route("/UI/public/<path:filename>")
def serve_public_assets(filename):
    try:
        return send_from_directory(UI_PUBLIC_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving public asset '{filename}': {e}")
        return f"❌ File '{filename}' not found", 404

@app.route("/health")
def health():
    try:
        dataset_status = df is not None and not df.empty
        gemini_status = model is not None
        restocking_status = df_predictions is not None and not df_predictions.empty

        overall_healthy = dataset_status and gemini_status and restocking_status

        status = {
            "status": "healthy" if overall_healthy else "degraded",
            "dataset_loaded": dataset_status,
            "gemini_configured": gemini_status,
            "restocking_loaded": restocking_status,
            "timestamp": pd.Timestamp.now().isoformat()
        }

        if not overall_healthy:
            status["warnings"] = []
            if not dataset_status:
                status["warnings"].append("Dataset not loaded")
            if not gemini_status:
                status["warnings"].append("Gemini API not configured")
            if not restocking_status:
                status["warnings"].append("Restocking predictions not loaded")

        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": pd.Timestamp.now().isoformat()
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not request.is_json:
            return jsonify({"reply": "❗ Invalid request format. Expected JSON."}), 400

        data = request.get_json()
        user_id = data.get("user_id", "").strip()
        query = data.get("query", "").strip()

        if not user_id or not query:
            return jsonify({"reply": "❗ Please enter both User ID and your message."}), 400

        if df is None:
            return jsonify({"reply": "⚠️ Application not initialized. Contact admin."}), 500

        intent = detect_intent(query)
        rag_intent = detect_rag_intent(query)

        try:
            if intent == "restock_check":
                reply = check_restock_status(user_id)
            elif rag_intent == "rag_query":
                reply = rag_product_analysis(user_id, query)
            elif intent == "gemini_query":
                reply = get_gemini_response(query, user_id)
            elif intent == "brand_suggestion":
                keyword = extract_keyword(query)
                if not keyword:
                    reply = "⚠️ Please specify what product you're looking for. Try: 'Suggest brands for cola'"
                else:
                    recs = get_brand_recommendation(user_id, keyword, df)
                    reply = format_response(recs) if recs else f"⚠️ No suggestions found for '{keyword}'."
            else:
                reply = (
                    "🤖 I'm your shopping assistant!\n\n"
                    "💡 Try:\n"
                    "• 'Check if to be restocked'\n"
                    "• 'Suggest brands for cola'\n"
                    "• 'walmart am I having too much cola'\n"
                    "• 'walmart what have I bought the most'\n"
                    "• 'Recommend brands for shampoo'"
                )
        except Exception as e:
            logger.error(f"Error handling chat request: {e}")
            reply = "⚠️ Something went wrong while processing your query."

        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"reply": "⚠️ Internal server error."}), 500

# ---------------------------- Run ----------------------------
if __name__ == "__main__":
    if df is not None:
        logger.info("✅ Application initialized successfully")
        logger.info("🌐 Open http://localhost:5000 to access the UI")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        logger.error("❌ Initialization failed. Check logs.")
