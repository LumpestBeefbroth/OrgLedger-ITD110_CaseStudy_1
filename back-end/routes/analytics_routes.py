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
                "amount": {"$sum": "$amount"}
            }},
            {"$lookup": {
                "from": "categories",
                "localField": "_id",
                "foreignField": "_id",
                "as": "category_info"
            }},
            {"$addFields": {
                "category_name": {
                    "$cond": [
                        {"$eq": [{"$type": "$_id"}, "string"]},
                        "$_id",
                        {"$arrayElemAt": ["$category_info.name", 0]}
                    ]
                }
            }},
            {"$project": {"category_name": 1, "amount": 1, "_id": 0}}
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
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "category_info"
                    }},
                    {"$addFields": {
                        "category_name": {
                            "$cond": [
                                {"$eq": [{"$type": "$_id"}, "string"]},
                                "$_id",
                                {"$arrayElemAt": ["$category_info.name", 0]}
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

        response = {
            "virtual_wallet": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_balance": net_balance
            },
            "category_totals": category_totals,
            "cash_flow_trend": cash_flow_trend,
            "top_categories": stats_agg[0]["top_categories"] if stats_agg else []
        }

        return jsonify(response)
    except Exception as e:
        print(f"Error in get_analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500
