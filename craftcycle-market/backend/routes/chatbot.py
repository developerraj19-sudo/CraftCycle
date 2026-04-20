"""
backend/routes/chatbot.py
────────────────────────────────────
AI Assistant route for CraftCycle Market.
[V2.3] Super Diagnostic Version.
"""
import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from extensions import limiter

chatbot_bp = Blueprint('chatbot', __name__)

SYSTEM_PROMPT = """You are CraftBot, the expert AI Assistant for CraftCycle Market. 
CraftCycle is a premium circular economy platform where users transform waste into wealth.

### YOUR PROFILE:
- Personality: Highly professional, visionary, encouraging, and eco-conscious. 
- Goal: To turn every user into a successful sustainable entrepreneur.
- Language: Professional English (India).

### PLATFORM EXPERTISE:
1. THE CORE CYCLE: Users buy raw scrap, learn via Tutorial Hub, and sell DIY creations.
2. AI SCANNER: Uses GPT-4o Vision to analyze waste photos and suggests 3 프로젝트 ideas.
3. GREEN COINS: 100 coins = ₹10. Earned via scanning, listing, and challenges.
4. QUALITY: All DIY products must be high quality and at least 70% upcycled material.

Keep answers professional, insightful, and concise (max 4 sentences).
"""

@chatbot_bp.route('/ping', methods=['GET'], strict_slashes=False)
def ping():
    return jsonify({
        "status": "success",
        "version": "2.3",
        "openai_key_present": os.getenv("OPENAI_API_KEY") is not None
    }), 200

@chatbot_bp.route('/chat', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "[V2.3] Missing message body"}), 400

    user_message = data['message']
    history = data.get('history', [])

    # Dynamic initialization to ensure latest env vars are used
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({
            "status": "error", 
            "message": "[V2.3] Configuration Error: OPENAI_API_KEY is null on Render."
        }), 503

    try:
        client = OpenAI(api_key=api_key)
        
        # Prepare context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history[-8:]: # Keep context shorter for stability
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "reply": reply,
            "api_ver": "2.3"
        })

    except Exception as e:
        error_detail = str(e)
        print(f"Chatbot [V2.3] Error: {error_detail}")
        # RETURN THE EXACT ERROR STRING FOR DEBUGGING
        return jsonify({
            "status": "error",
            "message": f"[V2.3] OpenAI API Error: {error_detail}"
        }), 500
