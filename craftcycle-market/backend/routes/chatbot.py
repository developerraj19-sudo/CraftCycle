"""
backend/routes/chatbot.py
────────────────────────────────────
AI Assistant route for CraftCycle Market.
Uses OpenAI GPT-4o for professional marketplace guidance.
"""
import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from extensions import limiter

chatbot_bp = Blueprint('chatbot', __name__)

def get_openai_client():
    """Lazily initialize OpenAI client to handle late-loading environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None

SYSTEM_PROMPT = """You are CraftBot, the expert AI Assistant for CraftCycle Market. 
CraftCycle is a premium circular economy platform where users transform waste into wealth.

### YOUR PROFILE:
- Personality: Highly professional, visionary, encouraging, and eco-conscious. 
- Goal: To turn every user into a successful sustainable entrepreneur.
- Language: Professional English (India) with a touch of modern tech-enthusiasm.

### PLATFORM EXPERTISE (USE THIS TO ANSWER):
1. THE CORE CYCLE: Users buy raw scrap (wood offcuts, metal, plastic bales), use our Tutorial Hub to learn crafting, and sell finished DIY creations in the Marketplace.
2. AI SCANNER: A powerful GPT-4o Vision tool that analyzes waste photos and suggests 3 upcycling product ideas with difficulty levels, steps, and estimated resale value.
3. GREEN COINS (THE ECONOMY):
   - 100 Green Coins = ₹10 (Marketplace credit).
   - EARN: +2 per AI Scan, +5 per marketplace listing, +10 for completing community challenges.
   - SPEND: Discounts on scrap materials and exclusive DIY kits.
4. MARKETPLACE RULES:
   - Raw materials must be clean and sorted.
   - DIY products must be at least 70% upcycled material.
   - All sellers are verified for quality.

### UPCYCLING GUIDELINES:
- PLASTIC: Focus on PET (bottles) and HDPE (containers). Suggest weaving, heat-shaping, or multi-purpose planters.
- WOOD: Teak and Pine pallet offcuts are highly sought after. Suggest rustic furniture and minimal décor.
- METAL: Scrap gears and rods. Suggest industrial-style lighting and garden sculptures.

Keep answers professional, insightful, and concise (max 4 sentences unless instructions are requested). Always encourage users to save waste! 🌱
"""

@chatbot_bp.route('/ping', methods=['GET'], strict_slashes=False)
def ping():
    """Simple connectivity check."""
    return jsonify({
        "status": "success",
        "message": "Chatbot API is operational",
        "openai_configured": os.getenv("OPENAI_API_KEY") is not None
    }), 200

@chatbot_bp.route('/chat', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def chat():
    """Handles professional AI chat sessions."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "Message is required"}), 400

    user_message = data['message']
    history = data.get('history', [])

    client = get_openai_client()
    if not client:
        return jsonify({
            "status": "error",
            "message": "Local setup error: OpenAI API Key is missing on the server. Please check Environment Variables."
        }), 503

    # Prepare message context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "reply": reply
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Chatbot Critical Error: {error_msg}")
        return jsonify({
            "status": "error",
            "message": f"AI Engine Exception: {error_msg}"
        }), 500
