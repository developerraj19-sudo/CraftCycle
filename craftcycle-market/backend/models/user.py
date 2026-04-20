"""
craftcycle/backend/app/models/user.py
───────────────────────────────────────
User SQLAlchemy model with helper methods.
"""
from datetime import datetime
from extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50),  nullable=False, unique=True)
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name     = db.Column(db.String(150), nullable=False)
    role          = db.Column(db.Enum("buyer","seller","admin"), nullable=False, default="buyer")
    avatar_url    = db.Column(db.String(500))
    bio           = db.Column(db.Text)
    phone         = db.Column(db.String(20))
    city          = db.Column(db.String(100))
    state         = db.Column(db.String(100))
    green_coins   = db.Column(db.Integer, nullable=False, default=0)
    is_active     = db.Column(db.Boolean, nullable=False, default=True)
    is_verified   = db.Column(db.Boolean, nullable=False, default=False)
    reset_token   = db.Column(db.String(100))
    reset_expires = db.Column(db.DateTime)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Password helpers ──────────────────────────────────────
    def set_password(self, plain: str):
        self.password_hash = bcrypt.generate_password_hash(plain).decode("utf-8")

    def check_password(self, plain: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, plain)

    # ── Role checks ───────────────────────────────────────────
    @property
    def is_admin(self)  -> bool: return self.role == "admin"
    @property
    def is_seller(self) -> bool: return self.role in ("seller", "admin")

    # ── Coin helpers ──────────────────────────────────────────
    def award_coins(self, amount: int, type_: str, description: str = "", ref_id: int = None):
        """Add coins to the user and write a ledger entry."""
        from coin_transaction import CoinTransaction
        self.green_coins += amount
        tx = CoinTransaction(
            user_id=self.id,
            amount=amount,
            balance=self.green_coins,
            type=type_,
            description=description,
            ref_id=ref_id,
        )
        db.session.add(tx)

    # ── Serialisation ─────────────────────────────────────────
    def to_public_dict(self) -> dict:
        """Safe data for public-facing responses."""
        return {
            "id":           self.id,
            "username":     self.username,
            "full_name":    self.full_name,
            "role":         self.role,
            "avatar_url":   self.avatar_url,
            "city":         self.city,
            "state":        self.state,
            "green_coins":  self.green_coins,
            "is_verified":  self.is_verified,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }

    def to_private_dict(self) -> dict:
        """Extended data for the user themselves (after login)."""
        d = self.to_public_dict()
        d.update({
            "email":     self.email,
            "phone":     self.phone,
            "bio":       self.bio,
            "is_active": self.is_active,
        })
        return d

    def __repr__(self):
        return f"<User {self.username}>"
