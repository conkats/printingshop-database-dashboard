import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QToolBar, QAction,
    QStatusBar, QLineEdit, QPushButton, QWidget, QFormLayout, QDialog, 
    QDialogButtonBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

# SQLite database setup
db_connection = sqlite3.connect("timologia.db")
db_cursor = db_connection.cursor()

db_cursor.execute('''
CREATE TABLE IF NOT EXISTS timologia (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    amount TEXT
)
''')
db_connection.commit()

# Assuming "timologia" is a placeholder for the database structure
timologia = {}

# Define a class for a separate dialog to handle data inputs
class DataEntryDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QFormLayout()
        self.entries = {}
        for field in fields:
            entry = QLineEdit()
            self.layout.addRow(QLabel(field), entry)
            self.entries[field] = entry

        # Dialog buttons for OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.layout.addWidget(buttons)
        self.setLayout(self.layout)

    def get_data(self):
        # Return data from entries
        return {field: self.entries[field].text() for field in self.entries}


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Timologia App")

        # Set window size to 10 inches x 10 inches (converted to pixels at 96 DPI)
        inch_to_pixels = 96
        self.resize(4.5 * inch_to_pixels, 6 * inch_to_pixels)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()        
        central_widget.setLayout(self.layout)

        self.label = QLabel("Welcome to the Timologia Database App!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Table widget to display entries
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Amount"])
        self.layout.addWidget(self.table)

        # Toolbar setup
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Defining actions for each functionality (1-6)
        action1 = QAction("Add Entry", self)
        action1.triggered.connect(self.action1_handler)
        toolbar.addAction(action1)

        action2 = QAction("Edit Entry", self)
        action2.triggered.connect(self.action2_handler)
        toolbar.addAction(action2)

        action3 = QAction("Delete Entry", self)
        action3.triggered.connect(self.action3_handler)
        toolbar.addAction(action3)

        action4 = QAction("Search Entry", self)
        action4.triggered.connect(self.action4_handler)
        toolbar.addAction(action4)

        action5 = QAction("View All Entries", self)
        action5.triggered.connect(self.action5_handler)
        toolbar.addAction(action5)

        action6 = QAction("Export to CSV", self)
        action6.triggered.connect(self.action6_handler)
        toolbar.addAction(action6)

        self.setStatusBar(QStatusBar(self))
    
        self.update_table()
    # Adding fn to update the table for PyQT firmat        
    def update_table(self):
        # Update the table widget with current data
         # Update the table widget with current data from the database
        db_cursor.execute("SELECT * FROM timologia")
        rows = db_cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
 
    def action1_handler(self):
        # Add a new entry to the "timologia" database
        fields = ["ID", "Name", "Description", "Amount"]
        dialog = DataEntryDialog("Add Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                db_cursor.execute(
                    "INSERT INTO timologia (id, name, description, amount) VALUES (?, ?, ?, ?)",
                    (data["ID"], data["Name"], data["Description"], data["Amount"])
                )
                db_connection.commit()
                self.label.setText(f"Added entry: {data}")
                self.update_table()
            except sqlite3.IntegrityError:
                self.label.setText("Error: ID already exists.")

    def action2_handler(self):
         # Edit an existing entry by ID
        fields = ["ID (to edit)", "Name", "Description", "Amount"]
        dialog = DataEntryDialog("Edit Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data.pop("ID (to edit)")
            db_cursor.execute("SELECT * FROM timologia WHERE id = ?", (entry_id,))
            if db_cursor.fetchone():
                db_cursor.execute(
                    "UPDATE timologia SET name = ?, description = ?, amount = ? WHERE id = ?",
                    (data["Name"], data["Description"], data["Amount"], entry_id)
                )
                db_connection.commit()
                self.label.setText(f"Edited entry with ID: {entry_id}")
                self.update_table()
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action3_handler(self):
        # Delete an entry by ID
        fields = ["ID"]
        dialog = DataEntryDialog("Delete Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data["ID"]
            db_cursor.execute("SELECT * FROM timologia WHERE id = ?", (entry_id,))
            if db_cursor.fetchone():
                db_cursor.execute("DELETE FROM timologia WHERE id = ?", (entry_id,))
                db_connection.commit()
                self.label.setText(f"Deleted entry with ID: {entry_id}")
                self.update_table()
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action4_handler(self):
        # Search for an entry by Name and display it in the table
        fields = ["Name"]
        dialog = DataEntryDialog("Search Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            name = data["Name"]
            db_cursor.execute("SELECT * FROM timologia WHERE name LIKE ?", (f"%{name}%",))
            rows = db_cursor.fetchall()
            if rows:
                self.table.setRowCount(len(rows))
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                self.label.setText(f"Found {len(rows)} entries matching name '{name}'")
            else:
                self.label.setText(f"No entries found for name '{name}'")


    def action5_handler(self):
        # View all entries in the database
        #entries = "\n".join([f"ID: {k}, Data: {v}" for k, v in timologia.items()])
        #self.label.setText(f"All Entries:\n{entries}" if entries else "No entries found.")
        self.update_table()
        self.label.setText("Displaying all entries")

    
    def action6_handler(self):
        # Export database to CSV
        db_cursor.execute("SELECT * FROM timologia")
        rows = db_cursor.fetchall()
        if rows:
            with open("timologia_export.csv", "w") as file:
                file.write("ID,Name,Description,Amount\n")
                for row in rows:
                    file.write(",".join(row) + "\n")
            self.label.setText("Exported database to 'timologia_export.csv'")
        else:
            self.label.setText("No entries to export.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
