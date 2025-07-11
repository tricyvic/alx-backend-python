import sqlite3

db = sqlite3.connect('users.db')
cursor = db.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   email TEXT NOT NULL UNIQUE,
                   age INTEGER NOT NULL 
                );''')

cursor.execute('''
               INSERT INTO users (name, email, age) VALUES (
                     'Kate', 'Kate@email.com', 30
                );''')
db.commit()
db.close()