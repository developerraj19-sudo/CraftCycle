"""
craftcycle/backend/app/models/scanner_history.py
──────────────────────────────────────────────────
Stores each AI scan result. The image_hash allows cache hits
so we don't call OpenAI again for the same image.
"""
from datetime import datetime
from .extensions import db


class ScannerHistory(db.Model):
    __tablename__ = "scanner_history"

    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_hash        = db.Column(db.String(64), nullable=False)    # SHA-256 hex
    image_url         = db.Column(db.String(500))
    material_detected = db.Column(db.String(200))
    suggestions       = db.Column(db.JSON)          # list of product idea dicts
    coins_earned      = db.Column(db.Integer, default=2)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "material_detected": self.material_detected,
            "suggestions":       self.suggestions or [],
            "suggestions_count": len(self.suggestions or []),
            "coins_earned":      self.coins_earned,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
        }
