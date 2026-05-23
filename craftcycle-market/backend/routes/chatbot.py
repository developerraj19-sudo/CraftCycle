"""
backend/routes/chatbot.py
────────────────────────────────────
AI Assistant route for CraftCycle Market.
[V2.4] Final Connectivity Fix with Fallback.
"""
import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from extensions import limiter

chatbot_bp = Blueprint('chatbot', __name__)

def get_openai_client():
    """Lazily initialize OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are CraftBot, the expert AI Assistant for CraftCycle Market. 
CraftCycle is a premium circular economy platform where users transform waste into wealth.

### YOUR PROFILE:
- Personality: Professional, visionary, and encouraging. 
- Goal: Help users build sustainable businesses.

### KEY INFO:
- 100 Green Coins = ₹10.
- AI Scanner analyses waste and suggests 3 프로젝트 ideas.
- Marketplace: Buy/sell scrap and upcycled goods.

Keep answers professional and concise.
"""

@chatbot_bp.route('/chat', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "Message is required"}), 400

    user_message = data['message']
    history = data.get('history', [])

    client = get_openai_client()
    if not client:
        return jsonify({
            "status": "error",
            "message": "AI Key Missing. Please add OPENAI_API_KEY to Render Environment Variables."
        }), 503

    # Prepare context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-5:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    # Try different models in order of preference
    # Some accounts don't have access to gpt-4o yet
    models_to_try = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    last_error = ""

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return jsonify({
                "status": "success",
                "reply": response.choices[0].message.content,
                "model_used": model
            })
        except Exception as e:
            last_error = str(e)
            print(f"Model {model} failed: {last_error}")
            
            # If quota is exceeded, no point in trying other models
            if "insufficient_quota" in last_error or "quota" in last_error.lower():
                return jsonify({
                    "status": "error",
                    "message": "OpenAI Account balance is $0. Please add credits at platform.openai.com/usage."
                }), 503
            
            # Continue to next model for other errors
            continue

    # If all models failed
    return jsonify({
        "status": "error",
        "message": "All AI models failed. Please try again later."
    }), 500
