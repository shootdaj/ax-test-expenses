"""In-memory data models and storage for the expense tracker."""

import uuid
from datetime import datetime, timezone

# Predefined categories with icons
CATEGORIES = {
    "food": {"name": "Food & Dining", "icon": "🍔"},
    "transport": {"name": "Transportation", "icon": "🚗"},
    "housing": {"name": "Housing", "icon": "🏠"},
    "utilities": {"name": "Utilities", "icon": "💡"},
    "entertainment": {"name": "Entertainment", "icon": "🎬"},
    "healthcare": {"name": "Healthcare", "icon": "🏥"},
    "shopping": {"name": "Shopping", "icon": "🛍️"},
    "education": {"name": "Education", "icon": "📚"},
    "other": {"name": "Other", "icon": "📦"},
}

PAYMENT_METHODS = ["cash", "credit_card", "debit_card", "bank_transfer", "other"]

# In-memory storage
expenses_db: dict[str, dict] = {}
budgets_db: dict[str, dict] = {}
recurring_db: dict[str, dict] = {}


def reset_db():
    """Reset all in-memory databases. Used for testing."""
    expenses_db.clear()
    budgets_db.clear()
    recurring_db.clear()


def create_expense(amount: float, category: str, description: str,
                   date: str | None = None, payment_method: str = "cash") -> dict:
    """Create a new expense and store it."""
    expense_id = str(uuid.uuid4())
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Valid: {list(CATEGORIES.keys())}")
    if payment_method not in PAYMENT_METHODS:
        raise ValueError(f"Invalid payment method: {payment_method}. Valid: {PAYMENT_METHODS}")
    if amount <= 0:
        raise ValueError("Amount must be positive")

    expense = {
        "id": expense_id,
        "amount": round(float(amount), 2),
        "category": category,
        "description": description,
        "date": date,
        "payment_method": payment_method,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    expenses_db[expense_id] = expense
    return expense


def get_expense(expense_id: str) -> dict | None:
    """Get a single expense by ID."""
    return expenses_db.get(expense_id)


def get_all_expenses(category: str | None = None,
                     date_from: str | None = None,
                     date_to: str | None = None,
                     amount_min: float | None = None,
                     amount_max: float | None = None) -> list[dict]:
    """Get all expenses with optional filtering."""
    result = list(expenses_db.values())

    if category:
        result = [e for e in result if e["category"] == category]
    if date_from:
        result = [e for e in result if e["date"] >= date_from]
    if date_to:
        result = [e for e in result if e["date"] <= date_to]
    if amount_min is not None:
        result = [e for e in result if e["amount"] >= amount_min]
    if amount_max is not None:
        result = [e for e in result if e["amount"] <= amount_max]

    result.sort(key=lambda e: e["date"], reverse=True)
    return result


def update_expense(expense_id: str, **kwargs) -> dict | None:
    """Update an existing expense."""
    expense = expenses_db.get(expense_id)
    if not expense:
        return None

    if "category" in kwargs and kwargs["category"] not in CATEGORIES:
        raise ValueError(f"Invalid category: {kwargs['category']}")
    if "payment_method" in kwargs and kwargs["payment_method"] not in PAYMENT_METHODS:
        raise ValueError(f"Invalid payment method: {kwargs['payment_method']}")
    if "amount" in kwargs and kwargs["amount"] <= 0:
        raise ValueError("Amount must be positive")

    for key in ["amount", "category", "description", "date", "payment_method"]:
        if key in kwargs:
            expense[key] = kwargs[key]
    if "amount" in kwargs:
        expense["amount"] = round(float(expense["amount"]), 2)

    return expense


def delete_expense(expense_id: str) -> bool:
    """Delete an expense. Returns True if found and deleted."""
    if expense_id in expenses_db:
        del expenses_db[expense_id]
        return True
    return False


def expenses_to_csv(expenses: list[dict]) -> str:
    """Convert a list of expenses to CSV format."""
    lines = ["id,amount,category,description,date,payment_method"]
    for e in expenses:
        desc = e["description"].replace('"', '""')
        lines.append(
            f'{e["id"]},{e["amount"]},{e["category"]},"{desc}",{e["date"]},{e["payment_method"]}'
        )
    return "\n".join(lines)
