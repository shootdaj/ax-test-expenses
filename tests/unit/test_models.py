"""Unit tests for expense models and in-memory storage."""

import pytest

from app.models import (
    CATEGORIES,
    create_expense,
    delete_expense,
    expenses_to_csv,
    get_all_expenses,
    get_expense,
    update_expense,
)


class TestCategories:
    """Tests for category definitions."""

    def test_categories_exist(self):
        assert len(CATEGORIES) >= 9

    def test_each_category_has_name_and_icon(self):
        for key, cat in CATEGORIES.items():
            assert "name" in cat, f"Category {key} missing name"
            assert "icon" in cat, f"Category {key} missing icon"

    def test_expected_categories_present(self):
        expected = ["food", "transport", "housing", "utilities",
                    "entertainment", "healthcare", "shopping", "education", "other"]
        for cat in expected:
            assert cat in CATEGORIES


class TestCreateExpense:
    """Tests for creating expenses."""

    def test_create_valid_expense(self):
        expense = create_expense(50.0, "food", "Lunch")
        assert expense["amount"] == 50.0
        assert expense["category"] == "food"
        assert expense["description"] == "Lunch"
        assert "id" in expense
        assert "date" in expense
        assert "created_at" in expense

    def test_create_expense_with_all_fields(self):
        expense = create_expense(
            amount=100.50,
            category="transport",
            description="Gas",
            date="2026-03-01",
            payment_method="credit_card",
        )
        assert expense["amount"] == 100.50
        assert expense["date"] == "2026-03-01"
        assert expense["payment_method"] == "credit_card"

    def test_create_expense_rounds_amount(self):
        expense = create_expense(50.556, "food", "Test")
        assert expense["amount"] == 50.56

    def test_create_expense_invalid_category(self):
        with pytest.raises(ValueError, match="Invalid category"):
            create_expense(50.0, "invalid_cat", "Test")

    def test_create_expense_invalid_payment_method(self):
        with pytest.raises(ValueError, match="Invalid payment method"):
            create_expense(50.0, "food", "Test", payment_method="bitcoin")

    def test_create_expense_negative_amount(self):
        with pytest.raises(ValueError, match="Amount must be positive"):
            create_expense(-10.0, "food", "Test")

    def test_create_expense_zero_amount(self):
        with pytest.raises(ValueError, match="Amount must be positive"):
            create_expense(0, "food", "Test")


class TestGetExpense:
    """Tests for retrieving expenses."""

    def test_get_existing_expense(self):
        created = create_expense(50.0, "food", "Lunch")
        fetched = get_expense(created["id"])
        assert fetched == created

    def test_get_nonexistent_expense(self):
        result = get_expense("nonexistent-id")
        assert result is None


class TestGetAllExpenses:
    """Tests for listing and filtering expenses."""

    def test_get_all_empty(self):
        assert get_all_expenses() == []

    def test_get_all_returns_all(self):
        create_expense(50.0, "food", "Lunch")
        create_expense(30.0, "transport", "Bus")
        assert len(get_all_expenses()) == 2

    def test_filter_by_category(self):
        create_expense(50.0, "food", "Lunch")
        create_expense(30.0, "transport", "Bus")
        result = get_all_expenses(category="food")
        assert len(result) == 1
        assert result[0]["category"] == "food"

    def test_filter_by_date_range(self):
        create_expense(50.0, "food", "A", date="2026-01-01")
        create_expense(30.0, "food", "B", date="2026-02-15")
        create_expense(20.0, "food", "C", date="2026-03-01")
        result = get_all_expenses(date_from="2026-02-01", date_to="2026-02-28")
        assert len(result) == 1
        assert result[0]["description"] == "B"

    def test_filter_by_amount_range(self):
        create_expense(10.0, "food", "Small")
        create_expense(50.0, "food", "Medium")
        create_expense(100.0, "food", "Big")
        result = get_all_expenses(amount_min=20.0, amount_max=80.0)
        assert len(result) == 1
        assert result[0]["description"] == "Medium"

    def test_results_sorted_by_date_descending(self):
        create_expense(50.0, "food", "Old", date="2026-01-01")
        create_expense(30.0, "food", "New", date="2026-03-01")
        result = get_all_expenses()
        assert result[0]["date"] == "2026-03-01"
        assert result[1]["date"] == "2026-01-01"


class TestUpdateExpense:
    """Tests for updating expenses."""

    def test_update_amount(self):
        created = create_expense(50.0, "food", "Lunch")
        updated = update_expense(created["id"], amount=75.0)
        assert updated["amount"] == 75.0

    def test_update_category(self):
        created = create_expense(50.0, "food", "Lunch")
        updated = update_expense(created["id"], category="entertainment")
        assert updated["category"] == "entertainment"

    def test_update_nonexistent(self):
        result = update_expense("nonexistent", amount=50.0)
        assert result is None

    def test_update_invalid_category(self):
        created = create_expense(50.0, "food", "Lunch")
        with pytest.raises(ValueError):
            update_expense(created["id"], category="invalid")

    def test_update_negative_amount(self):
        created = create_expense(50.0, "food", "Lunch")
        with pytest.raises(ValueError):
            update_expense(created["id"], amount=-5.0)


class TestDeleteExpense:
    """Tests for deleting expenses."""

    def test_delete_existing(self):
        created = create_expense(50.0, "food", "Lunch")
        assert delete_expense(created["id"]) is True
        assert get_expense(created["id"]) is None

    def test_delete_nonexistent(self):
        assert delete_expense("nonexistent") is False


class TestExpensesToCsv:
    """Tests for CSV export."""

    def test_empty_csv(self):
        csv = expenses_to_csv([])
        assert csv == "id,amount,category,description,date,payment_method"

    def test_csv_with_expenses(self):
        expense = create_expense(50.0, "food", "Lunch", date="2026-03-01")
        csv = expenses_to_csv([expense])
        lines = csv.split("\n")
        assert len(lines) == 2
        assert "50.0" in lines[1]
        assert "food" in lines[1]

    def test_csv_escapes_quotes(self):
        expense = create_expense(50.0, "food", 'Lunch "special"', date="2026-03-01")
        csv = expenses_to_csv([expense])
        assert '""special""' in csv
