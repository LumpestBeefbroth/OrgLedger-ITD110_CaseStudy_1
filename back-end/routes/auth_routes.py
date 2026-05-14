import sys
import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import users_collection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        if users_collection is None:
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Missing required fields: username, email, password"}), 400
        
        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already exists"}), 409

        hashed_password = generate_password_hash(data["password"])
        user_doc = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password
        }
        result = users_collection.insert_one(user_doc)
        return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        if users_collection is None:
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing required fields: username, password"}), 400
        
        user = users_collection.find_one({"username": data["username"]})
        
        if user and check_password_hash(user["password"], data["password"]):
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200
        
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/user/<user_id>/username", methods=["PUT"])
def update_username(user_id):
    try:
        if users_collection is None:
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'new_username' not in data:
            return jsonify({"error": "Missing required field: new_username"}), 400
        
        if users_collection.find_one({"username": data["new_username"]}):
            return jsonify({"error": "Username already exists"}), 409

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": data["new_username"]}}
        )
        return jsonify({"message": "Username updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Update failed: {str(e)}"}), 500
