"""
Database Configuration Module
Location: back-end/db.py

This module initializes the MongoDB connection and exports collections
to prevent circular imports and provide a single source of truth for
database connections across the application.

Connection Details:
- Local: mongodb://localhost:27017
- Vercel: Uses MONGO_URI environment variable (MongoDB Atlas mongodb+srv://)
- Requires dnspython for mongodb+srv:// URIs
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
print(f"[DEBUG] MongoDB URI: {MONGO_URI[:50]}{'...' if len(MONGO_URI) > 50 else ''}")

try:
    print("[DEBUG] Attempting MongoDB connection...")
    mongo_client = MongoClient(
        MONGO_URI,
        maxPoolSize=50,
        minPoolSize=10,
        maxIdleTimeMS=300000,
        connectTimeoutMS=10000,
        socketTimeoutMS=30000,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        w='majority'
    )
    
    mongo_client.admin.command('ping')
    print("[DEBUG] ✓ MongoDB connection successful")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"[ERROR] MongoDB connection failed: {type(e).__name__}")
    print(f"[ERROR] Details: {str(e)}")
    mongo_client = None
except Exception as e:
    print(f"[ERROR] Unexpected error during MongoDB connection: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    mongo_client = None

try:
    if mongo_client:
        db = mongo_client["expense_tracker"]
        print("[DEBUG] ✓ Connected to database: expense_tracker")
        
        users_collection = db["users"]
        categories_collection = db["categories"]
        expenses_collection = db["expenses"]
        expense_backup_collection = db["expense_backup"]
        
        print("[DEBUG] Creating indexes...")
        users_collection.create_index("username", unique=True)
        categories_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
        expenses_collection.create_index("user_id")
        expense_backup_collection.create_index("expense_id")
        print("[DEBUG] ✓ Indexes created successfully")
    else:
        print("[WARN] MongoDB not connected - collections will be None")
        db = None
        users_collection = None
        categories_collection = None
        expenses_collection = None
        expense_backup_collection = None
except Exception as e:
    print(f"[ERROR] Failed to initialize collections: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    db = None
    users_collection = None
    categories_collection = None
    expenses_collection = None
    expense_backup_collection = None

