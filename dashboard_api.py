# dashboard_api.py
import sqlite3
import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

DB = os.path.join(os.path.dirname(__file__), "timologia.db")
app = FastAPI(title="Printing Shop Dashboard")


def rows(query, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    res = cur.fetchall()
    conn.close()
    return res


def query_summary():
    # total sales
    r = rows("SELECT SUM(CAST(amount AS REAL)) as total FROM timologia")
    total = float(r[0]["total"] or 0.0) if r else 0.0

    # top customer
    r = rows("SELECT name, SUM(CAST(amount AS REAL)) as tot FROM timologia GROUP BY name ORDER BY tot DESC LIMIT 1")
    if r:
        top_customer = {"name": r[0]["name"], "total": float(r[0]["tot"] or 0.0)}
    else:
        top_customer = {"name": None, "total": 0.0}

    # most expensive sale
    r = rows("SELECT id, name, amount, date, description FROM timologia ORDER BY CAST(amount AS REAL) DESC LIMIT 1")
    most_expensive = dict(r[0]) if r else None

    # top customers for chart
    top = rows("SELECT name, SUM(CAST(amount AS REAL)) as tot FROM timologia GROUP BY name ORDER BY tot DESC LIMIT 8")
    top_customers = [{"name": row["name"], "total": float(row["tot"] or 0.0)} for row in top]

    return {
        "total_sales": total,
        "top_customer": top_customer,
        "most_expensive": most_expensive,
        "top_customers": top_customers,
    }


@app.get("/api/summary", response_class=JSONResponse)
def api_summary():
    return JSONResponse(content=query_summary())


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    s = query_summary()
    labels = [tc["name"] or "Unknown" for tc in s["top_customers"]]
    values = [tc["total"] for tc in s["top_customers"]]
    labels_js = json.dumps(labels)
    values_js = json.dumps(values)
    total_html = f"{s['total_sales']:.2f}"
    top_name = s["top_customer"]["name"] or "N/A"
    top_total = f"{s['top_customer']['total']:.2f}"
    most = s["most_expensive"] or {}
    most_html = "<em>None</em>"
    if most:
        desc = most.get("description") or ""
        issue = most.get("id") or ""
        most_html = f"<div><strong>Issue:</strong> {issue}</div><div><strong>Customer:</strong> {most.get('name','')}</div><div><strong>Amount:</strong> {most.get('amount','')}</div><div><strong>Date:</strong> {most.get('date','')}</div><div><strong>Description:</strong> {desc}</div>"

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Printing Shop Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body{{font-family:Arial;margin:20px}} .panel{{display:inline-block;width:30%;padding:12px;margin:6px;border:1px solid #ddd;border-radius:6px}}
  </style>
</head>
<body>
  <h1>Printing Shop Dashboard</h1>
  <div class="panel"><h3>Total sales</h3><div style="font-size:22px">€ {total_html}</div></div>
  <div class="panel"><h3>Top customer</h3><div>{top_name}</div><div>€ {top_total}</div></div>
  <div class="panel"><h3>Most expensive</h3>{most_html}</div>
  <div style="width:70%;margin-top:18px"><canvas id="bar"></canvas></div>
<script>
const labels = {labels_js};
const data = {{
  labels: labels,
  datasets: [{{
    label: 'Top customers (€)',
    data: {values_js},
    backgroundColor: 'rgba(54,162,235,0.6)'
  }}]
}};
new Chart(document.getElementById('bar').getContext('2d'), {{type:'bar', data}});
</script>
<p><small>JSON summary: <a href="/api/summary">/api/summary</a></small></p>
</body>
</html>
"""
    return HTMLResponse(content=html)


if __name__ == "__main__":
    # to run manually: python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8000
    import uvicorn
    uvicorn.run("dashboard_api:app", host="127.0.0.1", port=8000)
