"""
backend/routes/chatbot.py
────────────────────────────────────
AI Assistant route for CraftCycle Market.
[V3.0] Gemini Integration.
"""
import os
from flask import Blueprint, request, jsonify
import google.generativeai as genai
from extensions import limiter

chatbot_bp = Blueprint('chatbot', __name__)

def configure_gemini():
    """Configure Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True

SYSTEM_PROMPT = """You are CraftBot, the expert AI Assistant for CraftCycle Market. 
CraftCycle is a premium circular economy platform where users transform waste into wealth.

### YOUR PROFILE:
- Personality: Professional, visionary, and encouraging. 
- Goal: Help users build sustainable businesses.

### KEY INFO:
- 100 Green Coins = ₹10.
- AI Scanner analyses waste and suggests 3 product ideas.
- Marketplace: Buy/sell scrap and upcycled goods.

### CRITICAL RULES:
1. You must ONLY answer questions related to CraftCycle, upcycling, scrap materials, sustainability, DIY crafts, circular economy, and the features of this platform.
2. If the user asks about ANYTHING unrelated (e.g., coding, politics, math, general trivia, recipes), you MUST politely refuse to answer. Say: "I am CraftBot, and I can only assist you with topics related to CraftCycle, upcycling, and sustainability. How can I help you with your green journey today?"
3. Keep answers professional and concise. Do not speak about unrelated topics.
"""

@chatbot_bp.route('/chat', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "Message is required"}), 400

    user_message = data['message']
    history = data.get('history', [])

    if not configure_gemini():
        return jsonify({
            "status": "error",
            "message": "AI Key Missing. Please add GEMINI_API_KEY to Render Environment Variables."
        }), 503

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-flash-latest"
    ]
    
    last_error_str = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT
            )

            formatted_history = []
            for msg in history[-5:]:
                role = "model" if msg.get("role") in ["assistant", "bot", "model"] else "user"
                formatted_history.append({"role": role, "parts": [msg.get("content", "")]})

            chat_session = model.start_chat(history=formatted_history)
            response = chat_session.send_message(user_message)

            return jsonify({
                "status": "success",
                "reply": response.text,
                "model_used": model_name
            })
        except Exception as e:
            error_str = str(e)
            print(f"ChatBot Model {model_name} failed: {error_str}")
            last_error_str = error_str
            # Move to next model on failure
            continue

    # If all models fail
    if last_error_str and ("429" in last_error_str or "ResourceExhausted" in last_error_str or "quota" in last_error_str.lower()):
        return jsonify({
            "status": "error",
            "message": "All Google Gemini AI models are currently at maximum capacity. Your free tier quota is exhausted. Please wait a minute or upgrade your API key."
        }), 429
        
    return jsonify({
        "status": "error",
        "message": "AI model failed. Please try again later."
    }), 500
