import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mongo_client = None
db = None
users_collection = None
categories_collection = None
expenses_collection = None
expense_backup_collection = None

try:
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
    
    db = mongo_client["expense_tracker"]
    users_collection = db["users"]
    categories_collection = db["categories"]
    expenses_collection = db["expenses"]
    expense_backup_collection = db["expense_backup"]
    
    users_collection.create_index("username", unique=True)
    categories_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
    expenses_collection.create_index("user_id")
    expense_backup_collection.create_index("expense_id")
except Exception as e:
    print(f"[WARNING] MongoDB connection failed: {type(e).__name__}: {str(e)}")
    print("[WARNING] Collections will be None - database operations will fail gracefully")


