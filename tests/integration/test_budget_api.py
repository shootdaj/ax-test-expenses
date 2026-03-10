"""Integration tests for budget API endpoints."""

import pytest

pytestmark = pytest.mark.integration


class TestBudgetCrud:
    def test_create_budget(self, client):
        resp = client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        assert resp.status_code == 201
        assert resp.get_json()["amount"] == 500.0

    def test_list_budgets(self, client):
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        resp = client.get("/api/budgets")
        assert len(resp.get_json()) == 1

    def test_list_budgets_by_month(self, client):
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-04", "amount": 600.0
        })
        resp = client.get("/api/budgets?month=2026-03")
        assert len(resp.get_json()) == 1

    def test_update_budget(self, client):
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        resp = client.put(
            "/api/budgets/food_2026-03", json={"amount": 750.0}
        )
        assert resp.status_code == 200
        assert resp.get_json()["amount"] == 750.0

    def test_delete_budget(self, client):
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        resp = client.delete("/api/budgets/food_2026-03")
        assert resp.status_code == 200

    def test_budget_status(self, client):
        client.post("/api/budgets", json={
            "category": "food", "month": "2026-03", "amount": 500.0
        })
        client.post("/api/expenses", json={
            "amount": 100.0, "category": "food",
            "description": "Lunch", "date": "2026-03-01"
        })
        resp = client.get("/api/budgets/status?month=2026-03")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["spent"] == 100.0
        assert data[0]["remaining"] == 400.0

    def test_budget_status_missing_month(self, client):
        resp = client.get("/api/budgets/status")
        assert resp.status_code == 400

    def test_create_budget_missing_fields(self, client):
        resp = client.post("/api/budgets", json={"category": "food"})
        assert resp.status_code == 400


class TestRecurringApi:
    def test_create_recurring(self, client):
        resp = client.post("/api/recurring", json={
            "amount": 5.0, "category": "food",
            "description": "Coffee", "interval": "daily",
            "start_date": "2026-03-01",
        })
        assert resp.status_code == 201
        assert resp.get_json()["interval"] == "daily"

    def test_list_recurring(self, client):
        client.post("/api/recurring", json={
            "amount": 5.0, "category": "food",
            "description": "Coffee", "interval": "daily",
            "start_date": "2026-03-01",
        })
        resp = client.get("/api/recurring")
        assert len(resp.get_json()) == 1

    def test_generate_recurring(self, client):
        client.post("/api/recurring", json={
            "amount": 5.0, "category": "food",
            "description": "Coffee", "interval": "daily",
            "start_date": "2026-03-01",
        })
        resp = client.post(
            "/api/recurring/generate",
            json={"as_of_date": "2026-03-03"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["generated"] == 3

    def test_create_recurring_missing_fields(self, client):
        resp = client.post("/api/recurring", json={"amount": 5.0})
        assert resp.status_code == 400


class TestSummaryApi:
    def test_monthly_summary(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food",
            "description": "A", "date": "2026-03-01"
        })
        resp = client.get("/api/summaries/monthly?month=2026-03")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 50.0
        assert data["count"] == 1

    def test_monthly_summary_missing_month(self, client):
        resp = client.get("/api/summaries/monthly")
        assert resp.status_code == 400

    def test_weekly_summary(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food",
            "description": "A", "date": "2026-03-03"
        })
        resp = client.get(
            "/api/summaries/weekly?week_start=2026-03-03"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 50.0

    def test_weekly_summary_missing_param(self, client):
        resp = client.get("/api/summaries/weekly")
        assert resp.status_code == 400

    def test_trends(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food",
            "description": "A", "date": "2026-03-01"
        })
        resp = client.get("/api/summaries/trends?months=3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3
