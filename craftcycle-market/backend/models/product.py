"""
craftcycle/backend/app/models/product.py
──────────────────────────────────────────
Finished upcycled product listed for sale by a seller.
"""
from datetime import datetime
from .extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id            = db.Column(db.Integer, primary_key=True)
    seller_id     = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, nullable=False)
    category      = db.Column(db.String(100), nullable=False)
    price         = db.Column(db.Numeric(10, 2), nullable=False)
    stock_qty     = db.Column(db.Integer, nullable=False, default=1)
    images        = db.Column(db.JSON)            # list of image URLs
    materials_used= db.Column(db.String(300))
    waste_kg_saved= db.Column(db.Numeric(8, 2), default=0)
    co2_kg_saved  = db.Column(db.Numeric(8, 2), default=0)
    time_to_make_h= db.Column(db.Numeric(5, 1))
    difficulty    = db.Column(db.Enum("easy","medium","hard"), default="medium")
    status        = db.Column(db.Enum("pending","active","sold_out","suspended"), nullable=False, default="pending")
    view_count    = db.Column(db.Integer, default=0)
    wish_count    = db.Column(db.Integer, default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = db.relationship("User", backref="products", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "title":          self.title,
            "description":    self.description,
            "category":       self.category,
            "price":          float(self.price),
            "stock_qty":      self.stock_qty,
            "images":         self.images or [],
            "materials_used": self.materials_used,
            "waste_kg_saved": float(self.waste_kg_saved or 0),
            "co2_kg_saved":   float(self.co2_kg_saved   or 0),
            "time_to_make_h": float(self.time_to_make_h or 0),
            "difficulty":     self.difficulty,
            "status":         self.status,
            "view_count":     self.view_count,
            "wish_count":     self.wish_count,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "seller": {
                "id":       self.seller.id,
                "username": self.seller.username,
                "full_name":self.seller.full_name,
            } if self.seller else None,
        }
