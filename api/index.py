import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from _config import CORS_ORIGINS
from _routes_auth import auth_bp
from _routes_todos import todos_bp

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(todos_bp, url_prefix="/api/todos")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
