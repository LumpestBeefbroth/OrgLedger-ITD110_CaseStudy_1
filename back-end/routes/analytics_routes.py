"""
Analytics Routes Blueprint
Location: back-end/routes/analytics_routes.py

Handles complex analytics and reporting with MongoDB aggregation pipelines.
Includes Virtual Wallet calculation, spending analysis, and cash flow trends.
"""

import sys
import os
from flask import Blueprint, request, jsonify
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import expenses_collection, categories_collection

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route("/analytics/<user_id>", methods=["GET"])
def get_analytics(user_id):
    try:
        category_totals = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$category_id",
                "amount": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$lookup": {
                "from": "categories",
                "let": {"category_id": "$_id"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$eq": [{"$toString": "$_id"}, "$$category_id"]}
                    }},
                    {"$project": {"name": 1, "_id": 0}}
                ],
                "as": "category_info"
            }},
            {"$addFields": {
                "category_name": {
                    "$ifNull": [
                        {"$arrayElemAt": ["$category_info.name", 0]},
                        "Uncategorized"
                    ]
                }
            }},
            {"$project": {"category_name": 1, "amount": 1, "count": 1, "_id": 0}}
        ]))

        stats_agg = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$facet": {
                "stats_data": [
                    {"$group": {
                        "_id": "$transaction_type",
                        "total": {"$sum": "$amount"}
                    }}
                ],
                "top_categories": [
                    {"$group": {
                        "_id": "$category_id",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": 5},
                    {"$lookup": {
                        "from": "categories",
                        "let": {"category_id": "$_id"},
                        "pipeline": [
                            {"$match": {
                                "$expr": {"$eq": [{"$toString": "$_id"}, "$$category_id"]}
                            }},
                            {"$project": {"name": 1, "_id": 0}}
                        ],
                        "as": "category_info"
                    }},
                    {"$addFields": {
                        "category_name": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$category_info.name", 0]},
                                "Uncategorized"
                            ]
                        }
                    }},
                    {"$project": {"category_name": 1, "count": 1, "_id": 0}}
                ]
            }}
        ]))

        income_expense = {}
        if stats_agg:
            for item in stats_agg[0]["stats_data"]:
                income_expense[item["_id"]] = item["total"]

        total_income = income_expense.get("Income", 0)
        total_expense = income_expense.get("Expense", 0)
        net_balance = total_income - total_expense

        cash_flow = list(expenses_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": {"$substr": ["$date", 0, 7]},
                "income": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$transaction_type", "Income"]},
                            "$amount",
                            0
                        ]
                    }
                },
                "expense": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$transaction_type", "Expense"]},
                            "$amount",
                            0
                        ]
                    }
                }
            }},
            {"$sort": {"_id": 1}}
        ]))

        cash_flow_trend = {}
        for item in cash_flow:
            month = item["_id"]
            cash_flow_trend[month] = {
                "income": item["income"],
                "expense": item["expense"]
            }

        # Count total transactions
        total_count = sum(item["amount"] for item in category_totals)
        
        # Transform category totals to match frontend expectations
        formatted_categories = []
        for item in category_totals:
            formatted_categories.append({
                "_id": {"category_name": item.get("category_name", "Uncategorized")},
                "total": item.get("amount", 0),
                "count": item.get("count", 0)
            })
        
        # Transform cash flow trend to match frontend expectations (expense_trend)
        expense_trend = []
        for month, flow_data in sorted(cash_flow_trend.items()):
            expense_trend.append({
                "month": month,
                "data": {
                    "Income": flow_data.get("income", 0),
                    "Expense": flow_data.get("expense", 0)
                }
            })

        response = {
            "statistics": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_balance": net_balance,
                "count": int(expenses_collection.count_documents({"user_id": user_id}))
            },
            "category_totals": formatted_categories,
            "expense_trend": expense_trend
        }

        return jsonify(response)
    except Exception as e:
        print(f"Error in get_analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500
