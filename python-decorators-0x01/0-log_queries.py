import sqlite3
import functools 
from datetime import datetime

# also check time of execution
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the query and the time of execution
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = args[0] if args else kwargs.get('query', '')
        print(f"Executing query: {query}")
        print(f"[{timestamp}] Executing function: {func.__doc__}")
        return func(*args, **kwargs)

    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")