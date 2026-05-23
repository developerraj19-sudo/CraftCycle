"""
craftcycle/backend/app/routes/scanner.py
──────────────────────────────────────────
AI Trash Scanner — upload a waste image and get product ideas.

Endpoints:
  POST   /api/v1/scanner/analyze    — Analyse image (rate-limited)
  GET    /api/v1/scanner/history    — User's scan history
"""
import hashlib
import base64
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db, limiter
from models.user import User
from models.scanner_history import ScannerHistory
from utils.storage import upload_image

scanner_bp = Blueprint("scanner", __name__)


# ── POST /analyze ─────────────────────────────────────────────
@scanner_bp.post("/analyze")
@jwt_required()
@limiter.limit("5 per hour")    # configurable in .env
def analyze():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error="User not found."), 404

    # Accept image as multipart file
    if "image" not in request.files:
        return jsonify(error="No image file provided."), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify(error="No file selected."), 400

    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"jpg","jpeg","png","webp"})
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify(error=f"Unsupported format. Use: {', '.join(allowed)}."), 415

    image_bytes = file.read()
    if len(image_bytes) > current_app.config["MAX_CONTENT_LENGTH"]:
        return jsonify(error="Image too large. Maximum 10 MB."), 413

    # SHA-256 hash for cache lookup
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    # Cache hit — return stored results
    cached = ScannerHistory.query.filter_by(image_hash=image_hash).first()
    if cached:
        return jsonify(
            material_detected=cached.material_detected,
            suggestions=cached.suggestions,
            coins_earned=0,   # already rewarded
            from_cache=True,
        ), 200

    # ── Call Gemini Vision API ────────────────────────────────
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    if not api_key:
        return jsonify(error="AI scanner not configured.", code="no_api_key"), 503

    try:
        import google.generativeai as genai
        import io
        from PIL import Image
        import re

        genai.configure(api_key=api_key)

        # Gemini supports PIL Image directly
        img = Image.open(io.BytesIO(image_bytes))

        prompt = """
You are an expert at upcycling and circular economy. Analyse the waste material in the image.

Respond ONLY with a valid JSON object — no markdown, no commentary.

{
  "material_detected": "short description of the material",
  "suggestions": [
    {
      "title": "Product name",
      "description": "2–3 sentence description of the product",
      "difficulty": "easy|medium|hard",
      "estimated_time_hours": 2,
      "estimated_resale_value_inr": 500,
      "waste_kg_saved": 0.5,
      "tools_needed": ["Tool 1", "Tool 2"],
      "steps_overview": ["Step 1", "Step 2", "Step 3", "Step 4"]
    }
  ]
}

Provide exactly 3 suggestions, ranging from easy to harder.
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([img, prompt])

        raw = response.text.strip()
        
        # Robust JSON extraction
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        result = json.loads(raw)

    except json.JSONDecodeError:
        return jsonify(error="AI returned an unexpected response. Please try again."), 502
    except Exception as e:
        current_app.logger.error(f"Gemini error: {e}")
        return jsonify(error="AI analysis failed. Please try again later."), 502

    # ── Save to DB + award coins ──────────────────────────────
    coins = current_app.config.get("SCAN_COINS", 2)

    # Upload to Supabase Storage
    image_url = None
    try:
        filename = f"scans/{user_id}/{image_hash[:10]}.{ext}"
        image_url = upload_image(image_bytes, filename)
    except Exception as e:
        current_app.logger.warning(f"Failed to upload scan image to Supabase: {e}")

    scan = ScannerHistory(
        user_id           = user_id,
        image_hash        = image_hash,
        image_url         = image_url,
        material_detected = result.get("material_detected"),
        suggestions       = result.get("suggestions", []),
        coins_earned      = coins,
    )
    db.session.add(scan)
    user.award_coins(coins, "scan", "AI Scanner reward", ref_id=None)
    db.session.commit()

    return jsonify(
        material_detected=result.get("material_detected"),
        suggestions=result.get("suggestions", []),
        coins_earned=coins,
        from_cache=False,
    ), 200


# ── GET /history ──────────────────────────────────────────────
@scanner_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    scans = (
        ScannerHistory.query
        .filter_by(user_id=user_id)
        .order_by(ScannerHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify(scans=[s.to_dict() for s in scans]), 200
