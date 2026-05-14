"""
Database Configuration Module
Location: back-end/db.py

This module initializes the MongoDB connection and exports collections
to prevent circular imports and provide a single source of truth for
database connections across the application.
"""

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

mongo_client = MongoClient(
    MONGO_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=300000,
    connectTimeoutMS=10000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=5000
)

db = mongo_client["expense_tracker"]

users_collection = db["users"]
categories_collection = db["categories"]
expenses_collection = db["expenses"]
expense_backup_collection = db["expense_backup"]

users_collection.create_index("username", unique=True)
categories_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
expenses_collection.create_index("user_id")
expense_backup_collection.create_index("expense_id")
