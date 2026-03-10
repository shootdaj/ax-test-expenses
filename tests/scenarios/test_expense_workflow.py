"""Scenario tests for full expense management workflows."""

import pytest

pytestmark = pytest.mark.scenario


class TestFullExpenseLifecycle:
    """Test complete expense creation, update, and deletion workflow."""

    def test_create_update_delete_expense(self, client):
        # Create an expense
        resp = client.post("/api/expenses", json={
            "amount": 50.0,
            "category": "food",
            "description": "Lunch at restaurant",
            "date": "2026-03-10",
            "payment_method": "credit_card",
        })
        assert resp.status_code == 201
        expense = resp.get_json()
        expense_id = expense["id"]

        # Verify it appears in the list
        resp = client.get("/api/expenses")
        assert len(resp.get_json()) == 1

        # Update the amount
        resp = client.put(f"/api/expenses/{expense_id}", json={
            "amount": 65.0,
            "description": "Lunch at restaurant (updated tip)",
        })
        assert resp.status_code == 200
        assert resp.get_json()["amount"] == 65.0

        # Verify update persisted
        resp = client.get(f"/api/expenses/{expense_id}")
        assert resp.get_json()["amount"] == 65.0

        # Delete the expense
        resp = client.delete(f"/api/expenses/{expense_id}")
        assert resp.status_code == 200

        # Verify it's gone
        resp = client.get("/api/expenses")
        assert len(resp.get_json()) == 0


class TestExpenseFilteringWorkflow:
    """Test filtering expenses across multiple dimensions."""

    def test_multi_filter_expenses(self, client):
        # Create expenses across categories and dates
        expenses = [
            {"amount": 50.0, "category": "food", "description": "Lunch", "date": "2026-03-01"},
            {"amount": 30.0, "category": "food", "description": "Coffee", "date": "2026-03-05"},
            {"amount": 100.0, "category": "transport", "description": "Gas", "date": "2026-03-03"},
            {"amount": 200.0, "category": "shopping",
             "description": "Clothes", "date": "2026-02-15"},
            {"amount": 15.0, "category": "food", "description": "Snack", "date": "2026-02-20"},
        ]
        for e in expenses:
            resp = client.post("/api/expenses", json=e)
            assert resp.status_code == 201

        # Filter by category
        resp = client.get("/api/expenses?category=food")
        assert len(resp.get_json()) == 3

        # Filter by date range
        resp = client.get("/api/expenses?date_from=2026-03-01&date_to=2026-03-31")
        assert len(resp.get_json()) == 3

        # Filter by amount range
        resp = client.get("/api/expenses?amount_min=40&amount_max=150")
        data = resp.get_json()
        assert len(data) == 2  # 50 + 100

        # Combined filters
        resp = client.get("/api/expenses?category=food&date_from=2026-03-01")
        data = resp.get_json()
        assert len(data) == 2  # March food expenses only


class TestCsvExportWorkflow:
    """Test CSV export with various expense data."""

    def test_export_all_expenses_to_csv(self, client):
        # Create several expenses
        for i in range(5):
            client.post("/api/expenses", json={
                "amount": 10.0 * (i + 1),
                "category": "food",
                "description": f"Expense {i+1}",
                "date": f"2026-03-{i+1:02d}",
            })

        # Export all
        resp = client.get("/api/expenses/export")
        assert resp.status_code == 200
        csv_text = resp.data.decode()
        lines = csv_text.strip().split("\n")
        assert len(lines) == 6  # Header + 5 expenses

        # Export filtered
        resp = client.get("/api/expenses/export?amount_min=30")
        csv_text = resp.data.decode()
        lines = csv_text.strip().split("\n")
        assert len(lines) == 4  # Header + 3 expenses (30, 40, 50)
