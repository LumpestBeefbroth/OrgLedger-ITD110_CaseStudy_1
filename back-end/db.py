"""
Database Configuration Module
Location: back-end/db.py

This module initializes the MongoDB connection and exports collections
to prevent circular imports and provide a single source of truth for
database connections across the application.
"""

import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
print(f"[DEBUG] MongoDB connection string: {MONGO_URI}")

try:
    mongo_client = MongoClient(
        MONGO_URI,
        maxPoolSize=50,
        minPoolSize=10,
        maxIdleTimeMS=300000,
        connectTimeoutMS=10000,
        socketTimeoutMS=30000,
        serverSelectionTimeoutMS=5000
    )
    
    mongo_client.admin.command('ping')
    print("[DEBUG] MongoDB connection successful")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {type(e).__name__}: {str(e)}")
    raise

db = mongo_client["expense_tracker"]
print(f"[DEBUG] Connected to database: expense_tracker")

users_collection = db["users"]
categories_collection = db["categories"]
expenses_collection = db["expenses"]
expense_backup_collection = db["expense_backup"]

print("[DEBUG] Creating indexes...")
users_collection.create_index("username", unique=True)
categories_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
expenses_collection.create_index("user_id")
expense_backup_collection.create_index("expense_id")
print("[DEBUG] Indexes created successfully")
