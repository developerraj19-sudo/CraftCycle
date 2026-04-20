"""
craftcycle/backend/app/extensions.py
──────────────────────────────────────
All Flask extensions are initialised here (without the app).
The app factory calls init_app() on each one.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

db      = SQLAlchemy()
jwt     = JWTManager()
bcrypt  = Bcrypt()
cors    = CORS()
mail    = Mail()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://",   # swap for redis:// in production
)
