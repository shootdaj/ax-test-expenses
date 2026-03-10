"""Scenario tests for dashboard workflows via API."""

import pytest

pytestmark = pytest.mark.scenario


class TestDashboardDataWorkflow:
    """Test that dashboard data endpoints work together."""

    def test_full_dashboard_data_flow(self, client):
        """Simulate what the dashboard JS does on load."""
        # 1. Load categories
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        cats = resp.get_json()
        assert "food" in cats

        # 2. Add expenses
        for exp in [
            {"amount": 50.0, "category": "food",
             "description": "Lunch", "date": "2026-03-01"},
            {"amount": 30.0, "category": "food",
             "description": "Coffee", "date": "2026-03-05"},
            {"amount": 100.0, "category": "transport",
             "description": "Gas", "date": "2026-03-03"},
        ]:
            resp = client.post("/api/expenses", json=exp)
            assert resp.status_code == 201

        # 3. Set budgets
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        client.post("/api/budgets", json={
            "category": "transport", "month": "2026-03", "amount": 200.0
        })

        # 4. Get monthly summary (used for summary cards + pie chart)
        resp = client.get("/api/summaries/monthly?month=2026-03")
        summary = resp.get_json()
        assert summary["total"] == 180.0
        assert summary["count"] == 3
        assert summary["by_category"]["food"] == 80.0
        assert summary["by_category"]["transport"] == 100.0

        # 5. Get budget status (for progress bars)
        resp = client.get("/api/budgets/status?month=2026-03")
        budgets = resp.get_json()
        assert len(budgets) == 2
        food_budget = next(
            b for b in budgets if b["category"] == "food"
        )
        assert food_budget["percentage"] == 16.0

        # 6. Get trends (for line chart)
        resp = client.get("/api/summaries/trends?months=6")
        trends = resp.get_json()
        assert len(trends) == 6

        # 7. Get filtered expenses (for expense list)
        resp = client.get("/api/expenses?category=food")
        food_expenses = resp.get_json()
        assert len(food_expenses) == 2

        # 8. Dashboard page loads
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Expense Tracker" in resp.data.decode()


class TestAddExpenseViaFormWorkflow:
    """Simulate adding expense via the form and verifying it shows up."""

    def test_add_expense_and_verify_in_list(self, client):
        # Add an expense (simulating form submission)
        resp = client.post("/api/expenses", json={
            "amount": 42.50,
            "category": "entertainment",
            "description": "Movie tickets",
            "date": "2026-03-10",
            "payment_method": "credit_card",
        })
        assert resp.status_code == 201
        expense_id = resp.get_json()["id"]

        # Verify it appears in the list
        resp = client.get("/api/expenses")
        expenses = resp.get_json()
        assert len(expenses) == 1
        assert expenses[0]["description"] == "Movie tickets"

        # Verify monthly summary updated
        resp = client.get("/api/summaries/monthly?month=2026-03")
        assert resp.get_json()["total"] == 42.50

        # Delete via the X button
        resp = client.delete(f"/api/expenses/{expense_id}")
        assert resp.status_code == 200

        # Verify empty
        resp = client.get("/api/expenses")
        assert len(resp.get_json()) == 0
