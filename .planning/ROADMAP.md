# Roadmap: Expense Tracker API

## Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Core API & Categories | Build CRUD expense API with category support and CSV export | EXP-01, EXP-02, EXP-03, EXP-04, EXP-05, EXP-06, CAT-01, CAT-02 | 4 |
| 2 | Budgets, Recurring & Summaries | Add budget management, recurring expenses, and financial summaries | BUD-01, BUD-02, BUD-03, REC-01, REC-02, SUM-01, SUM-02, SUM-03 | 4 |
| 3 | Dashboard & Frontend | Build interactive dashboard with charts, filters, and forms | DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06 | 5 |

## Phase 1: Core API & Categories

**Goal:** Build the foundational Flask app with full expense CRUD, predefined categories with icons, filtering, and CSV export.

**Requirements:** EXP-01, EXP-02, EXP-03, EXP-04, EXP-05, EXP-06, CAT-01, CAT-02

**Success Criteria:**
1. POST /api/expenses creates an expense and returns it with an ID
2. GET /api/expenses returns all expenses and supports filtering by date range, category, and amount
3. PUT /api/expenses/:id and DELETE /api/expenses/:id work correctly
4. GET /api/expenses/export returns valid CSV with all expense data

## Phase 2: Budgets, Recurring & Summaries

**Goal:** Add budget management per category, recurring expense generation, and weekly/monthly spending summaries.

**Requirements:** BUD-01, BUD-02, BUD-03, REC-01, REC-02, SUM-01, SUM-02, SUM-03

**Success Criteria:**
1. POST/GET/PUT/DELETE /api/budgets manages monthly budgets per category with spending tracking
2. POST /api/recurring creates a recurring expense and GET /api/recurring/generate creates due entries
3. GET /api/summaries/monthly and /api/summaries/weekly return correct spending aggregations
4. GET /api/summaries/trends returns multi-month spending data

## Phase 3: Dashboard & Frontend

**Goal:** Build a clean, data-focused dashboard with summary cards, SVG pie chart, budget progress bars, filterable expense list, add expense form, and trend line chart.

**Requirements:** DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06

**Success Criteria:**
1. Dashboard loads at / and shows spending summary cards with total, budget remaining, and top category
2. SVG pie chart displays accurate category breakdown with colors and labels
3. Budget progress bars show spending vs budget for each category with visual fill
4. Expense list supports filtering by date range, category, and amount with live updates
5. Monthly trend SVG line chart shows spending over time with labeled axes

---
*Roadmap created: 2026-03-10*
*Last updated: 2026-03-10*
