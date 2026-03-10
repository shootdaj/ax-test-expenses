"""Dashboard route - serves the frontend HTML."""

from flask import render_template_string

from app import app

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Expense Tracker</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f7;
    color: #1d1d1f;
    line-height: 1.5;
}
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
header {
    background: #fff;
    border-bottom: 1px solid #e5e5e7;
    padding: 16px 0;
    margin-bottom: 24px;
}
header h1 { font-size: 24px; font-weight: 600; text-align: center; }
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.card-label { font-size: 13px; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; }
.card-value { font-size: 28px; font-weight: 700; margin-top: 4px; }
.card-value.green { color: #34c759; }
.card-value.red { color: #ff3b30; }
.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}
@media (max-width: 768px) { .charts-row { grid-template-columns: 1fr; } }
.chart-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.chart-card h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.budget-bars { margin-bottom: 24px; }
.budget-item { margin-bottom: 12px; }
.budget-header { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 4px; }
.budget-bar-bg {
    height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden;
}
.budget-bar-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.expense-section { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
.expense-section h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.filters {
    display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;
    padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;
}
.filters input, .filters select {
    padding: 8px 12px; border: 1px solid #d2d2d7; border-radius: 8px;
    font-size: 14px; background: #fff;
}
.filters button {
    padding: 8px 16px; background: #007aff; color: #fff; border: none;
    border-radius: 8px; font-size: 14px; cursor: pointer;
}
.filters button:hover { background: #0062cc; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 8px; font-size: 13px; color: #86868b;
     border-bottom: 1px solid #f0f0f0; }
td { padding: 10px 8px; border-bottom: 1px solid #f5f5f7; font-size: 14px; }
tr:hover { background: #f9f9fb; }
.cat-badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 12px; background: #f0f0f0;
}
.add-form {
    background: #fff; border-radius: 12px; padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px;
}
.add-form h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.form-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.form-group { flex: 1; min-width: 150px; }
.form-group label { display: block; font-size: 13px; color: #86868b; margin-bottom: 4px; }
.form-group input, .form-group select {
    width: 100%; padding: 8px 12px; border: 1px solid #d2d2d7;
    border-radius: 8px; font-size: 14px;
}
.btn-add {
    padding: 10px 24px; background: #34c759; color: #fff; border: none;
    border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600;
}
.btn-add:hover { background: #2db84d; }
.btn-delete {
    background: none; border: none; color: #ff3b30; cursor: pointer; font-size: 16px;
}
.toast {
    position: fixed; bottom: 20px; right: 20px; padding: 12px 20px;
    background: #1d1d1f; color: #fff; border-radius: 8px;
    font-size: 14px; display: none; z-index: 100;
}
svg text { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
</style>
</head>
<body>
<header><div class="container"><h1>Expense Tracker</h1></div></header>
<div class="container">
<!-- Summary Cards -->
<div class="summary-cards" id="summary-cards"></div>

<!-- Charts Row -->
<div class="charts-row">
    <div class="chart-card">
        <h2>Category Breakdown</h2>
        <div id="pie-chart"></div>
    </div>
    <div class="chart-card">
        <h2>Monthly Trend</h2>
        <div id="trend-chart"></div>
    </div>
</div>

<!-- Budget Progress -->
<div class="card budget-bars">
    <h2 style="font-size:16px;font-weight:600;margin-bottom:16px;">Budget Progress</h2>
    <div id="budget-bars"></div>
</div>

<!-- Add Expense Form -->
<div class="add-form">
    <h2>Add Expense</h2>
    <div class="form-row">
        <div class="form-group">
            <label>Amount ($)</label>
            <input type="number" id="exp-amount" step="0.01" min="0.01" placeholder="0.00">
        </div>
        <div class="form-group">
            <label>Category</label>
            <select id="exp-category"></select>
        </div>
        <div class="form-group">
            <label>Description</label>
            <input type="text" id="exp-desc" placeholder="What did you spend on?">
        </div>
        <div class="form-group">
            <label>Date</label>
            <input type="date" id="exp-date">
        </div>
        <div class="form-group">
            <label>Payment</label>
            <select id="exp-payment">
                <option value="cash">Cash</option>
                <option value="credit_card">Credit Card</option>
                <option value="debit_card">Debit Card</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="other">Other</option>
            </select>
        </div>
    </div>
    <button class="btn-add" onclick="addExpense()">Add Expense</button>
</div>

<!-- Expense List -->
<div class="expense-section">
    <h2>Expenses</h2>
    <div class="filters">
        <input type="date" id="filter-from" placeholder="From">
        <input type="date" id="filter-to" placeholder="To">
        <select id="filter-category"><option value="">All Categories</option></select>
        <input type="number" id="filter-min" placeholder="Min $" step="0.01">
        <input type="number" id="filter-max" placeholder="Max $" step="0.01">
        <button onclick="loadExpenses()">Filter</button>
    </div>
    <table>
        <thead><tr>
            <th>Date</th><th>Category</th><th>Description</th>
            <th>Amount</th><th>Payment</th><th></th>
        </tr></thead>
        <tbody id="expense-list"></tbody>
    </table>
</div>
</div>

<div class="toast" id="toast"></div>

<script>
const COLORS = ['#007aff','#34c759','#ff9500','#ff3b30','#af52de',
    '#5856d6','#ff2d55','#00c7be','#86868b'];
const CAT_ICONS = {};

function getCurrentMonth() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0');
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 2000);
}

async function api(path, opts) {
    const resp = await fetch(path, opts);
    return resp.json();
}

async function loadCategories() {
    const cats = await api('/api/categories');
    const sel1 = document.getElementById('exp-category');
    const sel2 = document.getElementById('filter-category');
    for (const [key, val] of Object.entries(cats)) {
        CAT_ICONS[key] = val.icon;
        sel1.innerHTML += `<option value="${key}">${val.icon} ${val.name}</option>`;
        sel2.innerHTML += `<option value="${key}">${val.icon} ${val.name}</option>`;
    }
}

async function loadSummary() {
    const month = getCurrentMonth();
    const data = await api(`/api/summaries/monthly?month=${month}`);
    const budgetData = await api(`/api/budgets/status?month=${month}`);
    const totalBudget = budgetData.reduce((s,b) => s + b.budget, 0);
    const totalRemaining = budgetData.reduce((s,b) => s + b.remaining, 0);
    const topCat = Object.entries(data.by_category || {})
        .sort((a,b) => b[1]-a[1])[0];

    document.getElementById('summary-cards').innerHTML = `
        <div class="card">
            <div class="card-label">Total Spent This Month</div>
            <div class="card-value">$${data.total.toFixed(2)}</div>
        </div>
        <div class="card">
            <div class="card-label">Budget Remaining</div>
            <div class="card-value ${totalRemaining >= 0 ? 'green' : 'red'}">
                $${totalRemaining.toFixed(2)}
            </div>
        </div>
        <div class="card">
            <div class="card-label">Expenses This Month</div>
            <div class="card-value">${data.count}</div>
        </div>
        <div class="card">
            <div class="card-label">Top Category</div>
            <div class="card-value" style="font-size:20px">
                ${topCat ? (CAT_ICONS[topCat[0]]||'') + ' $' + topCat[1].toFixed(2) : 'N/A'}
            </div>
        </div>
    `;
}

async function loadPieChart() {
    const month = getCurrentMonth();
    const data = await api(`/api/summaries/monthly?month=${month}`);
    const cats = Object.entries(data.by_category || {}).sort((a,b) => b[1]-a[1]);
    if (!cats.length) {
        document.getElementById('pie-chart').innerHTML =
            '<p style="color:#86868b;text-align:center;padding:40px">No data yet</p>';
        return;
    }
    const total = cats.reduce((s,c) => s + c[1], 0);
    let svg = '<svg viewBox="0 0 300 300" width="100%">';
    let angle = 0;
    const cx = 150, cy = 130, r = 100;
    cats.forEach(([cat, amt], i) => {
        const pct = amt / total;
        const a1 = angle;
        const a2 = angle + pct * 2 * Math.PI;
        const x1 = cx + r * Math.cos(a1);
        const y1 = cy + r * Math.sin(a1);
        const x2 = cx + r * Math.cos(a2);
        const y2 = cy + r * Math.sin(a2);
        const large = pct > 0.5 ? 1 : 0;
        svg += `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2} Z"
            fill="${COLORS[i % COLORS.length]}" opacity="0.85"/>`;
        angle = a2;
    });
    let ly = 260;
    cats.forEach(([cat, amt], i) => {
        const pct = ((amt/total)*100).toFixed(1);
        svg += `<rect x="${20 + (i % 3)*100}" y="${ly + Math.floor(i/3)*18}"
            width="10" height="10" fill="${COLORS[i % COLORS.length]}" rx="2"/>`;
        svg += `<text x="${34 + (i % 3)*100}" y="${ly + 10 + Math.floor(i/3)*18}"
            font-size="11" fill="#1d1d1f">${CAT_ICONS[cat]||''} ${pct}%</text>`;
    });
    svg += '</svg>';
    document.getElementById('pie-chart').innerHTML = svg;
}

async function loadTrendChart() {
    const data = await api('/api/summaries/trends?months=6');
    if (!data.length) {
        document.getElementById('trend-chart').innerHTML =
            '<p style="color:#86868b;text-align:center;padding:40px">No data yet</p>';
        return;
    }
    const maxVal = Math.max(...data.map(d => d.total), 1);
    const w = 300, h = 200, pad = 40;
    const pw = (w - pad*2) / Math.max(data.length - 1, 1);
    let svg = `<svg viewBox="0 0 ${w} ${h+30}" width="100%">`;
    // Grid lines
    for (let i = 0; i <= 4; i++) {
        const y = pad + (h - pad*2) * (1 - i/4);
        const val = (maxVal * i / 4).toFixed(0);
        svg += `<line x1="${pad}" y1="${y}" x2="${w-pad}" y2="${y}"
            stroke="#f0f0f0" stroke-width="1"/>`;
        svg += `<text x="${pad-5}" y="${y+4}" text-anchor="end"
            font-size="10" fill="#86868b">$${val}</text>`;
    }
    // Line
    let points = data.map((d, i) => {
        const x = pad + i * pw;
        const y = pad + (h - pad*2) * (1 - d.total / maxVal);
        return `${x},${y}`;
    }).join(' ');
    svg += `<polyline points="${points}" fill="none" stroke="#007aff"
        stroke-width="2.5" stroke-linejoin="round"/>`;
    // Dots and labels
    data.forEach((d, i) => {
        const x = pad + i * pw;
        const y = pad + (h - pad*2) * (1 - d.total / maxVal);
        svg += `<circle cx="${x}" cy="${y}" r="4" fill="#007aff"/>`;
        svg += `<text x="${x}" y="${h+10}" text-anchor="middle"
            font-size="10" fill="#86868b">${d.month.slice(5)}</text>`;
    });
    svg += '</svg>';
    document.getElementById('trend-chart').innerHTML = svg;
}

async function loadBudgetBars() {
    const month = getCurrentMonth();
    const data = await api(`/api/budgets/status?month=${month}`);
    if (!data.length) {
        document.getElementById('budget-bars').innerHTML =
            '<p style="color:#86868b">No budgets set for this month</p>';
        return;
    }
    let html = '';
    data.forEach(b => {
        const pct = Math.min(b.percentage, 100);
        const color = pct > 90 ? '#ff3b30' : pct > 70 ? '#ff9500' : '#34c759';
        html += `<div class="budget-item">
            <div class="budget-header">
                <span>${CAT_ICONS[b.category]||''} ${b.category}</span>
                <span>$${b.spent.toFixed(2)} / $${b.budget.toFixed(2)}</span>
            </div>
            <div class="budget-bar-bg">
                <div class="budget-bar-fill" style="width:${pct}%;background:${color}"></div>
            </div>
        </div>`;
    });
    document.getElementById('budget-bars').innerHTML = html;
}

async function loadExpenses() {
    const params = new URLSearchParams();
    const from = document.getElementById('filter-from').value;
    const to = document.getElementById('filter-to').value;
    const cat = document.getElementById('filter-category').value;
    const min = document.getElementById('filter-min').value;
    const max = document.getElementById('filter-max').value;
    if (from) params.set('date_from', from);
    if (to) params.set('date_to', to);
    if (cat) params.set('category', cat);
    if (min) params.set('amount_min', min);
    if (max) params.set('amount_max', max);

    const data = await api(`/api/expenses?${params}`);
    const tbody = document.getElementById('expense-list');
    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#86868b;padding:20px">No expenses found</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(e => `<tr>
        <td>${e.date}</td>
        <td><span class="cat-badge">${CAT_ICONS[e.category]||''} ${e.category}</span></td>
        <td>${e.description}</td>
        <td><strong>$${e.amount.toFixed(2)}</strong></td>
        <td>${e.payment_method.replace('_',' ')}</td>
        <td><button class="btn-delete" onclick="deleteExpense('${e.id}')">&times;</button></td>
    </tr>`).join('');
}

async function addExpense() {
    const amount = parseFloat(document.getElementById('exp-amount').value);
    const category = document.getElementById('exp-category').value;
    const description = document.getElementById('exp-desc').value;
    const date = document.getElementById('exp-date').value;
    const payment = document.getElementById('exp-payment').value;

    if (!amount || !description) { showToast('Please fill amount and description'); return; }

    const body = { amount, category, description, payment_method: payment };
    if (date) body.date = date;

    const resp = await fetch('/api/expenses', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    });
    if (resp.ok) {
        showToast('Expense added!');
        document.getElementById('exp-amount').value = '';
        document.getElementById('exp-desc').value = '';
        refreshAll();
    } else {
        const err = await resp.json();
        showToast('Error: ' + err.error);
    }
}

async function deleteExpense(id) {
    await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
    showToast('Expense deleted');
    refreshAll();
}

function refreshAll() {
    loadSummary();
    loadPieChart();
    loadTrendChart();
    loadBudgetBars();
    loadExpenses();
}

// Init
document.getElementById('exp-date').value = new Date().toISOString().slice(0,10);
loadCategories().then(refreshAll);
</script>
</body>
</html>"""


@app.route("/")
def dashboard():
    """Serve the dashboard."""
    return render_template_string(DASHBOARD_HTML)
