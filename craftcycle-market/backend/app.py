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
    
    # Enable CORS for all /api/* routes
    # In production, CORS_ORIGINS should be set to your Netlify URL
    cors.init_app(app, resources={r"/api/*": {
        "origins": app.config.get("CORS_ORIGINS", "*"),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
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

    app.register_blueprint(auth_bp,        url_prefix="/api/v1/auth")
    app.register_blueprint(marketplace_bp, url_prefix="/api/v1/marketplace")
    app.register_blueprint(products_bp,    url_prefix="/api/v1/products")
    app.register_blueprint(scanner_bp,     url_prefix="/api/v1/scanner")
    app.register_blueprint(admin_bp,       url_prefix="/api/v1/admin")
    app.register_blueprint(chatbot_bp,     url_prefix="/api/v1/chatbot")

    # ── Register error handlers ───────────────────────────────
    from utils.errors import register_error_handlers
    register_error_handlers(app)

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
