"""
craftcycle/backend/app/routes/admin.py
───────────────────────────────────────
Admin-only endpoints. Every route verifies role=admin.

Endpoints:
  GET    /api/v1/admin/dashboard         — Platform KPIs
  GET    /api/v1/admin/users             — Paginated user list
  PUT    /api/v1/admin/users/<id>        — Update user (role, status, coins)
  GET    /api/v1/admin/products          — Products moderation queue
  PUT    /api/v1/admin/products/<id>     — Approve / reject product
  GET    /api/v1/admin/analytics         — 30-day chart data
"""
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .extensions import db
from .models.user import User
from .models.product import Product
from .models.scrap_material import ScrapMaterial
from .models.coin_transaction import CoinTransaction

admin_bp = Blueprint("admin", __name__)


# ── Admin guard decorator ─────────────────────────────────────
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify(error="Admin access required."), 403
        return fn(*args, **kwargs)
    return wrapper


# ── GET /dashboard ────────────────────────────────────────────
@admin_bp.get("/dashboard")
@admin_required
def dashboard():
    now        = datetime.utcnow()
    month_ago  = now - timedelta(days=30)

    total_users     = User.query.count()
    new_this_month  = User.query.filter(User.created_at >= month_ago).count()
    total_sellers   = User.query.filter_by(role="seller").count()
    total_active    = Product.query.filter_by(status="active").count()
    pending_approval= Product.query.filter_by(status="pending").count()

    # Revenue = sum of all product prices sold (approximation using order items if available)
    total_waste = db.session.query(
        db.func.coalesce(db.func.sum(Product.waste_kg_saved), 0)
    ).scalar()
    total_co2   = db.session.query(
        db.func.coalesce(db.func.sum(Product.co2_kg_saved), 0)
    ).scalar()

    # Recent 5 users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return jsonify(
        kpis={
            "total_users":          total_users,
            "new_users_this_month": new_this_month,
            "total_sellers":        total_sellers,
            "total_active_products":total_active,
            "pending_approval":     pending_approval,
            "total_waste_kg":       float(total_waste),
            "total_co2_kg":         float(total_co2),
        },
        recent_users=[u.to_public_dict() for u in recent_users],
    ), 200


# ── GET /users ────────────────────────────────────────────────
@admin_bp.get("/users")
@admin_required
def list_users():
    page     = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    role     = request.args.get("role")
    active   = request.args.get("active")   # "true" / "false"
    search   = request.args.get("search", "").strip()

    q = User.query
    if role in ("buyer","seller","admin"):
        q = q.filter_by(role=role)
    if active == "true":
        q = q.filter_by(is_active=True)
    elif active == "false":
        q = q.filter_by(is_active=False)
    if search:
        like = f"%{search}%"
        q = q.filter(
            db.or_(
                User.username.ilike(like),
                User.email.ilike(like),
                User.full_name.ilike(like),
            )
        )

    q = q.order_by(User.created_at.desc())
    paged = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        users=[u.to_private_dict() for u in paged.items],
        pagination={
            "page":  paged.page,
            "pages": paged.pages,
            "total": paged.total,
        },
    ), 200


# ── PUT /users/<id> ───────────────────────────────────────────
@admin_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    current_admin_id = get_jwt_identity()
    target = User.query.get_or_404(user_id)

    data = request.get_json(silent=True) or {}

    # Prevent self-demotion
    if user_id == current_admin_id and "role" in data and data["role"] != "admin":
        return jsonify(error="Admins cannot demote themselves."), 400

    allowed = ["role","is_active","is_verified"]
    for field in allowed:
        if field in data:
            setattr(target, field, data[field])

    # Manual coin adjustment
    if "coin_adjustment" in data:
        adj = int(data["coin_adjustment"])
        target.award_coins(
            adj,
            "admin",
            data.get("coin_reason", f"Admin adjustment: {adj:+d} coins"),
        )

    db.session.commit()
    return jsonify(message="User updated.", user=target.to_private_dict()), 200


# ── GET /products ─────────────────────────────────────────────
@admin_bp.get("/products")
@admin_required
def list_products():
    status   = request.args.get("status", "pending")
    page     = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 50)

    q = Product.query
    if status in ("pending","active","sold_out","suspended"):
        q = q.filter_by(status=status)

    paged = q.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        products=[p.to_dict() for p in paged.items],
        pagination={"page": paged.page, "pages": paged.pages, "total": paged.total},
    ), 200


# ── PUT /products/<id> ────────────────────────────────────────
@admin_bp.put("/products/<int:product_id>")
@admin_required
def moderate_product(product_id):
    product = Product.query.get_or_404(product_id)
    data    = request.get_json(silent=True) or {}
    status  = data.get("status")

    if status not in ("active","suspended","pending"):
        return jsonify(error="Status must be 'active', 'suspended', or 'pending'."), 422

    product.status = status
    db.session.commit()

    # Reward seller on approval
    if status == "active":
        seller = User.query.get(product.seller_id)
        if seller:
            seller.award_coins(5, "sale", f"Product approved: {product.title}", product.id)
            db.session.commit()

    return jsonify(message=f"Product {status}.", product=product.to_dict()), 200


# ── GET /analytics ────────────────────────────────────────────
@admin_bp.get("/analytics")
@admin_required
def analytics():
    """Return 30-day daily signup counts (extend with real orders later)."""
    today = datetime.utcnow().date()
    days  = [(today - timedelta(days=i)) for i in range(29, -1, -1)]

    labels       = [d.strftime("%b %d") for d in days]
    signup_data  = []

    for day in days:
        start = datetime(day.year, day.month, day.day)
        end   = start + timedelta(days=1)
        count = User.query.filter(User.created_at >= start, User.created_at < end).count()
        signup_data.append(count)

    # Placeholder revenue data (replace with real orders sum)
    revenue_data = [count * 1200 for count in signup_data]

    return jsonify(
        chart_labels=labels,
        signups_series=signup_data,
        revenue_series=revenue_data,
    ), 200
