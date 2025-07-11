import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()
        if exc_type is not None:
            print(f"An error occurred: {exc_value}")
        return False

with DatabaseConnection('users.db') as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    print(c.fetchall())