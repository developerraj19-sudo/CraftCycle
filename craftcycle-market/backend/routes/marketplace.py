"""
craftcycle/backend/app/routes/marketplace.py
──────────────────────────────────────────────
Scrap material listings (buy/sell raw waste).

Endpoints:
  GET    /api/v1/marketplace/            — List with filters & pagination
  POST   /api/v1/marketplace/            — Create listing  (seller only)
  GET    /api/v1/marketplace/<id>        — Get single listing
  PUT    /api/v1/marketplace/<id>        — Update listing   (owner/admin)
  DELETE /api/v1/marketplace/<id>        — Delete listing   (owner/admin)
  GET    /api/v1/marketplace/categories  — Category counts
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from .extensions import db
from .models.user import User
from .models.scrap_material import ScrapMaterial, VALID_CATEGORIES, VALID_QUALITIES
from .utils.validators import sanitize_string, is_positive_number

marketplace_bp = Blueprint("marketplace", __name__)


# ── GET / ─────────────────────────────────────────────────────
@marketplace_bp.get("/")
def list_listings():
    page       = int(request.args.get("page", 1))
    per_page   = min(int(request.args.get("per_page", 20)), 50)
    category   = request.args.get("category")
    quality    = request.args.get("quality")
    min_price  = request.args.get("min_price", type=float)
    max_price  = request.args.get("max_price", type=float)
    city       = request.args.get("city")
    barter     = request.args.get("barter")        # "true" / "false"
    search     = request.args.get("search", "").strip()

    q = ScrapMaterial.query.filter_by(status="active")

    if category and category in VALID_CATEGORIES:
        q = q.filter(ScrapMaterial.category == category)
    if quality and quality in VALID_QUALITIES:
        q = q.filter(ScrapMaterial.quality == quality)
    if min_price is not None:
        q = q.filter(ScrapMaterial.total_price >= min_price)
    if max_price is not None:
        q = q.filter(ScrapMaterial.total_price <= max_price)
    if city:
        q = q.filter(ScrapMaterial.location_city.ilike(f"%{city}%"))
    if barter == "true":
        q = q.filter(ScrapMaterial.is_barter_ok == True)
    if search:
        like = f"%{search}%"
        q = q.filter(
            db.or_(
                ScrapMaterial.title.ilike(like),
                ScrapMaterial.description.ilike(like),
            )
        )

    q = q.order_by(ScrapMaterial.created_at.desc())
    paged = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        listings=[l.to_dict() for l in paged.items],
        pagination={
            "page":  paged.page,
            "pages": paged.pages,
            "total": paged.total,
            "per_page": per_page,
        },
    ), 200


# ── POST / ────────────────────────────────────────────────────
@marketplace_bp.post("/")
@jwt_required()
def create_listing():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_seller:
        return jsonify(error="Only sellers can create listings."), 403

    data = request.get_json(silent=True) or {}

    # Required fields
    title       = sanitize_string(data.get("title", ""))
    description = sanitize_string(data.get("description", ""))
    category    = data.get("category", "")
    quality     = data.get("quality", "good")
    quantity_kg = data.get("quantity_kg")
    price_per_kg= data.get("price_per_kg")

    errors = {}
    if not title:             errors["title"]       = "Title is required."
    if not description:       errors["description"] = "Description is required."
    if category not in VALID_CATEGORIES:
        errors["category"] = f"Category must be one of: {', '.join(VALID_CATEGORIES)}."
    if quality not in VALID_QUALITIES:
        errors["quality"]  = f"Quality must be one of: {', '.join(VALID_QUALITIES)}."
    if not is_positive_number(quantity_kg):
        errors["quantity_kg"] = "Enter a valid quantity greater than 0."
    if not is_positive_number(price_per_kg):
        errors["price_per_kg"] = "Enter a valid price greater than 0."
    if errors:
        return jsonify(error="Validation failed", details=errors), 422

    qty   = float(quantity_kg)
    price = float(price_per_kg)

    listing = ScrapMaterial(
        seller_id      = user_id,
        title          = title,
        description    = description,
        category       = category,
        quality        = quality,
        quantity_kg    = qty,
        price_per_kg   = price,
        total_price    = round(qty * price, 2),
        location_city  = sanitize_string(data.get("location_city", "")),
        location_state = sanitize_string(data.get("location_state", "")),
        is_barter_ok   = bool(data.get("is_barter_ok", False)),
        barter_for     = sanitize_string(data.get("barter_for", "")),
        images         = data.get("images", []),
        tags           = data.get("tags", []),
        status         = "active",
    )
    db.session.add(listing)
    db.session.commit()

    return jsonify(message="Listing created.", listing=listing.to_dict()), 201


# ── GET /<id> ─────────────────────────────────────────────────
@marketplace_bp.get("/<int:listing_id>")
def get_listing(listing_id):
    listing = ScrapMaterial.query.get_or_404(listing_id)

    # Increment view count
    listing.view_count += 1
    db.session.commit()

    return jsonify(listing=listing.to_dict()), 200


# ── PUT /<id> ─────────────────────────────────────────────────
@marketplace_bp.put("/<int:listing_id>")
@jwt_required()
def update_listing(listing_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    listing = ScrapMaterial.query.get_or_404(listing_id)

    if listing.seller_id != user_id and not user.is_admin:
        return jsonify(error="You can only edit your own listings."), 403

    data = request.get_json(silent=True) or {}
    allowed = ["title","description","quality","quantity_kg","price_per_kg",
               "location_city","location_state","is_barter_ok","barter_for","images","tags","status"]

    for field in allowed:
        if field in data:
            setattr(listing, field, data[field])

    # Recalculate total price if either component changed
    if "quantity_kg" in data or "price_per_kg" in data:
        listing.total_price = round(float(listing.quantity_kg) * float(listing.price_per_kg), 2)

    db.session.commit()
    return jsonify(message="Listing updated.", listing=listing.to_dict()), 200


# ── DELETE /<id> ──────────────────────────────────────────────
@marketplace_bp.delete("/<int:listing_id>")
@jwt_required()
def delete_listing(listing_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    listing = ScrapMaterial.query.get_or_404(listing_id)

    if listing.seller_id != user_id and not user.is_admin:
        return jsonify(error="You can only delete your own listings."), 403

    listing.status = "suspended"   # soft delete
    db.session.commit()
    return jsonify(message="Listing removed."), 200


# ── GET /categories ───────────────────────────────────────────
@marketplace_bp.get("/categories")
def categories():
    rows = (
        db.session.query(ScrapMaterial.category, db.func.count(ScrapMaterial.id).label("count"))
        .filter_by(status="active")
        .group_by(ScrapMaterial.category)
        .all()
    )
    result = [{"name": r.category, "count": r.count} for r in rows]
    # Include empty categories
    existing = {r["name"] for r in result}
    for cat in VALID_CATEGORIES:
        if cat not in existing:
            result.append({"name": cat, "count": 0})
    return jsonify(categories=result), 200
