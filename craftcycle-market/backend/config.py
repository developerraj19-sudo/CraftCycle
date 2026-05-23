"""
craftcycle/backend/config.py
─────────────────────────────────
All configuration classes.
Updated for Supabase/PostgreSQL.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # loads .env file


class Config:
    """Base configuration shared by all environments."""

    # ── Flask core ────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JSON_SORT_KEYS = False

    # ── Database (PostgreSQL / Supabase) ────────────────────────
    # SQLAlchemy requires postgresql:// not postgres://
    _db_url = os.getenv("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    
    # Only add sslmode for PostgreSQL
    if _db_url.startswith("postgresql"):
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            "sslmode": "require" if os.getenv("FLASK_ENV") == "production" else "prefer"
        }

    # ── Supabase ──────────────────────────────────────────────
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_EXPIRES_MINUTES", 120))  # 2 hours
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", 7))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "*"
    ).split(",")

    # ── Email ─────────────────────────────────────────────────
    MAIL_SERVER   = os.getenv("MAIL_SERVER", "smtp-relay.brevo.com")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@craftcycle.in")

    # ── External APIs ─────────────────────────────────────────
    GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "AIzaSyAeRg3N5IWmTKeA8cBPeCwPHyTB2sLW7Z0")
    RAZORPAY_KEY_ID     = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

    # ── File uploads ──────────────────────────────────────────
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    # ── Platform settings ─────────────────────────────────────
    COMMISSION_RATE    = float(os.getenv("COMMISSION_RATE", 10))
    WELCOME_COINS      = int(os.getenv("WELCOME_COINS", 100))
    SCAN_COINS         = int(os.getenv("SCAN_COINS", 2))
    SCANNER_RATE_LIMIT = int(os.getenv("SCANNER_RATE_LIMIT", 5))

    FRONTEND_URL       = os.getenv("FRONTEND_URL", "http://localhost:5500")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


# Maps FLASK_ENV string → class
config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}


def get_config() -> Config:
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
