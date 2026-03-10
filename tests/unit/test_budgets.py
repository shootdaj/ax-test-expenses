"""Unit tests for budget management."""

import pytest

from app.models import (
    create_budget,
    create_expense,
    delete_budget,
    get_all_budgets,
    get_budget,
    get_budget_status,
    update_budget,
)


class TestCreateBudget:
    def test_create_valid_budget(self):
        budget = create_budget("food", "2026-03", 500.0)
        assert budget["category"] == "food"
        assert budget["month"] == "2026-03"
        assert budget["amount"] == 500.0
        assert budget["id"] == "food_2026-03"

    def test_create_budget_invalid_category(self):
        with pytest.raises(ValueError, match="Invalid category"):
            create_budget("invalid", "2026-03", 500.0)

    def test_create_budget_negative_amount(self):
        with pytest.raises(ValueError, match="positive"):
            create_budget("food", "2026-03", -100.0)


class TestGetBudgets:
    def test_get_all_budgets(self):
        create_budget("food", "2026-03", 500.0)
        create_budget("transport", "2026-03", 300.0)
        assert len(get_all_budgets()) == 2

    def test_get_budgets_by_month(self):
        create_budget("food", "2026-03", 500.0)
        create_budget("food", "2026-04", 600.0)
        result = get_all_budgets(month="2026-03")
        assert len(result) == 1
        assert result[0]["month"] == "2026-03"


class TestBudgetStatus:
    def test_budget_status_with_spending(self):
        create_budget("food", "2026-03", 500.0)
        create_expense(100.0, "food", "Lunch", date="2026-03-01")
        create_expense(50.0, "food", "Coffee", date="2026-03-05")

        status = get_budget_status("2026-03")
        assert len(status) == 1
        assert status[0]["category"] == "food"
        assert status[0]["budget"] == 500.0
        assert status[0]["spent"] == 150.0
        assert status[0]["remaining"] == 350.0
        assert status[0]["percentage"] == 30.0

    def test_budget_status_no_spending(self):
        create_budget("food", "2026-03", 500.0)
        status = get_budget_status("2026-03")
        assert status[0]["spent"] == 0
        assert status[0]["remaining"] == 500.0


class TestUpdateBudget:
    def test_update_budget_amount(self):
        create_budget("food", "2026-03", 500.0)
        updated = update_budget("food_2026-03", 750.0)
        assert updated["amount"] == 750.0

    def test_update_nonexistent_budget(self):
        result = update_budget("nonexistent", 500.0)
        assert result is None

    def test_update_negative_amount(self):
        create_budget("food", "2026-03", 500.0)
        with pytest.raises(ValueError):
            update_budget("food_2026-03", -100.0)


class TestDeleteBudget:
    def test_delete_budget(self):
        create_budget("food", "2026-03", 500.0)
        assert delete_budget("food_2026-03") is True
        assert get_budget("food_2026-03") is None

    def test_delete_nonexistent(self):
        assert delete_budget("nonexistent") is False
