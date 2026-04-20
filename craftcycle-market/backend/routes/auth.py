"""
craftcycle/backend/app/routes/auth.py
───────────────────────────────────────
Endpoints:
  POST   /api/v1/auth/register     — Create account
  POST   /api/v1/auth/login        — Login → JWT tokens
  POST   /api/v1/auth/refresh      — Refresh access token
  GET    /api/v1/auth/me           — Get current user profile
  POST   /api/v1/auth/logout       — (client-side token clear)
  POST   /api/v1/auth/forgot       — Request password reset email
  POST   /api/v1/auth/reset        — Reset password with token
"""
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)

from extensions import db
from models.user import User
from models.coin_transaction import CoinTransaction
from utils.validators import validate_email, validate_password, validate_username, sanitize_string

auth_bp = Blueprint("auth", __name__)


# ── POST /register ────────────────────────────────────────────
@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    # Required fields
    email     = sanitize_string(data.get("email",     "")).lower()
    username  = sanitize_string(data.get("username",  ""))
    password  = data.get("password", "")
    full_name = sanitize_string(data.get("full_name", ""))
    role      = data.get("role", "buyer")

    # Validation
    errors = {}
    if not validate_email(email):
        errors["email"] = "Enter a valid email address."
    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        errors["password"] = pw_msg
    valid_un, un_msg = validate_username(username)
    if not valid_un:
        errors["username"] = un_msg
    if not full_name:
        errors["full_name"] = "Full name is required."
    if role not in ("buyer", "seller"):
        errors["role"] = "Role must be 'buyer' or 'seller'."
    if errors:
        return jsonify(error="Validation failed", details=errors), 422

    # Uniqueness checks
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered."), 409
    if User.query.filter_by(username=username).first():
        return jsonify(error="Username already taken."), 409

    # Create user
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        role=role,
    )
    user.set_password(password)

    # Award welcome coins
    welcome = current_app.config.get("WELCOME_COINS", 100)
    user.green_coins = welcome

    db.session.add(user)
    db.session.flush()  # gives user.id

    # Coin ledger
    tx = CoinTransaction(
        user_id=user.id,
        amount=welcome,
        balance=welcome,
        type="welcome",
        description="Welcome bonus for joining CraftCycle!",
    )
    db.session.add(tx)
    db.session.commit()

    # Issue tokens
    access  = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return jsonify(
        message=f"Account created! You received {welcome} Green Coins 🎉",
        user=user.to_private_dict(),
        access_token=access,
        refresh_token=refresh,
    ), 201


# ── POST /login ───────────────────────────────────────────────
@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    identifier = sanitize_string(data.get("email", "")).lower()  # email or username
    password   = data.get("password", "")

    if not identifier or not password:
        return jsonify(error="Email/username and password are required."), 400

    # Find user by email or username
    user = (
        User.query.filter_by(email=identifier).first()
        or User.query.filter_by(username=identifier).first()
    )

    if not user or not user.check_password(password):
        return jsonify(error="Invalid credentials."), 401

    if not user.is_active:
        return jsonify(error="Your account has been suspended. Contact support."), 403

    # Issue tokens
    access  = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return jsonify(
        message="Login successful.",
        user=user.to_private_dict(),
        access_token=access,
        refresh_token=refresh,
    ), 200


# ── POST /refresh ─────────────────────────────────────────────
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify(error="User not found or suspended."), 401

    access = create_access_token(identity=user_id)
    return jsonify(access_token=access), 200


# ── GET /me ───────────────────────────────────────────────────
@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error="User not found."), 404
    return jsonify(user=user.to_private_dict()), 200


# ── POST /logout ──────────────────────────────────────────────
@auth_bp.post("/logout")
def logout():
    # JWT is stateless — client simply deletes the token.
    return jsonify(message="Logged out successfully."), 200


# ── POST /forgot ──────────────────────────────────────────────
@auth_bp.post("/forgot")
def forgot_password():
    data  = request.get_json(silent=True) or {}
    email = sanitize_string(data.get("email", "")).lower()

    if not validate_email(email):
        return jsonify(error="Enter a valid email address."), 422

    # Always return 200 to prevent email enumeration
    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token   = token
        user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        # TODO: send email with link:  /reset-password?token=<token>
        # current_app.logger.info(f"Password reset token for {email}: {token}")

    return jsonify(message="If that email exists, a reset link has been sent."), 200


# ── POST /reset ───────────────────────────────────────────────
@auth_bp.post("/reset")
def reset_password():
    data     = request.get_json(silent=True) or {}
    token    = data.get("token", "")
    password = data.get("password", "")

    if not token or not password:
        return jsonify(error="Token and new password are required."), 400

    valid, msg = validate_password(password)
    if not valid:
        return jsonify(error=msg), 422

    user = User.query.filter_by(reset_token=token).first()
    if not user or (user.reset_expires and user.reset_expires < datetime.utcnow()):
        return jsonify(error="Invalid or expired reset token."), 400

    user.set_password(password)
    user.reset_token   = None
    user.reset_expires = None
    db.session.commit()

    return jsonify(message="Password reset successful. You can now log in."), 200
