"""
craftcycle/backend/app/models/order.py
──────────────────────────────────────
Order and OrderItem models for tracking purchases.
"""
from datetime import datetime
from extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id               = db.Column(db.Integer, primary_key=True)
    buyer_id         = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_fee     = db.Column(db.Numeric(10, 2), default=0)
    platform_fee     = db.Column(db.Numeric(10, 2), default=0)
    status           = db.Column(db.Enum("pending", "processing", "shipped", "delivered", "cancelled"), default="pending")
    
    # Shipping info
    full_name        = db.Column(db.String(200))
    phone            = db.Column(db.String(20))
    address_line1    = db.Column(db.String(300))
    address_line2    = db.Column(db.String(300))
    city             = db.Column(db.String(100))
    state            = db.Column(db.String(100))
    pincode          = db.Column(db.String(10))
    
    payment_method   = db.Column(db.String(50))
    payment_status   = db.Column(db.Enum("pending", "paid", "failed"), default="pending")
    
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer = db.relationship("User", backref="orders", lazy="joined")
    items = db.relationship("OrderItem", backref="order", lazy="select", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "buyer_id":       self.buyer_id,
            "total_amount":   float(self.total_amount),
            "delivery_fee":   float(self.delivery_fee),
            "platform_fee":   float(self.platform_fee),
            "status":         self.status,
            "shipping": {
                "full_name":     self.full_name,
                "phone":         self.phone,
                "address_line1": self.address_line1,
                "address_line2": self.address_line2,
                "city":          self.city,
                "state":         self.state,
                "pincode":       self.pincode,
            },
            "payment": {
                "method": self.payment_method,
                "status": self.payment_status,
            },
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "items":          [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id          = db.Column(db.Integer, primary_key=True)
    order_id    = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    scrap_id    = db.Column(db.Integer, db.ForeignKey("scrap_materials.id", ondelete="SET NULL"), nullable=True)
    
    # Store seller_id here for easy lookup of seller orders
    seller_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title       = db.Column(db.String(200), nullable=False)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    quantity    = db.Column(db.Numeric(10, 2), nullable=False) # can be kg for scrap
    unit        = db.Column(db.String(20), default="unit") # "unit" or "kg"
    
    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "order_id":   self.order_id,
            "product_id": self.product_id,
            "scrap_id":   self.scrap_id,
            "seller_id":  self.seller_id,
            "title":      self.title,
            "price":      float(self.price),
            "quantity":   float(self.quantity),
            "unit":       self.unit
        }
