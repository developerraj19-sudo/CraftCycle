"""
craftcycle/backend/app/routes/products.py
───────────────────────────────────────────
Finished upcycled products for sale.

Endpoints:
  GET    /api/v1/products/        — List products (filters, pagination)
  POST   /api/v1/products/        — Create product (seller only)
  GET    /api/v1/products/<id>    — Get product detail
  PUT    /api/v1/products/<id>    — Update product (owner/admin)
  DELETE /api/v1/products/<id>    — Delete product (owner/admin)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.user import User
from models.product import Product
from utils.validators import sanitize_string, is_positive_number

products_bp = Blueprint("products", __name__)


# ── GET / ─────────────────────────────────────────────────────
@products_bp.get("/")
def list_products():
    page     = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 50)
    category = request.args.get("category")
    min_price= request.args.get("min_price", type=float)
    max_price= request.args.get("max_price", type=float)
    search   = request.args.get("search", "").strip()
    seller_id= request.args.get("seller_id", type=int)
    sort     = request.args.get("sort", "newest")  # newest | price_asc | price_desc | popular

    q = Product.query
    if not seller_id:
        q = q.filter_by(status="active")
    # If seller_id is provided, we might want to show all their products (including pending/suspended)
    # but for public listing, we usually only show active.
    # However, for the seller dashboard 'my-products', we need to show all.
    # So if seller_id is requested, we show all for that seller.
    # If it's a general list, we only show active.

    if category:
        q = q.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if seller_id:
        q = q.filter(Product.seller_id == seller_id)
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(Product.title.ilike(like), Product.description.ilike(like)))

    # Sorting
    sort_map = {
        "newest":     Product.created_at.desc(),
        "price_asc":  Product.price.asc(),
        "price_desc": Product.price.desc(),
        "popular":    Product.view_count.desc(),
    }
    q = q.order_by(sort_map.get(sort, Product.created_at.desc()))

    paged = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        products=[p.to_dict() for p in paged.items],
        pagination={
            "page":  paged.page,
            "pages": paged.pages,
            "total": paged.total,
        },
    ), 200


# ── POST / ────────────────────────────────────────────────────
@products_bp.post("/")
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_seller:
        return jsonify(error="Only sellers can create products."), 403
    if not user.is_verified:
        return jsonify(error="Your seller account must be verified by an admin before you can create products."), 403

    data = request.get_json(silent=True) or {}
    errors = {}

    title    = sanitize_string(data.get("title", ""))
    desc     = sanitize_string(data.get("description", ""))
    category = sanitize_string(data.get("category", ""))
    price    = data.get("price")

    if not title:               errors["title"]       = "Title is required."
    if not desc:                errors["description"] = "Description is required."
    if not category:            errors["category"]    = "Category is required."
    if not is_positive_number(price): errors["price"] = "Enter a valid price."
    if errors:
        return jsonify(error="Validation failed", details=errors), 422

    product = Product(
        seller_id     = user_id,
        title         = title,
        description   = desc,
        category      = category,
        price         = float(price),
        stock_qty     = int(data.get("stock_qty", 1)),
        images        = data.get("images", []),
        materials_used= sanitize_string(data.get("materials_used", "")),
        waste_kg_saved= float(data.get("waste_kg_saved", 0)),
        co2_kg_saved  = float(data.get("co2_kg_saved", 0)),
        time_to_make_h= data.get("time_to_make_h"),
        difficulty    = data.get("difficulty", "medium"),
        status        = "active",
    )
    db.session.add(product)
    db.session.commit()

    return jsonify(
        message="Product submitted for review. You'll be notified once approved.",
        product=product.to_dict(),
    ), 201


# ── GET /<id> ─────────────────────────────────────────────────
@products_bp.get("/<int:product_id>")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.view_count += 1
    db.session.commit()
    return jsonify(product=product.to_dict()), 200


# ── PUT /<id> ─────────────────────────────────────────────────
@products_bp.put("/<int:product_id>")
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.seller_id != user_id and not user.is_admin:
        return jsonify(error="Permission denied."), 403

    data = request.get_json(silent=True) or {}
    allowed = ["title","description","category","price","stock_qty","images",
               "materials_used","waste_kg_saved","co2_kg_saved","time_to_make_h","difficulty","status"]
    for f in allowed:
        if f in data:
            setattr(product, f, data[f])

    db.session.commit()
    return jsonify(message="Product updated.", product=product.to_dict()), 200


# ── DELETE /<id> ──────────────────────────────────────────────
@products_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.seller_id != user_id and not user.is_admin:
        return jsonify(error="Permission denied."), 403

    product.status = "suspended"
    db.session.commit()
    return jsonify(message="Product removed."), 200
