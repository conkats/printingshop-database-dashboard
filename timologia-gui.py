import sys
import sqlite3
from datetime import datetime
import json  

from  PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QToolBar, QAction,
    QStatusBar, QLineEdit, QPushButton, QWidget, QFormLayout, QDialog, 
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHBoxLayout, QInputDialog
)
from PyQt5.QtCore import Qt

# SQLite database setup
db_connection = sqlite3.connect("timologia.db")
db_cursor = db_connection.cursor()

# Check if the 'timologia' table needs to be migrated
def ensure_table_schema():
    db_cursor.execute("PRAGMA table_info(timologia)")
    columns = [column[1] for column in db_cursor.fetchall()]
    if "date" not in columns:
        # If the 'date' column doesn't exist, migrate the table
        db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS timologia_new (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            amount TEXT,
            date TEXT
        )
        ''')
        # Copy data from the old table to the new table
        db_cursor.execute('''
        INSERT INTO timologia_new (id, name, description, amount)
        SELECT id, name, description, amount FROM timologia
        ''')
        # Drop the old table and rename the new table
        db_cursor.execute("DROP TABLE timologia")
        db_cursor.execute("ALTER TABLE timologia_new RENAME TO timologia")
        db_connection.commit()

# Ensure the table schema is correct
ensure_table_schema()

# Assuming "timologia" is a placeholder for the database structure
timologia = {}

# Define a class for a separate dialog to handle data inputs
class DataEntryDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QFormLayout()
        self.entries = {}
        self.date_field = None  # To keep track of the date field for validation
        self.descriptions = []  # Store user-enterd descriptions in a list
        
        # Add fields to the layout
        for field in fields:
            entry = QLineEdit()
            if field == "Date":
                entry.setPlaceholderText("DD-MM-YY") # Add placeholder for date
                self.date_field = entry
            self.layout.addRow(QLabel(field), entry)
            self.entries[field] = entry
            
        # Add a button to add descriptions
        self.description_button = QPushButton("Add Description")
        self.description_button.clicked.connect(self.add_description)
        self.layout.addWidget(self.description_button)

        # Layout to display added descriptions
        self.descriptions_layout = QVBoxLayout()
        self.layout.addRow(self.descriptions_layout)

        # Dialog buttons for OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        self.layout.addWidget(buttons)
        self.setLayout(self.layout)
        
    # The add_description method appends descriptions to the self.descriptions list, 
    # so to be added to the data dictionary when the dialog is accepted.
    # After adding a description, the update_description_list() method updates the UI to display all added descriptions in the dialog.
    def add_description(self):
        description, ok = QInputDialog.getText(self, "Add Description", "Enter description:")
        if ok and description:
            self.descriptions.append(description)
            self.update_description_list()
    
    def update_description_list(self):
        # Clear previous descriptions in the layout
        for i in reversed(range(self.descriptions_layout.count())):
            widget = self.descriptions_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add the descriptions to the layout
        for description in self.descriptions:
            label = QLabel(description)
            self.descriptions_layout.addWidget(label)
    
    def validate_and_accept(self):
        # Validate the date format if the Date field exists
        if self.date_field:
            date_text = self.date_field.text()
            try:
                # Validate the date format
                datetime.strptime(date_text, "%d-%m-%y")
            except ValueError:
                QMessageBox.warning(self, "Invalid Date", "Παραχώρησε την ημερομηνία με το σωστό τύπο π.χ. DD-MM-YY.")
                return  # Do not close the dialog if the date is invalid
        self.accept()

    def get_data(self):
        # The method returns data dictionary from entries of db 
        # and add descriptions
        data = {field: self.entries[field].text() for field in self.entries}
        data["Descriptions"] = self.descriptions  # Add Descriptions as a key to the returned data dict.
        print(f"Descriptions in get_data: {data['Descriptions']}")  # Log the descriptions here
        return data
    

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Timologia App")

        # Set window size to 10 inches x 10 inches (converted to pixels at 96 DPI)
        inch_to_pixels = 96
        self.resize(4 * inch_to_pixels, 6 * inch_to_pixels)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()        
        central_widget.setLayout(self.layout)

        self.label = QLabel("Καλοσωρίσατε στη Βάση Δεδομένων Τιμολογίου!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Table widget to display entries
        # of 5 columns: ID, Name, Description, Amount, Date
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Αριθμός Τιμολογίου", "Ονοματεπώνυμο", "Περιγραφή", "Ποσό", "Ημερομηνία"])
        self.layout.addWidget(self.table)

        # Toolbar setup
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Defining actions for each functionality (1-6)
        action1 = QAction("Πρόσθεση Τιμολογίου", self)
        action1.triggered.connect(self.action1_handler)
        toolbar.addAction(action1)

        action2 = QAction("Επεξεργασία Τιμολογίου", self)
        action2.triggered.connect(self.action2_handler)
        toolbar.addAction(action2)

        action3 = QAction("Διαγραφή Τιμολογίου", self)
        action3.triggered.connect(self.action3_handler)
        toolbar.addAction(action3)

        action4 = QAction("Αναζήτηση Τιμολογίου", self)
        action4.triggered.connect(self.action4_handler)
        toolbar.addAction(action4)

        action5 = QAction("Θέαση όλων Τιμολογίων", self)
        action5.triggered.connect(self.action5_handler)
        toolbar.addAction(action5)

        action6 = QAction("Αποθήκευση σε CSV ", self)
        action6.triggered.connect(self.action6_handler)
        toolbar.addAction(action6)

        self.setStatusBar(QStatusBar(self))
        
        # Call the update_table method to display the initial data in the table
        self.update_table()
        
    # Adding fn to update the table for PyQT format        
    def update_table(self):
        # Update the table widget with current data
         # Update the table widget with current data from the database
         # handles the deserialized JSON data and sisplays it in the table
        db_cursor.execute("SELECT * FROM timologia")
        #fetch the descriptions, deserialize them, 
        # convert them to string and display them in the table
        rows = db_cursor.fetchall()
        
        # Set row count based on fetched rows
        self.table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            # Deserialize JSON descriptions (column 3 is "description")
            for col_idx, value in enumerate(row):
                # Check for the Decsription column (index 2 in this case)    
                if col_idx == 2:  # "Description" column
                    #print(f"Raw description value: {value}")  # Log the raw value
                    try:
                       # If the description is stored as a JSON string, deserialize it
                       # decode the JSON string stored in the descrition column into a list
                       descriptions = json.loads(value) if value else []
                       print(f"Deserialized descriptions: {descriptions}")  # Log the deserialized value
                       
                        # Ensure descriptions is a list before trying to join to avoid
                        # TypeError: sequence item 0: expected str instance, NoneType found
                       if not isinstance(descriptions, list):
                          descriptions = []
                       
                       # Join the descriptions into a string with line breaks or commas (adjust as needed)
                       descriptions_str = "\n".join(descriptions) #if descriptions else "No descriptions" # You can change "\n" to ", " if needed
                       
                       # Create the QTableWidgetItem and set word wrapping
                       # so that the descriptions are displayed in multiple lines
                       item = QTableWidgetItem(descriptions_str)
                       item.setTextAlignment(Qt.AlignTop)  # Align text to the top of the cell
                       item.setToolTip(descriptions_str)  # Optionally add a tooltip for full description
                       # In case the description column is not valid JSON, just show the raw value
                       self.table.setItem(row_idx, col_idx, item)
                       #self.table.setItem(row_idx, col_idx, QTableWidgetItem(descriptions_str))
                       # Adjust the row height to fit the descriptions
                       self.table.resizeRowToContents(row_idx)
                    
                    except json.JSONDecodeError:
                        # In case the description column is not valid JSON, just show the raw value
                       self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                else:
                   # For other columns, just display the value
                   self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def action1_handler(self):
        # Add a new entry to the "timologia" database
        fields = ["ID", "Name", "Amount", "Date"]
        dialog = DataEntryDialog("Πρόσθεση Τιμολογίου", fields, self)
        
        if dialog.exec():
            data = dialog.get_data()


            # Try autocompleting based on Name
            existing_entry = self.autocomplete_name(data["Name"])
            if existing_entry:
               # Ask the user if they want to autocomplete
               reply = QMessageBox.question(self, "Εύρεση Υπάρχοντος Ονόματος",
                                          f"Βρέθηκε ήδη πελάτης με το όνομα '{data['Name']}'. Θέλεις να συμπληρωθούν αυτόματα τα στοιχεία;",
                                          QMessageBox.Yes | QMessageBox.No)
               if reply == QMessageBox.Yes:
                   # Update the data with the autocompleted fields
                   data.update({
                       "Amount": existing_entry["Amount"],
                       "Date": existing_entry["Date"]
                   })
                   data["Descriptions"] = existing_entry["Descriptions"]
  

            try:
                # Convert the list of descriptions to JSON string format
                # Check if descriptions in the key exist, retrieve them
                # and then to be serialized to JSON before inserted in the db - data dict.
                descriptions = data.get("Descriptions", [])
                #print(f"Descriptions before saving: {descriptions}")  # Log the descriptions
                # Check if descriptions is a list and exists before trying to convert to JSON
                if descriptions:# If descriptions exist, convert them to JSON string
                    descriptions_json = json.dumps(descriptions)
                else:
                    descriptions_json = "[]" # If no descriptions, use an empty JSON array
                # check the descriptions are not empty []
                # otherwise problem of updating-deserialising the JSOn
                # print(descriptions,descriptions_json)
                
                # Insert into the database
                db_cursor.execute(
                    "INSERT INTO timologia (id, name, description, amount, date) VALUES (?, ?, ?, ?, ?)",
                    (data["ID"], data["Name"], descriptions_json, data["Amount"], data["Date"])
                )
                db_connection.commit()
                self.label.setText(f"Added entry: {data}")
                self.update_table()
            except sqlite3.IntegrityError:
                self.label.setText("Error: ID already exists.")

    def action2_handler(self):
         # Edit an existing entry by ID
        fields = ["ID (to edit)", "Name", "Amount", "Date"]
        dialog = DataEntryDialog("Επεξεργασία Τιμολογίου", fields, self)
        if dialog.exec():
            data = dialog.get_data()
            entry_id = data.pop("ID (to edit)")
            db_cursor.execute("SELECT * FROM timologia WHERE id = ?", (entry_id,))
            if db_cursor.fetchone():
                descriptions_json = json.dumps(data.get("Descriptions", []))  # Use the "Descriptions" key
                db_cursor.execute(
                     "UPDATE timologia SET name = ?, description = ?, amount = ?, date = ? WHERE id = ?",
                     (data["Name"], descriptions_json, data["Amount"], data["Date"], entry_id)
                )
                db_connection.commit()
                self.label.setText(f"Edited entry with ID: {entry_id}")
                self.update_table()
            else:
                self.label.setText(f"Entry ID {entry_id} not found.")

    def action3_handler(self):
        # Delete an entry by ID
        fields = ["ID"]
        dialog = DataEntryDialog("Διαγραφή Τιμολογίου", fields, self)
        
        # Remove the description button from the dialog 
        # since we don't need it in delete action
        dialog.description_button.setVisible(False)
    
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
        dialog = DataEntryDialog("Αναζήτηση Τιμολογίου", fields, self)
        
        # Remove the description button from the dialog since we don't need it in delete action
        dialog.description_button.setVisible(False)
        if dialog.exec():
            data = dialog.get_data()
            name = data["Name"]
            db_cursor.execute("SELECT * FROM timologia WHERE name LIKE ?", (f"%{name}%",))
            rows = db_cursor.fetchall()
            if rows:
                self.table.setRowCount(len(rows))
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        #self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                        if col_idx == 2:  # "Description" column
                            try:
                                # If the description is stored as a JSON string, deserialize it
                                descriptions = json.loads(value) if value else []
                                
                                # Ensure descriptions is a list before trying to join
                                if not isinstance(descriptions, list):
                                    descriptions = []
                                
                                # Join the descriptions into a string with line breaks
                                descriptions_str = "\n".join(descriptions)  # Each description on a new line
                                
                                # Create the QTableWidgetItem and set word wrapping
                                item = QTableWidgetItem(descriptions_str)
                                item.setTextAlignment(Qt.AlignTop)  # Align text to the top of the cell
                                item.setToolTip(descriptions_str)  # Optionally add a tooltip for full description
                                self.table.setItem(row_idx, col_idx, item)
                                
                                # Adjust the row height to fit the descriptions
                                self.table.resizeRowToContents(row_idx)
                                
                            except json.JSONDecodeError:
                                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                        else:
                            # For other columns, just display the value
                            self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))                
                
                self.label.setText(f"Found {len(rows)} entries matching name '{name}'")    
            else:
                self.label.setText(f"No entries found for name '{name}'")


    def action5_handler(self):
        # Θέαση όλων Τιμολογίων in the database
        # the fucntion only updates the table and shows descriptions as multi-line
        # test.
        
        #entries = "\n".join([f"ID: {k}, Data: {v}" for k, v in timologia.items()])
        #self.label.setText(f"All Entries:\n{entries}" if entries else "No entries found.")
        self.update_table()
        self.label.setText("Θέαση όλων Τιμολογίων!")

    
    def action6_handler(self):
        # Export database to CSV
        db_cursor.execute("SELECT * FROM timologia")
        rows = db_cursor.fetchall()
        if rows:
            with open("timologia_export.csv", "w", encoding="utf-8") as file:
                file.write("ID,Name,Description,Amount\n")
                for row in rows:
                    # Replace None values with empty strings to prevent TypeError
                    row = [str(item) if item is not None else "" for item in row]
                    file.write(",".join(row) + "\n")
            self.label.setText("Exported database to 'timologia_export.csv'")
        else:
            self.label.setText("No entries to export.")
    
    # Method to handle autocomplete functionality
    def autocomplete_name(self, name):
        db_cursor.execute("SELECT name, description, amount, date FROM timologia WHERE name = ?", (name,))
        result = db_cursor.fetchone()
        if result:
            # Return the matching entry details
            name, description_json, amount, date = result
            try:
                descriptions = json.loads(description_json) if description_json else []
            except json.JSONDecodeError:
                descriptions = []
            return {
                "Name": name,
                "Descriptions": descriptions,
                "Amount": amount,
                "Date": date
            }
        return None  # No matching name found

# Close the database connection when the application exits
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
