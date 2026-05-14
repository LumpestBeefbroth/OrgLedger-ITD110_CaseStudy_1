"""
OrgLedger Application Entry Point
Location: back-end/app.py

Main Flask application factory. Initializes the Flask app, configures CORS,
and registers all blueprints from the routes/ folder.

This is the single, clean entry point for the entire OrgLedger backend.
All endpoint logic is organized in modular blueprint files within the routes/ folder.

Vercel Configuration:
- Vercel handles app execution; app.run() only used locally (debug=True)
- Health check route verifies backend is operational
- MongoDB connection wrapped in try-except to prevent crashes
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app)

print("[DEBUG] Flask app initialized")
print(f"[DEBUG] Environment: {'Vercel' if os.getenv('VERCEL') else 'Local'}")

try:
    print("[DEBUG] Importing route blueprints...")
    from routes.auth_routes import auth_bp
    from routes.category_routes import category_bp
    from routes.ledger_routes import ledger_bp
    from routes.analytics_routes import analytics_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(analytics_bp)
    print("[DEBUG] All blueprints registered successfully")
except Exception as e:
    print(f"[ERROR] Failed to register blueprints: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint to verify backend is operational"""
    try:
        from db import mongo_client
        mongo_client.admin.command('ping')
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        print(f"[ERROR] Health check failed: {type(e).__name__}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)