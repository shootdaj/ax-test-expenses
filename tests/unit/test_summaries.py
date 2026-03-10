"""Unit tests for spending summaries."""

from app.models import (
    create_expense,
    get_monthly_summary,
    get_trends,
    get_weekly_summary,
)


class TestMonthlySummary:
    def test_monthly_summary(self):
        create_expense(50.0, "food", "Lunch", date="2026-03-01")
        create_expense(30.0, "food", "Coffee", date="2026-03-05")
        create_expense(100.0, "transport", "Gas", date="2026-03-10")

        summary = get_monthly_summary("2026-03")
        assert summary["month"] == "2026-03"
        assert summary["total"] == 180.0
        assert summary["count"] == 3
        assert summary["by_category"]["food"] == 80.0
        assert summary["by_category"]["transport"] == 100.0

    def test_monthly_summary_empty(self):
        summary = get_monthly_summary("2026-03")
        assert summary["total"] == 0
        assert summary["count"] == 0
        assert summary["by_category"] == {}


class TestWeeklySummary:
    def test_weekly_summary(self):
        create_expense(50.0, "food", "A", date="2026-03-03")
        create_expense(30.0, "food", "B", date="2026-03-05")
        create_expense(100.0, "transport", "C", date="2026-03-10")

        summary = get_weekly_summary("2026-03-03")
        assert summary["week_start"] == "2026-03-03"
        assert summary["week_end"] == "2026-03-09"
        assert summary["total"] == 80.0  # Only A and B
        assert summary["count"] == 2


class TestTrends:
    def test_trends_returns_months(self):
        create_expense(50.0, "food", "A", date="2026-03-01")
        create_expense(30.0, "food", "B", date="2026-02-01")

        trends = get_trends(months=3)
        assert len(trends) == 3
        # Should be in chronological order
        assert trends[-1]["month"] == "2026-03"
