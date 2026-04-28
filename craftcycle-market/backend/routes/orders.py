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

def ensure_schema():
    """Helper to add ALL missing columns to the orders table."""
    try:
        from sqlalchemy import text
        cols = [
            ('delivery_fee', 'NUMERIC(10, 2) DEFAULT 0'),
            ('platform_fee', 'NUMERIC(10, 2) DEFAULT 0'),
            ('full_name', 'VARCHAR(200)'),
            ('phone', 'VARCHAR(20)'),
            ('address_line1', 'VARCHAR(300)'),
            ('address_line2', 'VARCHAR(300)'),
            ('city', 'VARCHAR(100)'),
            ('state', 'VARCHAR(100)'),
            ('pincode', 'VARCHAR(10)'),
            ('payment_method', 'VARCHAR(50)'),
            ('payment_status', 'VARCHAR(50) DEFAULT \'pending\'')
        ]
        for col, type_info in cols:
            try:
                db.session.execute(text(f'ALTER TABLE orders ADD COLUMN IF NOT EXISTS {col} {type_info}'))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error adding column {col} to orders: {e}")

        # Fix order_items table too
        item_cols = [
            ('scrap_id', 'INTEGER'),
            ('seller_id', 'INTEGER'),
            ('quantity', 'NUMERIC(10, 2) DEFAULT 1'),
            ('unit', 'VARCHAR(20) DEFAULT \'unit\'')
        ]
        for col, type_info in item_cols:
            try:
                db.session.execute(text(f'ALTER TABLE order_items ADD COLUMN IF NOT EXISTS {col} {type_info}'))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error adding column {col} to order_items: {e}")
    except Exception as e:
        print(f"Schema sync error: {e}")

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
        db.session.flush() # Get order ID

        for item in data["items"]:
            # Check if it's a product or scrap
            seller_id = None
            if "product_id" in item:
                product = Product.query.get(item["product_id"])
                if not product or product.status == "sold_out":
                    return {"error": f"Product {item['title']} is unavailable"}, 400
                seller_id = product.seller_id
                # Update stock
                product.stock_qty -= int(item.get("qty", 1))
                if product.stock_qty <= 0:
                    product.status = "sold_out"
            elif "scrap_id" in item:
                scrap = ScrapMaterial.query.get(item["scrap_id"])
                if not scrap or scrap.status == "sold":
                    return {"error": f"Material {item['title']} is unavailable"}, 400
                seller_id = scrap.seller_id
                # Update status
                scrap.status = "sold"
            
            if not seller_id:
                return {"error": "Invalid item or seller not found"}, 400

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.get("product_id"),
                scrap_id=item.get("scrap_id"),
                seller_id=seller_id,
                title=item["title"],
                price=item["price"],
                quantity=item.get("qty", 1),
                unit=item.get("unit", "unit")
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201

    except Exception as e:
        db.session.rollback()
        # Auto-repair if any columns are missing (UndefinedColumn)
        missing_indicators = ["delivery_fee", "platform_fee", "scrap_id", "seller_id", "quantity"]
        if any(ind in str(e) for ind in missing_indicators):
            ensure_schema()
            return create_order() # Retry
        
        return {"error": str(e)}, 500


@orders_bp.get("/")
@jwt_required()
def list_orders():
    """List orders for the current buyer."""
    user_id = get_jwt_identity()
    try:
        orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()
        return jsonify({"orders": [o.to_dict() for o in orders]})
    except Exception as e:
        if "delivery_fee" in str(e) or "platform_fee" in str(e):
            ensure_schema()
            return list_orders() # Retry
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
        if "delivery_fee" in str(e) or "platform_fee" in str(e):
            ensure_schema()
            return list_seller_orders() # Retry
        return {"error": str(e)}, 500
