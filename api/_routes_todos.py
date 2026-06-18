from flask import Blueprint, request, jsonify, g
import _db as db
from _auth import require_auth
from _cache import cache_get, cache_set, cache_delete

todos_bp = Blueprint("todos", __name__)

CACHE_TTL = 120  # seconds


def _user_cache_key(user_id):
    return f"todos:user:{user_id}"


@todos_bp.route("/", methods=["GET"])
@require_auth
def list_todos():
    key = _user_cache_key(g.user_id)
    cached = cache_get(key)
    if cached is not None:
        return jsonify({"todos": cached, "cached": True})

    rows = db.fetchall(
        "SELECT id, title, completed, created_at::text FROM todos "
        "WHERE user_id = %s ORDER BY created_at DESC",
        (g.user_id,),
    )
    todos = [dict(r) for r in rows]
    cache_set(key, todos, CACHE_TTL)
    return jsonify({"todos": todos, "cached": False})


@todos_bp.route("/", methods=["POST"])
@require_auth
def create_todo():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400

    row = db.execute(
        "INSERT INTO todos (user_id, title) VALUES (%s, %s) "
        "RETURNING id, title, completed, created_at::text",
        (g.user_id, title),
    )
    cache_delete(_user_cache_key(g.user_id))
    return jsonify({"todo": dict(row)}), 201


@todos_bp.route("/<int:todo_id>", methods=["PATCH"])
@require_auth
def update_todo(todo_id):
    data = request.get_json() or {}

    existing = db.fetchone(
        "SELECT id FROM todos WHERE id = %s AND user_id = %s", (todo_id, g.user_id)
    )
    if not existing:
        return jsonify({"error": "Not found"}), 404

    updates, params = [], []
    if "title" in data:
        updates.append("title = %s")
        params.append(data["title"].strip())
    if "completed" in data:
        updates.append("completed = %s")
        params.append(bool(data["completed"]))

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    params.extend([todo_id, g.user_id])
    row = db.execute(
        f"UPDATE todos SET {', '.join(updates)}, updated_at = NOW() "
        "WHERE id = %s AND user_id = %s "
        "RETURNING id, title, completed, created_at::text",
        params,
    )
    cache_delete(_user_cache_key(g.user_id))
    return jsonify({"todo": dict(row)})


@todos_bp.route("/<int:todo_id>", methods=["DELETE"])
@require_auth
def delete_todo(todo_id):
    row = db.execute(
        "DELETE FROM todos WHERE id = %s AND user_id = %s RETURNING id",
        (todo_id, g.user_id),
    )
    if not row:
        return jsonify({"error": "Not found"}), 404
    cache_delete(_user_cache_key(g.user_id))
    return jsonify({"deleted": todo_id})
