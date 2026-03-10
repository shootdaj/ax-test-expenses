# Expense Tracker API

## What This Is

A full-stack Expense Tracker application built with Python/Flask. It provides a RESTful API for managing expenses, budgets, and financial summaries, paired with a clean dashboard frontend for visualizing spending patterns. Uses in-memory storage (Python dicts) for simplicity. Deployed to Vercel.

## Core Value

Users can quickly log expenses and see where their money is going through clear summaries and visual breakdowns.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] CRUD operations for expenses (amount, category, description, date, payment_method)
- [ ] Budget management — set monthly budgets per category, track spending vs budget
- [ ] Expense categories with icons
- [ ] Monthly/weekly summaries and aggregations
- [ ] CSV export endpoint
- [ ] Recurring expenses support
- [ ] Dashboard with spending summary cards
- [ ] Category breakdown pie chart (SVG)
- [ ] Budget progress bars
- [ ] Expense list with filters (date range, category, amount)
- [ ] Add expense form
- [ ] Monthly trend line chart

### Out of Scope

- User authentication — not needed for v1 demo
- Persistent database — using in-memory storage
- Mobile app — web-first
- Multi-currency support — single currency for v1
- Receipt scanning/OCR — complexity not warranted

## Context

- Python/Flask backend deployed to Vercel as serverless function
- Entry point at `api/index.py` with Vercel Python runtime
- In-memory storage using Python dicts (data resets on cold start, acceptable for demo)
- Frontend served as static HTML/CSS/JS from Flask routes
- SVG-based charts (no external charting library needed)

## Constraints

- **Stack**: Python 3.12, Flask — required by project spec
- **Deployment**: Vercel with `@vercel/python` runtime
- **Storage**: In-memory only (Python dicts) — no database
- **Entry point**: `api/index.py` imports from `app` module
- **Charts**: SVG-based, no external JS charting libraries

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| In-memory storage | Simplicity for demo, no DB setup needed | — Pending |
| SVG charts | No external dependencies, works everywhere | — Pending |
| Flask | Lightweight, well-supported on Vercel Python | — Pending |
| Single-file frontend | Simplicity, served by Flask | — Pending |

---
*Last updated: 2026-03-10 after initialization*
