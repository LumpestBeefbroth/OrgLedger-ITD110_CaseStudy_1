from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import os
import subprocess
from datetime import datetime
from bson import ObjectId, json_util

app = Flask(__name__)
CORS(app)

from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

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

@app.route("/register", methods=["POST"])
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

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user = users_collection.find_one({"username": data["username"]})
        
        if user and check_password_hash(user["password"], data["password"]):
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])})
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-username", methods=["PUT"])
def update_username():
    try:
        data = request.get_json()
        if users_collection.find_one({"username": data["new_username"]}):
            return jsonify({"error": "Username already exists"}), 409

        users_collection.update_one(
            {"_id": ObjectId(data["user_id"])},
            {"$set": {"username": data["new_username"]}}
        )
        return jsonify({"message": "Username updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/categories/<user_id>", methods=["GET"])
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

@app.route("/categories", methods=["POST"])
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

@app.route("/categories/<category_id>", methods=["PUT"])
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

@app.route("/categories/<category_id>", methods=["DELETE"])
def delete_category(category_id):
    try:
        expenses_collection.delete_many({"category_id": category_id})
        categories_collection.delete_one({"_id": ObjectId(category_id)})
        
        return jsonify({"message": "Category and its expenses deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/expenses/<user_id>", methods=["GET"])
def get_expenses(user_id):
    try:
        # Simple approach: fetch expenses and categories separately
        expenses = list(expenses_collection.find(
            {"user_id": user_id},
            {"_id": 1, "user_id": 1, "category_id": 1, "transaction_type": 1, "amount": 1, "description": 1, "date": 1, "or_number": 1}
        ))
        
        # Fetch all categories for this user
        categories_list = list(categories_collection.find(
            {"user_id": user_id},
            {"_id": 1, "name": 1}
        ))
        
        # Create a map of category_id to category_name
        category_map = {str(cat["_id"]): cat["name"] for cat in categories_list}
        
        # Add category_name to each expense
        for expense in expenses:
            expense["_id"] = str(expense["_id"])
            category_id_str = str(expense.get("category_id", ""))
            expense["category_name"] = category_map.get(category_id_str, "Uncategorized")
        
        return jsonify(expenses)
    except Exception as e:
        print(f"Error in get_expenses: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/expenses", methods=["POST"])
def add_expense():
    try:
        data = request.get_json()
        
        # Validate category_id exists
        category_id = data.get("category_id", "").strip()
        if not category_id or category_id == "undefined":
            return jsonify({"error": "Invalid or missing category_id"}), 400
        
        expense_doc = {
            "user_id": data["user_id"],
            "category_id": category_id,
            "amount": data["amount"],
            "description": data["description"],
            "date": data["date"],
            "transaction_type": data.get("transaction_type", "Expense"),
            "or_number": data.get("or_number", "")
        }
        result = expenses_collection.insert_one(expense_doc)
        return jsonify({"message": "Expense added successfully", "_id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"Error adding expense: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/expenses/<expense_id>", methods=["PUT"])
@cross_origin()
def update_expense(expense_id):
    try:
        data = request.get_json()
        date_value = data["date"] if data["date"] else None

        expenses_collection.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {
                "amount": data["amount"],
                "description": data["description"],
                "date": date_value
            }}
        )
        return jsonify({"message": "Expense updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/expenses/<expense_id>/restore", methods=["PUT"])
@cross_origin()
def restore_expense(expense_id):
    try:
        backup_expense = expense_backup_collection.find_one(
            {"expense_id": expense_id},
            sort=[("modified_at", -1)]
        )
        if not backup_expense:
            return jsonify({"error": "No backup found"}), 404
        expenses_collection.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {
                "amount": backup_expense["amount"],
                "description": backup_expense["description"],
                "date": backup_expense["date"],
                "category_id": backup_expense["category_id"]
            }}
        )
        return jsonify({"message": "Expense reverted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/expenses/<expense_id>/backup", methods=["POST"])
def backup_expense(expense_id):
    try:
        exp = expenses_collection.find_one({"_id": ObjectId(expense_id)})
        if not exp:
            return jsonify({"error": "Expense not found"}), 404
        
        backup_doc = {
            "expense_id": expense_id,
            "user_id": exp["user_id"],
            "category_id": exp["category_id"],
            "amount": exp["amount"],
            "description": exp["description"],
            "date": exp["date"],
            "modified_at": datetime.utcnow()
        }
        expense_backup_collection.insert_one(backup_doc)
        return jsonify({"message": "Backup created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/expenses/<expense_id>", methods=["DELETE"])
@cross_origin()
def delete_expense(expense_id):
    try:
        expenses_collection.delete_one({"_id": ObjectId(expense_id)})
        remaining_expense = expenses_collection.find_one({"_id": ObjectId(expense_id)})
        if remaining_expense:
            return jsonify({"error": "Expense deletion failed"}), 500
        
        return jsonify({"message": "Expense deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/export-ledger/<user_id>", methods=["GET"])
def export_ledger_json(user_id):
    try:
        transactions = list(expenses_collection.find({"user_id": user_id}))
        json_data = json_util.dumps(transactions, indent=4)
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=org_ledger_backup.json"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate-backup-bat", methods=["POST"])
def generate_backup_bat():
    try:
        data = request.get_json()
        username = data.get("username")
        if not username:
            return jsonify({"error": "Username required"}), 400

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        bat_filename = f"backup_expenses_{username}.bat"
        bat_path = os.path.join(desktop_path, bat_filename)
        MONGO_URI = "mongodb://localhost:27017"
        MONGO_DB = "expense_tracker"
        BACKUP_FOLDER = os.path.join(desktop_path, "mongo_backups")

        bat_content = f"""@echo off
set USERNAME={username}
set DATE=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set BACKUP_FOLDER={BACKUP_FOLDER}
set MONGO_URI={MONGO_URI}
set MONGO_DB={MONGO_DB}

if not exist "%BACKUP_FOLDER%" mkdir "%BACKUP_FOLDER%"

mongodump --uri "%MONGO_URI%/%MONGO_DB%" --out "%BACKUP_FOLDER%\\backup_%DATE%"
echo Backup complete: %BACKUP_FOLDER%\\backup_%DATE%

echo.
echo To restore this backup, press any key...
pause

mongorestore --uri "%MONGO_URI%/%MONGO_DB%" "%BACKUP_FOLDER%\\backup_%DATE%\\%MONGO_DB%"
echo Restore complete!
pause
"""

        try:
            with open(bat_path, "w") as f:
                f.write(bat_content)
            return jsonify({"message": f"Backup & restore script created on Desktop as {bat_filename}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/backup-expenses", methods=["POST"])
def backup_expenses():
    try:
        data = request.get_json()
        username = data.get("username")
        if not username:
            return jsonify({"error": "Username required"}), 400
        user = users_collection.find_one({"username": username})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user["_id"])
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        MONGO_URI = "mongodb://localhost:27017"
        MONGO_DB = "expense_tracker"
        BACKUP_FOLDER = os.path.join(desktop_path, "mongo_backups")

        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        backup_filename = f"expense_backup_{username}_{user_id}.tar.gz"
        backup_path = os.path.join(BACKUP_FOLDER, backup_filename)
        dump_cmd = [
            "mongodump",
            f"--uri={MONGO_URI}/{MONGO_DB}",
            f"--query={{'user_id': '{user_id}'}}",
            f"--out={backup_path}"
        ]

        try:
            result = subprocess.run(dump_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({"error": result.stderr}), 500
            return jsonify({"message": f"Backup created in {BACKUP_FOLDER} as {backup_filename}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== ANALYTICS ENDPOINTS (With Aggregation Queries) ==========

@app.route("/analytics/<user_id>", methods=["GET"])
def get_analytics(user_id):
    try:
        # 1. Total expenses by category
        category_totals = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "categories",
                    "let": {"category_id": "$category_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": [
                                        "$_id",
                                        {
                                            "$cond": [
                                                {"$eq": [{"$type": "$$category_id"}, "string"]},
                                                {"$toObjectId": "$$category_id"},
                                                "$_id"
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "category_info"
                }
            },
            {
                "$group": {
                    "_id": {"category_id": "$category_id", "category_name": {"$arrayElemAt": ["$category_info.name", 0]}},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"total": -1}}
        ]))

        # 2. Overall Organizational Statistics (Income, Expense, Net)
        stats_agg = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$transaction_type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Process the stats result
        total_income = 0
        total_expense = 0
        transaction_count = 0
        
        for stat in stats_agg:
            transaction_count += stat["count"]
            if stat["_id"] == "Income":
                total_income = stat["total"]
            elif stat["_id"] == "Expense":
                total_expense = stat["total"]
                
        net_balance = total_income - total_expense

        processed_stats = {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "count": transaction_count
        }

        # 3. Monthly Cash Flow Trend (Group by Month instead of raw dates)
        cash_flow_trend = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {
                "$project": {
                    "year_month": {"$substr": ["$date", 0, 7]}, # Extracts YYYY-MM
                    "transaction_type": 1,
                    "amount": 1
                }
            },
            {
                "$group": {
                    "_id": {
                        "month": "$year_month",
                        "type": "$transaction_type"
                    },
                    "total": {"$sum": "$amount"}
                }
            },
            {
                "$group": {
                    "_id": "$_id.month",
                    "finances": {
                        "$push": {
                            "k": "$_id.type",
                            "v": "$total"
                        }
                    }
                }
            },
            {
                "$project": {
                    "month": "$_id",
                    "data": {"$arrayToObject": "$finances"}
                }
            },
            {"$sort": {"month": 1}}
        ]))

        # 4. Top spending categories
        top_categories = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "categories",
                    "let": {"category_id": "$category_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": [
                                        "$_id",
                                        {
                                            "$cond": [
                                                {"$eq": [{"$type": "$$category_id"}, "string"]},
                                                {"$toObjectId": "$$category_id"},
                                                "$_id"
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "category_info"
                }
            },
            {
                "$group": {
                    "_id": {"category_id": "$category_id", "category_name": {"$arrayElemAt": ["$category_info.name", 0]}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]))

        return jsonify({
            "category_totals": category_totals,
            "statistics": processed_stats,
            "expense_trend": cash_flow_trend,
            "top_categories": top_categories
        })
    except Exception as e:
        print(f"Error in get_analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/seed-data/<user_id>", methods=["POST"])
def seed_data(user_id):
    try:
        # Sample categories
        sample_categories = [
            {"user_id": user_id, "name": "Membership Dues"},
            {"user_id": user_id, "name": "Event Venues"},
            {"user_id": user_id, "name": "Marketing/Posters"},
            {"user_id": user_id, "name": "Food/Catering"},
            {"user_id": user_id, "name": "Equipment"},
            {"user_id": user_id, "name": "Miscellaneous"}
        ]

        # Insert categories and get their IDs
        category_results = []
        for cat in sample_categories:
            existing = categories_collection.find_one({"name": cat["name"], "user_id": user_id})
            if existing:
                category_results.append(str(existing["_id"]))
            else:
                result = categories_collection.insert_one(cat)
                category_results.append(str(result.inserted_id))

        # Sample expenses with organization context spanning a full semester
        sample_expenses = [
            # AUGUST (Orientation & Rush Week)
            {"user_id": user_id, "category_id": category_results[0], "amount": 5000.00, "description": "University Org Subsidy - Fall Semester", "date": "2025-08-01", "transaction_type": "Income", "or_number": "INC-001"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 850.00, "description": "Rush Week Banners & Tarpaulins", "date": "2025-08-05", "transaction_type": "Expense", "or_number": "EXP-001"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 1200.00, "description": "Orientation Snacks & Drinks (200 pax)", "date": "2025-08-10", "transaction_type": "Expense", "or_number": "EXP-002"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 1500.00, "description": "Main Hall Reservation - Welcome Assembly", "date": "2025-08-12", "transaction_type": "Expense", "or_number": "EXP-003"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 4500.00, "description": "Membership Dues - Freshmen Batch 1", "date": "2025-08-15", "transaction_type": "Income", "or_number": "INC-002"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 3800.00, "description": "Membership Dues - Freshmen Batch 2", "date": "2025-08-18", "transaction_type": "Income", "or_number": "INC-003"},
            {"user_id": user_id, "category_id": category_results[4], "amount": 950.00, "description": "New Portable PA System", "date": "2025-08-20", "transaction_type": "Expense", "or_number": "EXP-004"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 350.00, "description": "Office Supplies (Markers, Tape, Scissors)", "date": "2025-08-22", "transaction_type": "Expense", "or_number": "EXP-005"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 2200.00, "description": "Membership Dues - Sophomores", "date": "2025-08-25", "transaction_type": "Income", "or_number": "INC-004"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 400.00, "description": "Exec Comm Meeting Dinner", "date": "2025-08-28", "transaction_type": "Expense", "or_number": "EXP-006"},
            
            # SEPTEMBER (Workshops & Seminars)
            {"user_id": user_id, "category_id": category_results[0], "amount": 1500.00, "description": "Membership Dues - Juniors & Seniors", "date": "2025-09-02", "transaction_type": "Income", "or_number": "INC-005"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 450.00, "description": "Social Media Boost - Workshop Ads", "date": "2025-09-05", "transaction_type": "Expense", "or_number": "EXP-007"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 800.00, "description": "Lab Room Rental - Python Basics", "date": "2025-09-08", "transaction_type": "Expense", "or_number": "EXP-008"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 600.00, "description": "Workshop Speaker Tokens & Lunch", "date": "2025-09-10", "transaction_type": "Expense", "or_number": "EXP-009"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 3000.00, "description": "Corporate Sponsorship - CodeCamp Inc.", "date": "2025-09-15", "transaction_type": "Income", "or_number": "INC-006"},
            {"user_id": user_id, "category_id": category_results[4], "amount": 1200.00, "description": "Projector Screen & Adapters", "date": "2025-09-18", "transaction_type": "Expense", "or_number": "EXP-010"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 950.00, "description": "Auditorium - Tech Talk Series 1", "date": "2025-09-22", "transaction_type": "Expense", "or_number": "EXP-011"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 250.00, "description": "Flyer Printing - Tech Talk", "date": "2025-09-23", "transaction_type": "Expense", "or_number": "EXP-012"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 1800.00, "description": "Tech Talk Non-Member Ticket Sales", "date": "2025-09-26", "transaction_type": "Income", "or_number": "INC-007"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 150.00, "description": "Monthly Web Hosting & Domain", "date": "2025-09-30", "transaction_type": "Expense", "or_number": "EXP-013"},

            # OCTOBER (Midterms & IT Week Prep)
            {"user_id": user_id, "category_id": category_results[3], "amount": 350.00, "description": "Midterm Study Group Snacks", "date": "2025-10-05", "transaction_type": "Expense", "or_number": "EXP-014"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 2500.00, "description": "Fundraising - Merch Pre-orders", "date": "2025-10-10", "transaction_type": "Income", "or_number": "INC-008"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 1800.00, "description": "IT Week Shirts Production (Deposit)", "date": "2025-10-12", "transaction_type": "Expense", "or_number": "EXP-015"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 2000.00, "description": "Gymnasium Booking - IT Olympics", "date": "2025-10-15", "transaction_type": "Expense", "or_number": "EXP-016"},
            {"user_id": user_id, "category_id": category_results[4], "amount": 400.00, "description": "Network Cables & Switches for LAN Party", "date": "2025-10-18", "transaction_type": "Expense", "or_number": "EXP-017"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 1200.00, "description": "Esports Tournament Entry Fees", "date": "2025-10-20", "transaction_type": "Income", "or_number": "INC-009"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 850.00, "description": "Trophies and Medals - IT Olympics", "date": "2025-10-25", "transaction_type": "Expense", "or_number": "EXP-018"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 2800.00, "description": "IT Week Opening Day Catering", "date": "2025-10-28", "transaction_type": "Expense", "or_number": "EXP-019"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 1800.00, "description": "IT Week Shirts Production (Full Payment)", "date": "2025-10-29", "transaction_type": "Expense", "or_number": "EXP-020"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 4200.00, "description": "Merch Sales - IT Week Booth", "date": "2025-10-31", "transaction_type": "Income", "or_number": "INC-010"},

            # NOVEMBER (Post-Event & Planning)
            {"user_id": user_id, "category_id": category_results[3], "amount": 1500.00, "description": "IT Week Volunteers Celebration Dinner", "date": "2025-11-05", "transaction_type": "Expense", "or_number": "EXP-021"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 200.00, "description": "Post-event Cleaning Fees", "date": "2025-11-08", "transaction_type": "Expense", "or_number": "EXP-022"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 800.00, "description": "Late Merch Sales", "date": "2025-11-12", "transaction_type": "Income", "or_number": "INC-011"},
            {"user_id": user_id, "category_id": category_results[4], "amount": 550.00, "description": "Replacement Microphones", "date": "2025-11-15", "transaction_type": "Expense", "or_number": "EXP-023"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 600.00, "description": "Conference Room - Planning Session", "date": "2025-11-18", "transaction_type": "Expense", "or_number": "EXP-024"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 350.00, "description": "Planning Session Food", "date": "2025-11-20", "transaction_type": "Expense", "or_number": "EXP-025"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 150.00, "description": "Monthly Web Hosting", "date": "2025-11-25", "transaction_type": "Expense", "or_number": "EXP-026"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 300.00, "description": "Holiday Drive Posters", "date": "2025-11-28", "transaction_type": "Expense", "or_number": "EXP-027"},

            # DECEMBER (Year-End & Charity)
            {"user_id": user_id, "category_id": category_results[0], "amount": 5500.00, "description": "Fundraiser - Charity Stream Donations", "date": "2025-12-02", "transaction_type": "Income", "or_number": "INC-012"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 5000.00, "description": "Donation Remittance to Partner Charity", "date": "2025-12-05", "transaction_type": "Expense", "or_number": "EXP-028"},
            {"user_id": user_id, "category_id": category_results[1], "amount": 1800.00, "description": "Banquet Hall - Year-End Gala", "date": "2025-12-10", "transaction_type": "Expense", "or_number": "EXP-029"},
            {"user_id": user_id, "category_id": category_results[3], "amount": 3500.00, "description": "Catering - Year-End Gala", "date": "2025-12-12", "transaction_type": "Expense", "or_number": "EXP-030"},
            {"user_id": user_id, "category_id": category_results[4], "amount": 600.00, "description": "Photo Booth Rental - Gala", "date": "2025-12-12", "transaction_type": "Expense", "or_number": "EXP-031"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 2500.00, "description": "Gala Ticket Sales", "date": "2025-12-14", "transaction_type": "Income", "or_number": "INC-013"},
            {"user_id": user_id, "category_id": category_results[5], "amount": 800.00, "description": "Outgoing Officer Tokens", "date": "2025-12-16", "transaction_type": "Expense", "or_number": "EXP-032"},
            {"user_id": user_id, "category_id": category_results[2], "amount": 150.00, "description": "Yearbook Ad Placement", "date": "2025-12-18", "transaction_type": "Expense", "or_number": "EXP-033"},
            {"user_id": user_id, "category_id": category_results[0], "amount": 1200.00, "description": "Alumni Association Grant", "date": "2025-12-20", "transaction_type": "Income", "or_number": "INC-014"}
        ]

        inserted_count = 0
        for expense in sample_expenses:
            existing = expenses_collection.find_one({
                "user_id": expense["user_id"],
                "description": expense["description"],
                "date": expense["date"]
            })
            if not existing:
                expenses_collection.insert_one(expense)
                inserted_count += 1

        return jsonify({
            "message": f"Seed data created",
            "categories_created": len(category_results),
            "expenses_created": inserted_count
        }), 201
    except Exception as e:
        print(f"Error in seed_data: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)