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