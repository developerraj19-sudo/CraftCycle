"""
craftcycle/backend/app/models/coin_transaction.py
───────────────────────────────────────────────────
Ledger record every time a user earns or spends Green Coins.
"""
from datetime import datetime
from extensions import db


class CoinTransaction(db.Model):
    __tablename__ = "coin_transactions"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount      = db.Column(db.Integer, nullable=False)     # positive=earn, negative=spend
    balance     = db.Column(db.Integer, nullable=False)     # balance AFTER this tx
    type        = db.Column(
        db.Enum("welcome","scan","sale","purchase","challenge","review","referral","admin","refund"),
        nullable=False
    )
    description = db.Column(db.String(300))
    ref_id      = db.Column(db.Integer)                     # optional FK to order/product
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "amount":      self.amount,
            "balance":     self.balance,
            "type":        self.type,
            "description": self.description,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }
