"""
Authentication Routes Blueprint
Location: back-end/routes/auth_routes.py

Handles user registration, login, and username update endpoints.
"""

import sys
import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import users_collection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        print("[DEBUG] Register endpoint called")
        
        if users_collection is None:
            print("[ERROR] Database not connected")
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            print("[ERROR] Missing required fields in request")
            return jsonify({"error": "Missing required fields: username, email, password"}), 400
        
        print(f"[DEBUG] Checking if username '{data['username']}' already exists")
        if users_collection.find_one({"username": data['username']}):
            print(f"[DEBUG] Username '{data['username']}' already exists")
            return jsonify({"error": "Username already exists"}), 409

        print(f"[DEBUG] Hashing password for user '{data['username']}'")
        hashed_password = generate_password_hash(data["password"])
        user_doc = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password
        }
        print(f"[DEBUG] Inserting user document for '{data['username']}'")
        result = users_collection.insert_one(user_doc)
        print(f"[DEBUG] User registered successfully with ID: {result.inserted_id}")
        return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"[ERROR] Registration failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        print("[DEBUG] Login endpoint called")
        
        if users_collection is None:
            print("[ERROR] Database not connected")
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            print("[ERROR] Missing username or password in request")
            return jsonify({"error": "Missing required fields: username, password"}), 400
        
        print(f"[DEBUG] Looking up user '{data['username']}'")
        user = users_collection.find_one({"username": data["username"]})
        
        if user and check_password_hash(user["password"], data["password"]):
            print(f"[DEBUG] Login successful for user '{data['username']}'")
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200
        
        print(f"[DEBUG] Invalid credentials for user '{data['username']}'")
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print(f"[ERROR] Login failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/user/<user_id>/username", methods=["PUT"])
def update_username(user_id):
    try:
        print(f"[DEBUG] Update username endpoint called for user_id: {user_id}")
        
        if users_collection is None:
            print("[ERROR] Database not connected")
            return jsonify({"error": "Database connection unavailable"}), 503
        
        data = request.get_json()
        
        if not data or 'new_username' not in data:
            print("[ERROR] Missing new_username in request")
            return jsonify({"error": "Missing required field: new_username"}), 400
        
        if users_collection.find_one({"username": data["new_username"]}):
            print(f"[DEBUG] Username '{data['new_username']}' already exists")
            return jsonify({"error": "Username already exists"}), 409

        print(f"[DEBUG] Updating username for user {user_id} to '{data['new_username']}'")
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": data["new_username"]}}
        )
        print(f"[DEBUG] Username updated successfully")
        return jsonify({"message": "Username updated successfully"}), 200
    except Exception as e:
        print(f"[ERROR] Update username failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Update failed: {str(e)}"}), 500
