"""
craftcycle/backend/app/models/scrap_material.py
─────────────────────────────────────────────────
Scrap listing posted by sellers on the marketplace.
"""
from datetime import datetime
from extensions import db


VALID_CATEGORIES = (
    "wood","metal","plastic","fabric","paper",
    "glass","e-waste","organic","rubber","other"
)
VALID_QUALITIES  = ("excellent","good","fair","poor")


class ScrapMaterial(db.Model):
    __tablename__ = "scrap_materials"

    id             = db.Column(db.Integer, primary_key=True)
    seller_id      = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title          = db.Column(db.String(200), nullable=False)
    description    = db.Column(db.Text, nullable=False)
    category       = db.Column(db.String(50), nullable=False)
    quality        = db.Column(db.String(20), nullable=False, default="good")
    quantity_kg    = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    price_per_kg   = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_price    = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    location_city  = db.Column(db.String(100))
    location_state = db.Column(db.String(100))
    is_barter_ok   = db.Column(db.Boolean, default=False)
    barter_for     = db.Column(db.String(300))
    images         = db.Column(db.JSON)   # list of image URLs
    tags           = db.Column(db.JSON)   # list of tag strings
    status         = db.Column(db.String(20), nullable=False, default="active")
    view_count     = db.Column(db.Integer, default=0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    seller = db.relationship("User", backref="scrap_listings", lazy="joined")

    def to_dict(self, include_seller: bool = True) -> dict:
        d = {
            "id":             self.id,
            "title":          self.title,
            "description":    self.description,
            "category":       self.category,
            "quality":        self.quality,
            "quantity_kg":    float(self.quantity_kg),
            "price_per_kg":   float(self.price_per_kg),
            "total_price":    float(self.total_price),
            "location_city":  self.location_city,
            "location_state": self.location_state,
            "is_barter_ok":   self.is_barter_ok,
            "barter_for":     self.barter_for,
            "images":         self.images or [],
            "tags":           self.tags   or [],
            "status":         self.status,
            "view_count":     self.view_count,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
        }
        if include_seller and self.seller:
            d["seller"] = {
                "id":       self.seller.id,
                "username": self.seller.username,
                "full_name":self.seller.full_name,
                "city":     self.seller.city,
            }
        return d
