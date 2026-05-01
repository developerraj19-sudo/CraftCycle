"""
craftcycle/backend/app/routes/orders.py
───────────────────────────────────────
Routes for managing orders.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.order import Order, OrderItem
from models.product import Product
from models.scrap_material import ScrapMaterial
from models.user import User

orders_bp = Blueprint("orders", __name__)

@orders_bp.post("/")
@jwt_required()
def create_order():
    """Create a new order."""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "items" not in data:
        return {"error": "Missing order data"}, 400

    shipping = data.get("shipping", {})
    payment = data.get("payment", {})
    
    # Start transaction
    try:
        new_order = Order(
            buyer_id=user_id,
            total_amount=data.get("total_amount", 0),
            delivery_fee=data.get("delivery_fee", 0),
            platform_fee=data.get("platform_fee", 0),
            status="pending",
            full_name=shipping.get("full_name"),
            phone=shipping.get("phone"),
            address_line1=shipping.get("address_line1"),
            address_line2=shipping.get("address_line2"),
            city=shipping.get("city"),
            state=shipping.get("state"),
            pincode=shipping.get("pincode"),
            payment_method=payment.get("method"),
            payment_status="pending"
        )
        db.session.add(new_order)
        db.session.flush()  # Get order ID

        for item in data["items"]:
            # Resolve seller_id from DB; fall back to buyer if item not in DB
            seller_id = None
            product_id = item.get("product_id")
            scrap_id = item.get("scrap_id")

            if product_id:
                product = Product.query.get(product_id)
                if product:
                    if product.status == "sold_out":
                        return {"error": f"Product '{item.get('title', product_id)}' is sold out"}, 400
                    seller_id = product.seller_id
                    # Update stock
                    product.stock_qty = max(0, (product.stock_qty or 1) - int(item.get("qty", 1)))
                    if product.stock_qty <= 0:
                        product.status = "sold_out"
                else:
                    # Product ID not found in DB (e.g. demo data) — skip stock update
                    scrap_id = None  # ensure we don't try scrap path
            elif scrap_id:
                scrap = ScrapMaterial.query.get(scrap_id)
                if scrap:
                    if scrap.status == "sold":
                        return {"error": f"Material '{item.get('title', scrap_id)}' is already sold"}, 400
                    seller_id = scrap.seller_id
                    scrap.status = "sold"
                else:
                    # Scrap ID not found in DB (e.g. demo data) — skip status update
                    pass

            # Fall back to buyer_id as seller if unresolvable (e.g. mock/demo listings)
            if not seller_id:
                seller_id = user_id

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product_id if product_id else None,
                scrap_id=scrap_id if scrap_id else None,
                seller_id=seller_id,
                title=item.get("title", "Unknown Item"),
                price=item.get("price", 0),
                quantity=item.get("qty", 1),
                unit=item.get("unit", "unit")
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return {"error": f"Database error: {str(e)}"}, 500

@orders_bp.get("/")
@jwt_required()
def list_orders():
    """List orders for the current buyer."""
    user_id = get_jwt_identity()
    try:
        orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()
        return jsonify({"orders": [o.to_dict() for o in orders]})
    except Exception as e:
        return {"error": str(e)}, 500


@orders_bp.get("/seller")
@jwt_required()
def list_seller_orders():
    """List orders for products owned by the current seller."""
    user_id = get_jwt_identity()
    
    try:
        # Join OrderItem with Order to get orders where this seller has items
        order_items = OrderItem.query.filter_by(seller_id=user_id).all()
        order_ids = list(set([oi.order_id for oi in order_items]))
        
        orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all()
        
        # For seller, we might want to only show the items they sold in that order
        result = []
        for o in orders:
            o_dict = o.to_dict()
            # Filter items to only show those belonging to this seller
            o_dict["items"] = [oi.to_dict() for oi in o.items if oi.seller_id == user_id]
            result.append(o_dict)
            
        return jsonify({"orders": result})
    except Exception as e:
        return {"error": str(e)}, 500
