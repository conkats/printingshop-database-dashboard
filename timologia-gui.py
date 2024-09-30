import sys
from pyqt5.qtwidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QToolBar, QAction,
    QStatusBar, QLineEdit, QPushButton, QWidget, QFormLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt

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

        self.setWindowTitle("Timologia Database App")

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        self.label = QLabel("Welcome to the Timologia Database App!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

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

    def action1_handler(self):
        # Add a new entry to the "timologia" database
        fields = ["ID", "Name", "Description", "Amount"]
        dialog = DataEntryDialog("Add Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            # Simulating database insert
            timologia[data["ID"]] = data
            self.label.setText(f"Added entry: {data}")

    def action2_handler(self):
        # Edit an existing entry by ID
        fields = ["ID (to edit)", "Name", "Description", "Amount"]
        dialog = DataEntryDialog("Edit Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data.pop("ID (to edit)")
            if entry_id in timologia:
                timologia[entry_id].update(data)
                self.label.setText(f"Edited entry with ID: {entry_id}")
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action3_handler(self):
        # Delete an entry by ID
        fields = ["ID"]
        dialog = DataEntryDialog("Delete Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data["ID"]
            if entry_id in timologia:
                del timologia[entry_id]
                self.label.setText(f"Deleted entry with ID: {entry_id}")
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action4_handler(self):
        # Search for an entry by ID and display it
        fields = ["ID"]
        dialog = DataEntryDialog("Search Entry", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data["ID"]
            if entry_id in timologia:
                entry = timologia[entry_id]
                self.label.setText(f"Found entry: {entry}")
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action5_handler(self):
        # View all entries in the database
        entries = "\n".join([f"ID: {k}, Data: {v}" for k, v in timologia.items()])
        self.label.setText(f"All Entries:\n{entries}" if entries else "No entries found.")

    def action6_handler(self):
        # Export database to CSV (simulation)
        if timologia:
            with open("timologia_export.csv", "w") as file:
                file.write("ID,Name,Description,Amount\n")
                for entry in timologia.values():
                    file.write(f"{entry['ID']},{entry['Name']},{entry['Description']},{entry['Amount']}\n")
            self.label.setText("Exported database to 'timologia_export.csv'")
        else:
            self.label.setText("No entries to export.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
