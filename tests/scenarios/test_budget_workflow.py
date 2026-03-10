"""Scenario tests for budget and recurring expense workflows."""

import pytest

pytestmark = pytest.mark.scenario


class TestBudgetTrackingWorkflow:
    """Full workflow: set budgets, spend, check status."""

    def test_budget_tracking_lifecycle(self, client):
        # Set budgets for March
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        client.post("/api/budgets", json={
            "category": "transport", "month": "2026-03", "amount": 200.0
        })

        # Add expenses
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food",
            "description": "Lunch", "date": "2026-03-01"
        })
        client.post("/api/expenses", json={
            "amount": 30.0, "category": "food",
            "description": "Coffee", "date": "2026-03-05"
        })
        client.post("/api/expenses", json={
            "amount": 75.0, "category": "transport",
            "description": "Gas", "date": "2026-03-03"
        })

        # Check budget status
        resp = client.get("/api/budgets/status?month=2026-03")
        data = resp.get_json()
        assert len(data) == 2

        food_status = next(s for s in data if s["category"] == "food")
        assert food_status["spent"] == 80.0
        assert food_status["remaining"] == 420.0
        assert food_status["percentage"] == 16.0

        transport_status = next(
            s for s in data if s["category"] == "transport"
        )
        assert transport_status["spent"] == 75.0
        assert transport_status["remaining"] == 125.0

        # Check monthly summary
        resp = client.get("/api/summaries/monthly?month=2026-03")
        data = resp.get_json()
        assert data["total"] == 155.0
        assert data["count"] == 3


class TestRecurringExpenseWorkflow:
    """Full workflow: create recurring, generate, verify expenses."""

    def test_recurring_generates_expenses(self, client):
        # Create a recurring expense
        resp = client.post("/api/recurring", json={
            "amount": 5.0, "category": "food",
            "description": "Daily coffee", "interval": "daily",
            "start_date": "2026-03-01",
        })
        assert resp.status_code == 201

        # Generate expenses for 3 days
        resp = client.post(
            "/api/recurring/generate",
            json={"as_of_date": "2026-03-03"},
        )
        data = resp.get_json()
        assert data["generated"] == 3

        # Verify expenses were created
        resp = client.get("/api/expenses?category=food")
        assert len(resp.get_json()) == 3

        # Check monthly summary includes recurring
        resp = client.get("/api/summaries/monthly?month=2026-03")
        data = resp.get_json()
        assert data["total"] == 15.0  # 3 x $5

        # Generate again - should not duplicate
        resp = client.post(
            "/api/recurring/generate",
            json={"as_of_date": "2026-03-03"},
        )
        assert resp.get_json()["generated"] == 0
