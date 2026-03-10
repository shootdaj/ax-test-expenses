"""Integration tests for dashboard endpoint."""

import pytest

pytestmark = pytest.mark.integration


class TestDashboardEndpoint:
    def test_dashboard_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Expense Tracker" in html
        assert "summary-cards" in html

    def test_dashboard_has_pie_chart_container(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "pie-chart" in html

    def test_dashboard_has_trend_chart_container(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "trend-chart" in html

    def test_dashboard_has_budget_bars_container(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "budget-bars" in html

    def test_dashboard_has_expense_form(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "exp-amount" in html
        assert "exp-category" in html
        assert "exp-desc" in html
        assert "Add Expense" in html

    def test_dashboard_has_filters(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "filter-from" in html
        assert "filter-category" in html
        assert "expense-list" in html
