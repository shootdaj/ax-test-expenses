"""Flask routes for the expense tracker API."""

from flask import Response, jsonify, request

from app import app
from app.models import (
    CATEGORIES,
    create_expense,
    delete_expense,
    expenses_to_csv,
    get_all_expenses,
    get_expense,
    update_expense,
)


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/api/categories", methods=["GET"])
def list_categories():
    """Return all available expense categories."""
    return jsonify(CATEGORIES)


@app.route("/api/expenses", methods=["GET"])
def list_expenses():
    """List all expenses with optional filtering."""
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    amount_min = request.args.get("amount_min", type=float)
    amount_max = request.args.get("amount_max", type=float)

    expenses = get_all_expenses(
        category=category,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
    )
    return jsonify(expenses)


@app.route("/api/expenses", methods=["POST"])
def create_expense_route():
    """Create a new expense."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required = ["amount", "category", "description"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        expense = create_expense(
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            date=data.get("date"),
            payment_method=data.get("payment_method", "cash"),
        )
        return jsonify(expense), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/expenses/<expense_id>", methods=["GET"])
def get_expense_route(expense_id):
    """Get a single expense by ID."""
    expense = get_expense(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify(expense)


@app.route("/api/expenses/<expense_id>", methods=["PUT"])
def update_expense_route(expense_id):
    """Update an existing expense."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        expense = update_expense(expense_id, **data)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(expense)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/expenses/<expense_id>", methods=["DELETE"])
def delete_expense_route(expense_id):
    """Delete an expense."""
    if delete_expense(expense_id):
        return jsonify({"message": "Expense deleted"}), 200
    return jsonify({"error": "Expense not found"}), 404


@app.route("/api/expenses/export", methods=["GET"])
def export_expenses():
    """Export all expenses as CSV."""
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    amount_min = request.args.get("amount_min", type=float)
    amount_max = request.args.get("amount_max", type=float)

    expenses = get_all_expenses(
        category=category,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
    )
    csv_data = expenses_to_csv(expenses)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )
