import sqlite3
import csv
import keras_ocr #for opencv
import re # for regex
import os

usage_message = '''
# Καλοσωρήσατε στο σύστημα τιμολογίων! 
# Τι θα θέλατε να κάνετε? (Επιλέξτε από το 1-7, 0)
# Για όλες τις επιλογές εισάγετε '' στα Linux.
 1 - Τοποθέτηση αριθμού τιμολογίου.
 2 - Ανανέωση αριθμού τιμολογίου.
 3 - Διαγραφή αριθμού τιμολογίου.
 4 - Αναζήτηση τιμολογίου.
 5 - Θέαση λίστας τιμολογίων.
 6 - Αποθήκευση λίστας τιμολογίων σε csv.
 7 - Εισαγωγή τιμολογίου από εικόνα.
 0 - Έξοδος προγράμματος.
'''


def create_database():
    db = sqlite3.connect("timologia")
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timologia (
            ID INTEGER PRIMARY KEY,
            TITLE varchar(100),
            Author varchar(100),
            Qty int
        )
    ''')
    db.commit()
    return db


# Add timologia in the db
def add_book(cursor):
    id = int(input('Τοποθετείστε αριθμό τιμολογίου:\n'))
    title = input('Τοποθετείστε προιόν και λεπτομέρειες:\n')
    author = input('Τοποθετείστε όνομα πελάτη:\n')
    qty = int(input('Τοποθετείστε ποσό τιμολογίου (ευρώ):\n'))
    cursor.execute('''INSERT INTO timologia(id, title, author, qty)
                   VALUES(?,?,?,?)''', (id, title, author, qty))


# Update the existing timologia in the db
def update_book(cursor):
    id = int(input('Τοποθετείστε αριθμό τιμολογίου για ανανέωση αριθμού:\n'))
    title = input('Τοποθετείστε νέο προιόν και λεπτομέρειες:\n')
    author = input('Τοποθετείστε νέο όνομα πελάτη:\n')
    qty = int(input('Τοποθετείστε νέο ποσό τιμολογίου (ευρώ):\n'))
    cursor.execute('''UPDATE timologia SET Title = ?, Author = ?, Qty = ? 
                   WHERE ID = ?''', (title, author, qty, id))


# Remove any timologia
def delete_book(cursor):
    id = int(input('Τοποθετείστε αριθμό τιμολογίου για διαγραφή:\n'))
    cursor.execute('''DELETE FROM timologia
                    WHERE ID = ?''', (id,))


# Retrieve data from sql db
def search_book(cursor):
    search_term = input("Αναζήτηση: ")
    cursor.execute('''SELECT * FROM timologia 
                   WHERE 
                   Title LIKE ? 
                   OR Author LIKE ?
                   OR ID LIKE ?''',
                   ('%' + search_term + '%',
                    '%' + search_term + '%',
                    '%' + search_term + '%'))
    rows = cursor.fetchall()
    for row in rows:
        print(row)


# View timologia entries in the db
def view_bookdb(cursor):
    cursor.execute('SELECT * FROM timologia')
    rows = cursor.fetchall()
    print("Δεδομένα:")
    for row in rows:
        print(row)


# Save the entries of the db to .csv
def savedb_csv(cursor, db):
    cursor.execute('''SELECT * FROM timologia''')
    rows = cursor.fetchall()

    with open('timologia.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Αρ. Τιμ.', 'Περιγραφή', 'Πελάτης', 'Euro'])
        writer.writerows(rows)
    print("Η λίστα τιμολογίων έχει αποθηκευτεί στο τιμολόγια.csv")


# Extract text from image using keras-ocr
def extract_text_from_image(image_path):
    image_path='scan.png'
    pipeline = keras_ocr.pipeline.Pipeline()
    image = keras_ocr.tools.read(image_path)
    predictions = pipeline.recognize([image])[0]
    extracted_text = " ".join([text for text, _ in predictions])
    return extracted_text


# Parse the extracted text into timologia fields
def parse_timologia_data(extracted_text):
    id_match = re.search(r"INVOICE[:\s]*(\d+)", extracted_text, re.IGNORECASE)
    title_match = re.search(r"ΟΝΟΜΑ[:\s]*(.+?)(?:Πελάτης|Qty|€|$)", extracted_text, re.IGNORECASE)
    author_match = re.search(r"ΠΕΡΙΓΡΑΦΗ[:\s]*(.+?)(?:Qty|€|$)", extracted_text, re.IGNORECASE)
    qty_match = re.search(r"€[:\s]*(\d+)", extracted_text, re.IGNORECASE)

    timologia_data = {
        "ID": int(id_match.group(1)) if id_match else None,
        "TITLE": title_match.group(1).strip() if title_match else "Άγνωστο",
        "Author": author_match.group(1).strip() if author_match else "Άγνωστος",
        "Qty": int(qty_match.group(1)) if qty_match else 0,
    }
    return timologia_data


# Add extracted timologia data to the database
def add_timologia_from_image(cursor, image_path):
    extracted_text = extract_text_from_image(image_path)
    print("Αναγνωρισμένο Κείμενο:", extracted_text)
    timologia_data = parse_timologia_data(extracted_text)
    print("Parsed Data:", timologia_data)

    cursor.execute('''INSERT INTO timologia (ID, TITLE, Author, Qty)
                   VALUES (?, ?, ?, ?)''',
                   (timologia_data["ID"], timologia_data["TITLE"], timologia_data["Author"], timologia_data["Qty"]))


# Main program
def main():
    db = create_database()
    cursor = db.cursor()

    while True:
        user_choice = int(input(usage_message))
        if user_choice == 1:
            add_book(cursor)
            db.commit()
        elif user_choice == 2:
            update_book(cursor)
            db.commit()
        elif user_choice == 3:
            delete_book(cursor)
            db.commit()
        elif user_choice == 4:
            search_book(cursor)
        elif user_choice == 5:
            view_bookdb(cursor)
        elif user_choice == 6:
            savedb_csv(cursor, db)
        elif user_choice == 7:
            image_path = input("Εισάγετε το μονοπάτι της εικόνας:\n")
            add_timologia_from_image(cursor, image_path)
            db.commit()
        elif user_choice == 0:
            print("Εξοδος!")
            db.close()
            break
        else:
            print("Μη αναγνωρίσημη επιλογή. Παρακαλώ δοκιμάστε ξανά.")


if __name__ == "__main__":
    main()
