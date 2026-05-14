"""
OrgLedger Application Entry Point
Location: back-end/app.py

Main Flask application factory. Initializes the Flask app, configures CORS,
and registers all blueprints from the routes/ folder.

This is the single, clean entry point for the entire OrgLedger backend.
All endpoint logic is organized in modular blueprint files within the routes/ folder.
"""

from flask import Flask
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


if __name__ == "__main__":
    app.run(debug=True)