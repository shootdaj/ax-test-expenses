"""Integration tests for expense API endpoints."""

import pytest

pytestmark = pytest.mark.integration


class TestHealthEndpoint:
    """Tests for health check."""

    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"


class TestCategoriesEndpoint:
    """Tests for categories endpoint."""

    def test_list_categories(self, client):
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "food" in data
        assert data["food"]["name"] == "Food & Dining"
        assert "icon" in data["food"]


class TestCreateExpenseEndpoint:
    """Tests for POST /api/expenses."""

    def test_create_expense(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0,
            "category": "food",
            "description": "Lunch",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["amount"] == 50.0
        assert "id" in data

    def test_create_expense_with_all_fields(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 100.0,
            "category": "transport",
            "description": "Gas",
            "date": "2026-03-01",
            "payment_method": "credit_card",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["date"] == "2026-03-01"
        assert data["payment_method"] == "credit_card"

    def test_create_expense_missing_fields(self, client):
        resp = client.post("/api/expenses", json={"amount": 50.0})
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]

    def test_create_expense_invalid_category(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0,
            "category": "invalid",
            "description": "Test",
        })
        assert resp.status_code == 400

    def test_create_expense_no_body(self, client):
        resp = client.post("/api/expenses", json=None)
        assert resp.status_code == 400


class TestListExpensesEndpoint:
    """Tests for GET /api/expenses."""

    def test_list_empty(self, client):
        resp = client.get("/api/expenses")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_all_expenses(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "A"
        })
        client.post("/api/expenses", json={
            "amount": 30.0, "category": "transport", "description": "B"
        })
        resp = client.get("/api/expenses")
        assert len(resp.get_json()) == 2

    def test_filter_by_category(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "A"
        })
        client.post("/api/expenses", json={
            "amount": 30.0, "category": "transport", "description": "B"
        })
        resp = client.get("/api/expenses?category=food")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["category"] == "food"

    def test_filter_by_date_range(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "A", "date": "2026-01-15"
        })
        client.post("/api/expenses", json={
            "amount": 30.0, "category": "food", "description": "B", "date": "2026-03-15"
        })
        resp = client.get("/api/expenses?date_from=2026-03-01&date_to=2026-03-31")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["description"] == "B"

    def test_filter_by_amount_range(self, client):
        client.post("/api/expenses", json={
            "amount": 10.0, "category": "food", "description": "Small"
        })
        client.post("/api/expenses", json={
            "amount": 100.0, "category": "food", "description": "Big"
        })
        resp = client.get("/api/expenses?amount_min=50&amount_max=200")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["description"] == "Big"


class TestGetExpenseEndpoint:
    """Tests for GET /api/expenses/:id."""

    def test_get_existing(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "Lunch"
        })
        expense_id = resp.get_json()["id"]
        resp = client.get(f"/api/expenses/{expense_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == expense_id

    def test_get_nonexistent(self, client):
        resp = client.get("/api/expenses/nonexistent")
        assert resp.status_code == 404


class TestUpdateExpenseEndpoint:
    """Tests for PUT /api/expenses/:id."""

    def test_update_expense(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "Lunch"
        })
        expense_id = resp.get_json()["id"]
        resp = client.put(f"/api/expenses/{expense_id}", json={"amount": 75.0})
        assert resp.status_code == 200
        assert resp.get_json()["amount"] == 75.0

    def test_update_nonexistent(self, client):
        resp = client.put("/api/expenses/nonexistent", json={"amount": 75.0})
        assert resp.status_code == 404

    def test_update_no_body(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "Lunch"
        })
        expense_id = resp.get_json()["id"]
        resp = client.put(f"/api/expenses/{expense_id}", json=None)
        assert resp.status_code == 400


class TestDeleteExpenseEndpoint:
    """Tests for DELETE /api/expenses/:id."""

    def test_delete_expense(self, client):
        resp = client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "Lunch"
        })
        expense_id = resp.get_json()["id"]
        resp = client.delete(f"/api/expenses/{expense_id}")
        assert resp.status_code == 200
        # Verify it's gone
        resp = client.get(f"/api/expenses/{expense_id}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/expenses/nonexistent")
        assert resp.status_code == 404


class TestExportEndpoint:
    """Tests for GET /api/expenses/export."""

    def test_export_csv(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "Lunch", "date": "2026-03-01"
        })
        resp = client.get("/api/expenses/export")
        assert resp.status_code == 200
        assert resp.content_type == "text/csv; charset=utf-8"
        csv_text = resp.data.decode()
        assert "id,amount,category,description,date,payment_method" in csv_text
        assert "50.0" in csv_text

    def test_export_empty(self, client):
        resp = client.get("/api/expenses/export")
        assert resp.status_code == 200
        csv_text = resp.data.decode()
        lines = csv_text.strip().split("\n")
        assert len(lines) == 1  # Header only

    def test_export_with_filter(self, client):
        client.post("/api/expenses", json={
            "amount": 50.0, "category": "food", "description": "A", "date": "2026-03-01"
        })
        client.post("/api/expenses", json={
            "amount": 30.0, "category": "transport", "description": "B", "date": "2026-03-01"
        })
        resp = client.get("/api/expenses/export?category=food")
        csv_text = resp.data.decode()
        lines = csv_text.strip().split("\n")
        assert len(lines) == 2  # Header + 1 expense
