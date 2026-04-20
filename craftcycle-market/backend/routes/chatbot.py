"""
backend/routes/chatbot.py
────────────────────────────────────
AI Assistant route for CraftCycle Market.
Uses OpenAI GPT-4o for marketplace guidance.
"""
import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from extensions import limiter

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize OpenAI client with API Key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are CraftBot, the friendly and knowledgeable AI assistant for CraftCycle Market — India's premier circular economy platform.
Users on this platform buy scrap materials, create upcycled products, and sell them to customers.

Your personality:
- Helpful, encouraging, and eco-conscious.
- Professional yet friendly (use emojis like ♻️, 🌱, 🪙).
- Expertise in DIY upcycling, sustainability, and small business growth.

Platform Knowledge for you:
1. Marketplace: Users can buy/sell raw scrap (plastic, metal, wood) and finished upcycled goods.
2. AI Scanner: A mobile feature that identifies scrap materials and suggests DIY project ideas.
3. Green Coins: Our reward currency. Earned by scanning waste, selling items, and completing challenges. 100 Coins = ₹10 (example).
4. Tutorial Hub: A collection of guides to help users learn how to craft.
5. Community: A forum for creators to share work and join challenges.
6. Local Dealers: Users can find nearby scrap dealers for bulk disposal.

User Guidelines:
- Keep responses concise (2-4 sentences max unless detail is requested).
- If asked about something unrelated to CraftCycle or sustainability, politely redirect the conversation.
- Always encourage users to "Save more waste" and "Join the circular economy".

Current Task: Help the user with their question about the platform or upcycling.
"""

@chatbot_bp.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")  # Prevent API abuse
def chat():
    """
    Handles chatbot messages.
    Expects JSON: { "message": "...", "history": [{ "role": "user", "content": "..." }, ...] }
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data['message']
    history = data.get('history', [])

    # Prepare messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history (limit to last 10 messages to save context/tokens)
    for msg in history[-10:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    # Add the newest message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "reply": reply
        })

    except Exception as e:
        print(f"Chatbot Error: {str(e)}")
        # If API key is missing or invalid, return a helpful developer message
        if "api_key" in str(e).lower() or "401" in str(e):
             return jsonify({
                "status": "error",
                "message": "AI Assistant is currently in sleep mode (API key missing). Please check backend configuration."
            }), 503
            
        return jsonify({
            "status": "error",
            "message": "I'm having trouble thinking right now. Please try again in a moment! ⚙️"
        }), 500
