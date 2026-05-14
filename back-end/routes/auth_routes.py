"""
Authentication Routes Blueprint
Location: back-end/routes/auth_routes.py

Handles user registration, login, and username update endpoints.
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from db import users_collection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already exists"}), 409

        hashed_password = generate_password_hash(data["password"])
        user_doc = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password
        }
        result = users_collection.insert_one(user_doc)
        return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user = users_collection.find_one({"username": data["username"]})
        
        if user and check_password_hash(user["password"], data["password"]):
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])})
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/user/<user_id>/username", methods=["PUT"])
def update_username(user_id):
    try:
        data = request.get_json()
        if users_collection.find_one({"username": data["new_username"]}):
            return jsonify({"error": "Username already exists"}), 409

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": data["new_username"]}}
        )
        return jsonify({"message": "Username updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
