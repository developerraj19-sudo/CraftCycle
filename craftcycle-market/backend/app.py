"""
craftcycle/backend/app.py
────────────────────────────────────
Application entry point for Render.com deployment.
"""
import os
from flask import Flask
from config import get_config
from extensions import db, jwt, bcrypt, cors, mail, limiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    # ── Init extensions ───────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Enable CORS — allow Render (same-origin) + Cloudflare Pages + localhost
    allowed_origins = app.config.get("CORS_ORIGINS", "*")
    if allowed_origins == "*" or allowed_origins == ["*"]:
        allowed_origins = [
            "https://craftcycle.pages.dev",
            "https://craftcycle.onrender.com",
            "http://localhost:5000",
            "http://localhost:5500",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:5500",
        ]
    cors.init_app(app, resources={r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
    }})
    mail.init_app(app)
    limiter.init_app(app)

    # ── Register blueprints ───────────────────────────────────
    from routes.auth        import auth_bp
    from routes.marketplace import marketplace_bp
    from routes.products    import products_bp
    from routes.scanner     import scanner_bp
    from routes.admin       import admin_bp
    from routes.chatbot     import chatbot_bp
    from routes.orders      import orders_bp

    app.register_blueprint(auth_bp,        url_prefix="/api/v1/auth")
    app.register_blueprint(marketplace_bp, url_prefix="/api/v1/marketplace")
    app.register_blueprint(products_bp,    url_prefix="/api/v1/products")
    app.register_blueprint(scanner_bp,     url_prefix="/api/v1/scanner")
    app.register_blueprint(admin_bp,       url_prefix="/api/v1/admin")
    app.register_blueprint(chatbot_bp,     url_prefix="/api/v1/chatbot")
    app.register_blueprint(orders_bp,      url_prefix="/api/v1/orders")

    # ── Register error handlers ───────────────────────────────
    from utils.errors import register_error_handlers
    register_error_handlers(app)

    # ── JWT error callbacks (always return JSON) ───────────────
    from flask import jsonify as _jsonify

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return _jsonify(error="Token expired", message="Your session has expired. Please log in again."), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return _jsonify(error="Invalid token", message=f"Authentication failed: {reason}"), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return _jsonify(error="Unauthorized", message="Authentication token is required."), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return _jsonify(error="Token revoked", message="Your session was revoked. Please log in again."), 401

    # ── Config endpoints ──────────────────────────────────────
    @app.get("/api/v1/config/maps-key")
    @limiter.exempt
    def maps_key():
        return {"key": os.getenv("GOOGLE_MAPS_API_KEY", "")}

    # ── Health check ──────────────────────────────────────────
    @app.get("/api/v1/health")
    def health():
        db_status = "ok"
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "ok", 
            "service": "CraftCycle API",
            "database": db_status
        }

    # ── Serve Frontend ──────────────────────────────────────────
    # This serves the static frontend files from the sibling directory
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    @limiter.exempt
    def serve_frontend(path):
        # Skip API routes
        if path.startswith("api/"):
            from flask import abort
            abort(404)
            
        from flask import send_from_directory
        from werkzeug.exceptions import NotFound

        # Try to serve requested file
        if path != "":
            try:
                return send_from_directory(frontend_dir, path)
            except NotFound:
                pass
        
        # Default to index.html for SPA or root
        return send_from_directory(frontend_dir, "index.html")

    # ── Auto-Sync Database Schema ──────────────────────────────
    # Run this once during app initialization to fix missing columns
    # in case Render's Start Command is ignoring the Procfile.
    with app.app_context():
        try:
            import sync_db
            # Ensure it doesn't sys.exit(1) on failure, just logs
            try:
                db.create_all()
            except Exception as e:
                print(f"[AutoSync] create_all error: {e}")
                
            from sqlalchemy import text
            enum_conversions = [
                ("orders",      "status",         "VARCHAR(20)",  "'pending'"),
                ("orders",      "payment_status", "VARCHAR(20)",  "'pending'"),
                ("scrap_materials", "status",     "VARCHAR(20)",  "'active'"),
                ("products",    "status",         "VARCHAR(20)",  "'pending'"),
                ("products",    "difficulty",     "VARCHAR(20)",  "'medium'"),
                ("users",       "role",           "VARCHAR(20)",  "'buyer'"),
                ("coin_transactions", "type",     "VARCHAR(20)",  "'welcome'"),
            ]
            for table, col, new_type, default_val in enum_conversions:
                try:
                    db.session.execute(text(f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type} USING {col}::TEXT"))
                    db.session.execute(text(f"ALTER TABLE {table} ALTER COLUMN {col} SET DEFAULT {default_val}"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            orders_cols = [
                ("delivery_fee",   "NUMERIC(10,2) DEFAULT 0"),
                ("platform_fee",   "NUMERIC(10,2) DEFAULT 0"),
                ("full_name",      "VARCHAR(200)"),
                ("phone",          "VARCHAR(20)"),
                ("address_line1",  "VARCHAR(300)"),
                ("address_line2",  "VARCHAR(300)"),
                ("city",           "VARCHAR(100)"),
                ("state",          "VARCHAR(100)"),
                ("pincode",        "VARCHAR(10)"),
                ("payment_method", "VARCHAR(50)"),
                ("payment_status", "VARCHAR(20) DEFAULT 'pending'"),
                ("status",         "VARCHAR(20) DEFAULT 'pending'"),
            ]
            for col, type_info in orders_cols:
                try:
                    db.session.execute(text(f"ALTER TABLE orders ADD COLUMN IF NOT EXISTS {col} {type_info}"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            items_cols = [
                ("product_id", "INTEGER"),
                ("scrap_id",   "INTEGER"),
                ("seller_id",  "INTEGER"),
                ("title",      "VARCHAR(200) DEFAULT 'Unknown Item'"),
                ("price",      "NUMERIC(10,2) DEFAULT 0"),
                ("quantity",   "NUMERIC(10,2) DEFAULT 1"),
                ("unit",       "VARCHAR(20) DEFAULT 'unit'"),
            ]
            for col, type_info in items_cols:
                try:
                    db.session.execute(text(f"ALTER TABLE order_items ADD COLUMN IF NOT EXISTS {col} {type_info}"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # Fix existing NOT NULL constraints on product_id, scrap_id, and legacy unit_price/total_price which block order placement
            try:
                db.session.execute(text("ALTER TABLE order_items ALTER COLUMN product_id DROP NOT NULL"))
                db.session.execute(text("ALTER TABLE order_items ALTER COLUMN scrap_id DROP NOT NULL"))
                db.session.execute(text("ALTER TABLE order_items ALTER COLUMN unit_price DROP NOT NULL"))
                db.session.execute(text("ALTER TABLE order_items ALTER COLUMN total_price DROP NOT NULL"))
                db.session.commit()
            except Exception:
                db.session.rollback()

            print("[AutoSync] Database schema verification complete.")
        except Exception as e:
            print(f"[AutoSync] Database sync error: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"""
  =======================================
      CraftCycle Market - API Server
      http://localhost:{port}/api/v1/health
  =======================================
    """)
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
