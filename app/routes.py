"""Flask routes for the expense tracker API."""

from flask import Response, jsonify, request

from app import app
from app.models import (
    CATEGORIES,
    create_budget,
    create_expense,
    create_recurring,
    delete_budget,
    delete_expense,
    expenses_to_csv,
    generate_recurring_expenses,
    get_all_budgets,
    get_all_expenses,
    get_all_recurring,
    get_budget_status,
    get_expense,
    get_monthly_summary,
    get_trends,
    get_weekly_summary,
    update_budget,
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


# --- Budget routes ---


@app.route("/api/budgets", methods=["GET"])
def list_budgets():
    """List all budgets, optionally filtered by month."""
    month = request.args.get("month")
    budgets = get_all_budgets(month=month)
    return jsonify(budgets)


@app.route("/api/budgets", methods=["POST"])
def create_budget_route():
    """Create a monthly budget for a category."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required = ["category", "month", "amount"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        budget = create_budget(
            category=data["category"],
            month=data["month"],
            amount=data["amount"],
        )
        return jsonify(budget), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/budgets/<budget_id>", methods=["PUT"])
def update_budget_route(budget_id):
    """Update a budget amount."""
    data = request.get_json(silent=True)
    if not data or "amount" not in data:
        return jsonify({"error": "amount is required"}), 400

    try:
        budget = update_budget(budget_id, data["amount"])
        if not budget:
            return jsonify({"error": "Budget not found"}), 404
        return jsonify(budget)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/budgets/<budget_id>", methods=["DELETE"])
def delete_budget_route(budget_id):
    """Delete a budget."""
    if delete_budget(budget_id):
        return jsonify({"message": "Budget deleted"}), 200
    return jsonify({"error": "Budget not found"}), 404


@app.route("/api/budgets/status", methods=["GET"])
def budget_status():
    """Get spending vs budget for a given month."""
    month = request.args.get("month")
    if not month:
        return jsonify({"error": "month query parameter required (YYYY-MM)"}), 400
    status = get_budget_status(month)
    return jsonify(status)


# --- Recurring expense routes ---


@app.route("/api/recurring", methods=["GET"])
def list_recurring():
    """List all recurring expense templates."""
    return jsonify(get_all_recurring())


@app.route("/api/recurring", methods=["POST"])
def create_recurring_route():
    """Create a recurring expense template."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required = ["amount", "category", "description", "interval", "start_date"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        recurring = create_recurring(
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            interval=data["interval"],
            start_date=data["start_date"],
            payment_method=data.get("payment_method", "cash"),
        )
        return jsonify(recurring), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/recurring/generate", methods=["POST"])
def generate_recurring_route():
    """Generate expenses from recurring templates."""
    data = request.get_json(silent=True) or {}
    as_of_date = data.get("as_of_date")
    generated = generate_recurring_expenses(as_of_date=as_of_date)
    return jsonify({
        "generated": len(generated),
        "expenses": generated,
    })


# --- Summary routes ---


@app.route("/api/summaries/monthly", methods=["GET"])
def monthly_summary():
    """Get spending summary for a given month."""
    month = request.args.get("month")
    if not month:
        return jsonify({"error": "month query parameter required (YYYY-MM)"}), 400
    summary = get_monthly_summary(month)
    return jsonify(summary)


@app.route("/api/summaries/weekly", methods=["GET"])
def weekly_summary():
    """Get spending summary for a given week."""
    week_start = request.args.get("week_start")
    if not week_start:
        return jsonify(
            {"error": "week_start query parameter required (YYYY-MM-DD)"}
        ), 400
    summary = get_weekly_summary(week_start)
    return jsonify(summary)


@app.route("/api/summaries/trends", methods=["GET"])
def trends_summary():
    """Get monthly spending trends."""
    months = request.args.get("months", 6, type=int)
    trends = get_trends(months=months)
    return jsonify(trends)
