# timologia_db
Timologia App - Database for Printing shop

A PyQt5-based desktop application for managing invoices (timologia) with SQLite (in Greek).
Includes features to add, edit, delete, search, export invoices, and a FastAPI-powered dashboard.

### Features included

1. Add Invoice – Add new invoice entries with multiple descriptions. Dates timologiou as column/multiple descriptions- nested. Autocomplete names and description.

2. Edit Invoice – Edit existing invoices by ID.

3. Delete Invoice – Delete invoices by ID.

4. Search Invoice – Search invoices by customer name.

5. View All – Display all invoices in a table with multi-line descriptions.

6. Export CSV – Export all invoices to timologia_export.csv. Saved .db.

7. Import CSV – Replace current database with a CSV file.

8. Dashboard – Start a FastAPI dashboard in html that shows: Total sales, Top customer, Most expensive sale, Bar chart of top 8 customers

Link to JSON summary

### CSV Import/Export

- Export: Click "Αποθήκευση σε .csv" to export timologia table to timologia_export.csv.

- Import: Click "Ανέβασε το .csv" to select a CSV file. This replaces the current database. CSV format:

`ID,Name,Description,Amount,Date`

- Descriptions are expected as JSON arrays or plain text (will be converted internally).

#### Dashboard

- Start from GUI: Click Start Dashboard (action 8).
- Opens your default browser to http://127.0.0.1:8000/dashboard.
- Auto-starts the FastAPI server if not running.
- JSON summary available at http://127.0.0.1:8000/api/summary.

### Manual start:

`python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8000`

- After starting, open http://127.0.0.1:8000/dashboard in a browser.

### Database

- SQLite database file: timologia.db (created automatically if not present).
- Table schema:


| Column      | Type              |
| ----------- | ----------------- |
| id          | TEXT PRIMARY KEY  |
| name        | TEXT              |
| description | TEXT (JSON array) |
| amount      | TEXT              |
| date        | TEXT (DD-MM-YY)   |

#### Notes

- Amounts are stored as text but converted to float for calculations.

- Descriptions are stored as JSON arrays for flexibility.

- The dashboard auto-generates charts using Chart.js.

#### License
MIT License – free to use, modify, and distribute.

Install libraries in the python envinroment using:
<pre><code>
conda install -r requirements.txt
</code></pre>

### Requirements
- Python 3.10+
- PyQt5
- FastAPI
- Uvicorn

Install dependencies via pip3:

`pip3 install pyqt5 fastapi uvicorn`

Running the App manually
`python main.py`

- Opens a PyQt5 GUI window.
- Toolbar buttons correspond to the features listed above.

Caution on Pyqt5 lib depends on OS-Mac/Windows/Linux

Packaged the programme into a single .exe for windows, use anaconda .env or python .env in cmd and execute:

`pyinstaller --onefile --windowed timologia-gui.py`

PyInstaller auto-generate a spec file, bundle verything in one single .exe 
and include additional files e.g. DB, CSV:

`pyinstaller --name TimologiaApp --onefile --windowed main.py --add-data "timologia.db;."`

Note that ;. separates source and destination on Windows

Include dashboard_api.py in the PyInstaller bundle:

`pyinstaller --onefile --windowed main.py --add-data "dashboard_api.py;."`

`pyinstaller --name TimologiaApp --onefile --windowed main.py --add-data "dashboard_api.py;." --add-data "timologia.db;."`

When build,
dist/
└── TimologiaApp.exe

- Run TimologiaApp.exe → GUI starts

- Click Start Dashboard → FastAPI dashboard runs at http://127.0.0.1:8000/dashboard

Remember that the timologia.db should be present in the directory.
