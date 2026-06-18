import jwt
from flask import Blueprint, request, jsonify, make_response, g
import _db as db
from _auth import (
    hash_password, check_password,
    make_access_token, make_refresh_token,
    decode_token, require_auth,
)
from _config import JWT_REFRESH_TTL

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing = db.fetchone("SELECT id FROM users WHERE email = $1", (email,))
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    user = db.execute(
        "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email",
        (email, hash_password(password)),
    )

    access_token = make_access_token(user["id"], user["email"])
    refresh_token = make_refresh_token(user["id"])

    resp = make_response(
        jsonify({"user": {"id": user["id"], "email": user["email"]}, "access_token": access_token}),
        201,
    )
    resp.set_cookie(
        "refresh_token", refresh_token,
        httponly=True, secure=True, samesite="Strict", max_age=JWT_REFRESH_TTL,
    )
    return resp


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.fetchone(
        "SELECT id, email, password_hash FROM users WHERE email = $1", (email,)
    )
    if not user or not check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = make_access_token(user["id"], user["email"])
    refresh_token = make_refresh_token(user["id"])

    resp = make_response(
        jsonify({"user": {"id": user["id"], "email": user["email"]}, "access_token": access_token})
    )
    resp.set_cookie(
        "refresh_token", refresh_token,
        httponly=True, secure=True, samesite="Strict", max_age=JWT_REFRESH_TTL,
    )
    return resp


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "No refresh token"}), 401
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return jsonify({"error": "Invalid token type"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    user = db.fetchone("SELECT id, email FROM users WHERE id = $1", (payload["sub"],))
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_token = make_access_token(user["id"], user["email"])
    return jsonify({"access_token": access_token})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "Logged out"}))
    resp.delete_cookie("refresh_token")
    return resp


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user = db.fetchone(
        "SELECT id, email, created_at FROM users WHERE id = $1", (g.user_id,)
    )
    return jsonify({"user": dict(user)})
