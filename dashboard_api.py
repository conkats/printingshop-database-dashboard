# dashboard_api.py
import sqlite3
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "timologia.db")
# If your DB is named differently, change the path above.

app = FastAPI(title="Printing Shop Dashboard API")


def get_db_connection(db_path: str = DB_PATH):
    # use check_same_thread=False for uvicorn single process, but we open/close per request so it's fine
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def safe_cast_amount(val):
    """Return float amount for different stored formats; fallback to 0.0"""
    try:
        return float(val)
    except Exception:
        try:
            # Try strip non numeric characters
            s = str(val).replace(",", ".")
            # remove currency symbols and spaces
            s = "".join(ch for ch in s if (ch.isdigit() or ch in ".-"))
            return float(s) if s else 0.0
        except Exception:
            return 0.0


def query_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor()

    # Total sales (sum of amounts) — cast amount to real
    try:
        cur.execute("SELECT SUM(CAST(amount AS REAL)) as total_sales FROM invoices")
        row = cur.fetchone()
        total_sales = row["total_sales"] if row and row["total_sales"] is not None else 0.0
    except sqlite3.OperationalError:
        # table invoices may not exist; try timologia as fallback
        cur.execute("SELECT SUM(CAST(amount AS REAL)) as total_sales FROM timologia")
        row = cur.fetchone()
        total_sales = row[0] if row and row[0] is not None else 0.0

    # Customer with highest sales
    # For invoices table
    try:
        cur.execute("""
            SELECT name, SUM(CAST(amount AS REAL)) AS total_by_customer
            FROM invoices
            GROUP BY name
            ORDER BY total_by_customer DESC
            LIMIT 1
        """)
        r = cur.fetchone()
        if r:
            top_customer = {"name": r["name"], "total": float(r["total_by_customer"] or 0.0)}
        else:
            top_customer = {"name": None, "total": 0.0}
    except sqlite3.OperationalError:
        # fallback to timologia
        cur.execute("""
            SELECT name, SUM(CAST(amount AS REAL)) AS total_by_customer
            FROM timologia
            GROUP BY name
            ORDER BY total_by_customer DESC
            LIMIT 1
        """)
        r = cur.fetchone()
        top_customer = {"name": r[0], "total": float(r[1] or 0.0)} if r else {"name": None, "total": 0.0}

    # Most expensive sale (single row)
    try:
        cur.execute("""
            SELECT * FROM invoices
            WHERE CAST(amount AS REAL) = (SELECT MAX(CAST(amount AS REAL)) FROM invoices)
            LIMIT 1
        """)
        r = cur.fetchone()
        if r:
            most_expensive = dict(r)
        else:
            most_expensive = None
    except sqlite3.OperationalError:
        # fallback timologia
        cur.execute("""
            SELECT * FROM timologia
            WHERE CAST(amount AS REAL) = (SELECT MAX(CAST(amount AS REAL)) FROM timologia)
            LIMIT 1
        """)
        r = cur.fetchone()
        most_expensive = dict(r) if r else None

    # Top N customers for chart
    try:
        cur.execute("""
            SELECT name, SUM(CAST(amount AS REAL)) AS total_by_customer
            FROM invoices
            GROUP BY name
            ORDER BY total_by_customer DESC
            LIMIT 8
        """)
        rows = cur.fetchall()
        top_customers = [{"name": r["name"], "total": float(r["total_by_customer"] or 0.0)} for r in rows]
    except sqlite3.OperationalError:
        cur.execute("""
            SELECT name, SUM(CAST(amount AS REAL)) AS total_by_customer
            FROM timologia
            GROUP BY name
            ORDER BY total_by_customer DESC
            LIMIT 8
        """)
        rows = cur.fetchall()
        top_customers = [{"name": r[0], "total": float(r[1] or 0.0)} for r in rows]

    conn.close()

    return {
        "total_sales": float(total_sales or 0.0),
        "top_customer": top_customer,
        "most_expensive": most_expensive,
        "top_customers": top_customers,
    }


@app.get("/api/summary", response_class=JSONResponse)
def api_summary():
    """Return JSON summary: total_sales, top_customer, most_expensive, top_customers list."""
    summary = query_summary()
    return JSONResponse(content=summary)


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Render a simple HTML dashboard (Chart.js used for a small bar chart)."""
    summary = query_summary()

    total_sales = f"{summary['total_sales']:.2f}"
    top_customer = summary["top_customer"]
    most_exp = summary["most_expensive"]
    top_customers = summary["top_customers"]

    # Prepare data for Chart.js
    labels = [tc["name"] or "Unknown" for tc in top_customers]
    values = [tc["total"] for tc in top_customers]

    labels_json = json.dumps(labels)
    values_json = json.dumps(values)

    most_exp_html = "<em>None found</em>"
    if most_exp:
        # description may be long JSON or newline; show safely
        desc = most_exp.get("description") or most_exp.get("Description") or ""
        # show truncated desc
        desc_text = str(desc)
        if len(desc_text) > 200:
            desc_text = desc_text[:200] + "..."
        issue = most_exp.get("issue_number") or most_exp.get("id") or most_exp.get("Issue number") or ""
        name = most_exp.get("name") or most_exp.get("Name") or ""
        amount = most_exp.get("amount") or most_exp.get("Amount") or ""
        date = most_exp.get("date") or most_exp.get("Date") or ""
        most_exp_html = f"""
            <div><strong>Issue:</strong> {issue}</div>
            <div><strong>Customer:</strong> {name}</div>
            <div><strong>Amount:</strong> {amount}</div>
            <div><strong>Date:</strong> {date}</div>
            <div><strong>Description:</strong> {desc_text}</div>
        """

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>Printing Shop Dashboard</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; }}
          .panel {{ display:inline-block; vertical-align:top; width:30%; padding:12px; margin:8px; box-shadow:0 1px 3px rgba(0,0,0,0.12); }}
          .panel h2 {{ margin:8px 0; }}
          .chart-container {{ width: 60%; margin-top: 16px; }}
          .small {{ font-size:0.9em; color:#666; }}
          table {{ border-collapse: collapse; width: 100%; margin-top:12px; }}
          table td, table th {{ border: 1px solid #ddd; padding: 8px; }}
          table th {{ background:#f8f8f8; }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      </head>
      <body>
        <h1>Printing Shop Dashboard</h1>
        <div class="panels">
          <div class="panel">
            <h2>Total sales</h2>
            <div style="font-size:28px;">€ {total_sales}</div>
            <div class="small">Sum of all recorded invoice amounts</div>
          </div>

          <div class="panel">
            <h2>Top Customer</h2>
            <div style="font-size:18px;">{top_customer.get('name') if top_customer else 'N/A'}</div>
            <div style="font-size:20px;">€ {top_customer.get('total') if top_customer else '0.00'}</div>
            <div class="small">Customer with highest cumulative sales</div>
          </div>

          <div class="panel">
            <h2>Most expensive sale</h2>
            {most_exp_html}
          </div>
        </div>

        <div style="clear:both;"></div>

        <div class="chart-container">
          <canvas id="topCustomersChart"></canvas>
        </div>

        <script>
          const labels = {labels_json};
          const data = {{
            labels: labels,
            datasets: [{{
              label: 'Top customers (total €)',
              data: {values_json},
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }}]
          }};

          const config = {{
            type: 'bar',
            data: data,
            options: {{
              scales: {{
                y: {{
                  beginAtZero: true
                }}
              }}
            }}
          }};

          const ctx = document.getElementById('topCustomersChart').getContext('2d');
          new Chart(ctx, config);
        </script>

        <p class="small">Raw JSON summary available at <a href="/api/summary">/api/summary</a></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dashboard_api:app", host="127.0.0.1", port=8000, reload=True)

