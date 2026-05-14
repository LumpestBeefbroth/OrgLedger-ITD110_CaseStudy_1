import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.category_routes import category_bp
from routes.ledger_routes import ledger_bp
from routes.analytics_routes import analytics_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(category_bp)
app.register_blueprint(ledger_bp)
app.register_blueprint(analytics_bp)


@app.route('/health', methods=['GET'])
def health():
    try:
        from db import users_collection
        if users_collection is not None:
            return jsonify({"status": "ok", "database": "connected"}), 200
        else:
            return jsonify({"status": "warning", "database": "disconnected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)