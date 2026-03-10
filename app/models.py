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


# --- Budget functions ---

def create_budget(category: str, month: str, amount: float) -> dict:
    """Create or update a monthly budget for a category.
    month format: 'YYYY-MM'
    """
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    if amount <= 0:
        raise ValueError("Budget amount must be positive")

    budget_id = f"{category}_{month}"
    budget = {
        "id": budget_id,
        "category": category,
        "month": month,
        "amount": round(float(amount), 2),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    budgets_db[budget_id] = budget
    return budget


def get_budget(budget_id: str) -> dict | None:
    """Get a single budget by ID."""
    return budgets_db.get(budget_id)


def get_all_budgets(month: str | None = None) -> list[dict]:
    """Get all budgets, optionally filtered by month."""
    result = list(budgets_db.values())
    if month:
        result = [b for b in result if b["month"] == month]
    return result


def get_budget_status(month: str) -> list[dict]:
    """Get spending vs budget for each category in a given month."""
    budgets = get_all_budgets(month=month)
    month_start = f"{month}-01"
    month_end = f"{month}-31"
    expenses = get_all_expenses(date_from=month_start, date_to=month_end)

    # Calculate spending per category
    spending = {}
    for e in expenses:
        spending[e["category"]] = spending.get(e["category"], 0) + e["amount"]

    result = []
    for b in budgets:
        cat = b["category"]
        spent = round(spending.get(cat, 0), 2)
        result.append({
            "category": cat,
            "budget": b["amount"],
            "spent": spent,
            "remaining": round(b["amount"] - spent, 2),
            "percentage": round((spent / b["amount"]) * 100, 1) if b["amount"] > 0 else 0,
        })
    return result


def update_budget(budget_id: str, amount: float) -> dict | None:
    """Update a budget amount."""
    budget = budgets_db.get(budget_id)
    if not budget:
        return None
    if amount <= 0:
        raise ValueError("Budget amount must be positive")
    budget["amount"] = round(float(amount), 2)
    return budget


def delete_budget(budget_id: str) -> bool:
    """Delete a budget."""
    if budget_id in budgets_db:
        del budgets_db[budget_id]
        return True
    return False


# --- Recurring expense functions ---

RECURRENCE_INTERVALS = ["daily", "weekly", "monthly"]


def create_recurring(amount: float, category: str, description: str,
                     interval: str, start_date: str,
                     payment_method: str = "cash") -> dict:
    """Create a recurring expense template."""
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    if interval not in RECURRENCE_INTERVALS:
        raise ValueError(f"Invalid interval: {interval}. Valid: {RECURRENCE_INTERVALS}")
    if amount <= 0:
        raise ValueError("Amount must be positive")

    rec_id = str(uuid.uuid4())
    recurring = {
        "id": rec_id,
        "amount": round(float(amount), 2),
        "category": category,
        "description": description,
        "interval": interval,
        "start_date": start_date,
        "payment_method": payment_method,
        "last_generated": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    recurring_db[rec_id] = recurring
    return recurring


def get_all_recurring() -> list[dict]:
    """Get all recurring expense templates."""
    return list(recurring_db.values())


def generate_recurring_expenses(as_of_date: str | None = None) -> list[dict]:
    """Generate expenses from recurring templates up to the given date."""
    from datetime import timedelta

    if as_of_date is None:
        as_of_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    generated = []
    target = datetime.strptime(as_of_date, "%Y-%m-%d")

    for rec in recurring_db.values():
        start = datetime.strptime(rec["start_date"], "%Y-%m-%d")
        last_gen = (
            datetime.strptime(rec["last_generated"], "%Y-%m-%d")
            if rec["last_generated"]
            else start - timedelta(days=1)
        )

        if rec["interval"] == "daily":
            delta = timedelta(days=1)
        elif rec["interval"] == "weekly":
            delta = timedelta(weeks=1)
        elif rec["interval"] == "monthly":
            delta = timedelta(days=30)  # Approximate
        else:
            continue

        current = start
        while current <= target:
            if current > last_gen:
                expense = create_expense(
                    amount=rec["amount"],
                    category=rec["category"],
                    description=f"[Recurring] {rec['description']}",
                    date=current.strftime("%Y-%m-%d"),
                    payment_method=rec["payment_method"],
                )
                generated.append(expense)
                rec["last_generated"] = current.strftime("%Y-%m-%d")
            current += delta

    return generated


# --- Summary functions ---

def get_monthly_summary(month: str) -> dict:
    """Get spending summary for a given month (YYYY-MM)."""
    month_start = f"{month}-01"
    month_end = f"{month}-31"
    expenses = get_all_expenses(date_from=month_start, date_to=month_end)

    total = sum(e["amount"] for e in expenses)
    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]

    # Round values
    by_category = {k: round(v, 2) for k, v in by_category.items()}

    return {
        "month": month,
        "total": round(total, 2),
        "count": len(expenses),
        "by_category": by_category,
    }


def get_weekly_summary(week_start: str) -> dict:
    """Get spending summary for a week starting from week_start (YYYY-MM-DD)."""
    from datetime import timedelta

    start = datetime.strptime(week_start, "%Y-%m-%d")
    end = start + timedelta(days=6)
    week_end = end.strftime("%Y-%m-%d")

    expenses = get_all_expenses(date_from=week_start, date_to=week_end)
    total = sum(e["amount"] for e in expenses)
    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]
    by_category = {k: round(v, 2) for k, v in by_category.items()}

    return {
        "week_start": week_start,
        "week_end": week_end,
        "total": round(total, 2),
        "count": len(expenses),
        "by_category": by_category,
    }


def get_trends(months: int = 6) -> list[dict]:
    """Get monthly spending trends for the last N months."""
    now = datetime.now(timezone.utc)
    trends = []
    for i in range(months - 1, -1, -1):
        # Calculate month
        year = now.year
        month_num = now.month - i
        while month_num <= 0:
            month_num += 12
            year -= 1
        month_str = f"{year}-{month_num:02d}"
        summary = get_monthly_summary(month_str)
        trends.append({
            "month": month_str,
            "total": summary["total"],
            "count": summary["count"],
        })
    return trends


def expenses_to_csv(expenses: list[dict]) -> str:
    """Convert a list of expenses to CSV format."""
    lines = ["id,amount,category,description,date,payment_method"]
    for e in expenses:
        desc = e["description"].replace('"', '""')
        lines.append(
            f'{e["id"]},{e["amount"]},{e["category"]},"{desc}",{e["date"]},{e["payment_method"]}'
        )
    return "\n".join(lines)
