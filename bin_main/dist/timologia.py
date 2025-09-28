# A program that can be used by a printing shop clerk.
# Run with 
# python3 timologia.py
# Pre-requisites-miniconda, python3, csv and sqlite3, pyqt5 libs
# 
import sqlite3
import csv 


usage_message = '''
# Καλοσωρήσατε στο σύστημα τιμολογίων! 
# Τι θα θέλατε να κάνετε? (Επιλέξτε από το 1-6, 0)
# Για όλες τις επιλογές εισάγετε '' στα Linux.
 1 - Τοποθέτηση αριθμού τιμολογίου.
 2 - Ανανέωση αριθμού τιμολογίου.
 3 - Διαγραφή αριθμού τιμολογίου.
 4 - Αναζήτηση τιμολογίου.
 5 - Θέαση λίστας τιμολογίων.
 6 - Αποθήκευση λίστας τιμολογίων σε csv. 
 0 - Έξοδος προγράμματος.
'''


def create_database():
    #try:
    # Creates or opens a file called timolgia 
    # with a SQLite3 DB
    db = sqlite3.connect('timologia')
    
    # Get a cursor object
    cursor = db.cursor()

    #Remove every trace of the table during testing
    #cursor.execute('''
    #               DROP TABLE IF EXISTS timologia
    #               ''')
    

    #rows = cursor.fetchall()
    #print("Initial data before adding any:")
    #for row in rows:
    #    print(row)
    

     # Check if table users does not exist and create it
    cursor.execute('''CREATE TABLE IF NOT EXISTS timologia (
      ID INTEGER PRIMARY KEY,
      TITLE varchar(100),
      Author varchar(100),
      Qty int
      )''')
    # Commit the change
    db.commit()
        
    #cursor = db.cursor()

    #timologia_= [(
    #     3001, 'A Tale of Two Cities', 'Charles Dickens', 30),
    #    (3002, "Harry Potter and the Philosopher's Stone", 'J.K. Rowling', 40),
    #    (3003, 'The Lion, the Witch and the Warddrobe', 'C. S. Lewis', 25),
    #    (3004, 'The Lord of the Rings', 'J.R.R. Tolkien', 37),
    #    (3005, 'Alice in Wonderland', 'Lewis Carroll', 12)
    #]
    #cursor.executemany('''
    #    INSERT INTO timologia (ID, 
    #                         Title, 
    #                         Author, 
    #                         Qty)	
    #     VALUES(?,?,?,?)''', books_)

    #db.commit()
       # Catch the exception
    #except Exception as e:
    #    # Roll back any change if something goes wrong
    #    db.rollback()
    #    raise e
    #finally:
    #    # Close the db connection
    #    db.close()

    return db

# Add timologia in the db
def add_book(cursor):
    id= int(input('Τοποθετείστε αριθμό τιμολογίου:\n'))
    title = input('Τοποθετείστε προιόν και λεπτομέρειες:\n')
    author = input('Τοποθετείστε όνομα πελάτη:\n')
    qty = int(input('Τοποθετείστε ποσό τιμολογίου (ευρώ):\n'))
    cursor.execute('''INSERT INTO timologia(id, title, author,qty)
                   VALUES(?,?,?,?)''', (id, title, author,qty)
                  )
    
# Update the existing timimologia in the db
def update_book(cursor):
    id= int(input('Τοποθετείστε αριθμό τιμολογίου για ανανέωση αριθμού :\n'))
    title = input('Τοποθετείστε νέο προιόν και λεπτομέρειες:\n')
    author = input('Τοποθετείστε νέο όνομα πελάτη:\n')
    qty = int(input('Τοποθετείστε νέο ποσό τιμολογίου (ευρώ):\n'))
    cursor.execute('''UPDATE timologia SET Title = ?, Author = ?, Qty = ? 
                   WHERE ID = ?''', (title, author, qty, id)
                  )
# Remove any timologia
def delete_book(cursor):
    id= int(input('Τοποθετείστε αριθμό τιμολογίου για διαγραφή:\n'))
    cursor.execute('''DELETE FROM timologia
                    WHERE ID = ?''', (id,)
                  )

#retrieve data from sql db
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

# view timologia entires in the db 
def view_bookdb(cursor):
    # Verify the deletion
    cursor.execute('SELECT * FROM timologia')
    rows = cursor.fetchall()
    print("Δεδομένα μετά την διαγραφή:")
    for row in rows:
        print(row)

# save the entries of the db to .csv
def savedb_csv(cursor,db):
   # SQL query to retrieve data
   cursor.execute('''SELECT * FROM timologia''')
   rows = cursor.fetchall()

   with open('timologia.csv', 'w') as file:
      writer = csv.writer(file)
      writer.writerow(['Αρ. Τιμ.', 'Περιγραφή', 'Πελάτης', 'Euro'])
      writer.writerows(rows)       
   print("Η λίστα τιμολογίων έχει αποθηκευτεί στο τιμολόγια.csv")



# Main program
def main():
    #Call fun to create the book database-i.e. connection with sqlite
    db = create_database()
    #create the cursor object
    cursor = db.cursor() 
    
    while True:
      user_choice = int(input(usage_message))
      # Options of actions
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
        savedb_csv(cursor,db)
      elif user_choice==0:
          print("Εξοδος!")
     
          # SQL code that will delete all the data in the table, but not the table
          # Delete all data inside the Student table
          #cursor.execute('DELETE FROM timologia')
          #db.commit()
          
          db.close()
          break
      else:
            print("Μη αναγνωρίσημη επιλογή. Παρακαλώ δοκιμάστε ξανά.")
         
# Call the main program         
if __name__ == "__main__":
    main()



