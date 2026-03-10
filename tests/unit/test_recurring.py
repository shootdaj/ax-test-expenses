"""Unit tests for recurring expenses."""

import pytest

from app.models import (
    create_recurring,
    generate_recurring_expenses,
    get_all_recurring,
)


class TestCreateRecurring:
    def test_create_valid_recurring(self):
        rec = create_recurring(50.0, "food", "Daily coffee", "daily", "2026-03-01")
        assert rec["amount"] == 50.0
        assert rec["interval"] == "daily"
        assert rec["last_generated"] is None

    def test_create_recurring_invalid_interval(self):
        with pytest.raises(ValueError, match="Invalid interval"):
            create_recurring(50.0, "food", "Test", "hourly", "2026-03-01")

    def test_create_recurring_invalid_category(self):
        with pytest.raises(ValueError, match="Invalid category"):
            create_recurring(50.0, "invalid", "Test", "daily", "2026-03-01")


class TestGenerateRecurring:
    def test_generate_daily_expenses(self):
        create_recurring(5.0, "food", "Coffee", "daily", "2026-03-01")
        generated = generate_recurring_expenses("2026-03-03")
        assert len(generated) == 3  # Mar 1, 2, 3
        assert all(e["amount"] == 5.0 for e in generated)

    def test_generate_weekly_expenses(self):
        create_recurring(20.0, "transport", "Gas", "weekly", "2026-03-01")
        generated = generate_recurring_expenses("2026-03-15")
        assert len(generated) == 3  # Mar 1, Mar 8, Mar 15

    def test_generate_no_duplicates(self):
        create_recurring(5.0, "food", "Coffee", "daily", "2026-03-01")
        first = generate_recurring_expenses("2026-03-03")
        second = generate_recurring_expenses("2026-03-05")
        # Second call should only generate Mar 4 and Mar 5
        assert len(first) == 3
        assert len(second) == 2

    def test_get_all_recurring(self):
        create_recurring(5.0, "food", "Coffee", "daily", "2026-03-01")
        create_recurring(20.0, "transport", "Gas", "weekly", "2026-03-01")
        assert len(get_all_recurring()) == 2
