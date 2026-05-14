"""
Category Routes Blueprint
Location: back-end/routes/category_routes.py

Handles all category CRUD operations (GET, POST, PUT, DELETE).
"""

import sys
import os
from flask import Blueprint, request, jsonify
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import categories_collection, expenses_collection

category_bp = Blueprint('categories', __name__)


@category_bp.route("/categories/<user_id>", methods=["GET"])
def get_categories(user_id):
    try:
        categories = list(categories_collection.find(
            {"user_id": user_id},
            {"_id": 1, "name": 1, "user_id": 1}
        ))
        for cat in categories:
            cat["_id"] = str(cat["_id"])
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/categories", methods=["POST"])
def add_category():
    try:
        data = request.get_json()
        if categories_collection.find_one({"name": data["name"], "user_id": data["user_id"]}):
            return jsonify({"error": "Category already exists"}), 409

        category_doc = {
            "user_id": data["user_id"],
            "name": data["name"]
        }
        result = categories_collection.insert_one(category_doc)
        return jsonify({
            "message": "Category added successfully",
            "_id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/categories/<category_id>", methods=["PUT"])
def update_category(category_id):
    try:
        data = request.get_json()
        categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": {"name": data["name"]}}
        )
        return jsonify({"message": "Category updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/categories/<category_id>", methods=["DELETE"])
def delete_category(category_id):
    try:
        expenses_collection.delete_many({"category_id": category_id})
        categories_collection.delete_one({"_id": ObjectId(category_id)})
        
        return jsonify({"message": "Category and its expenses deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
