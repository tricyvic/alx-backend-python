import time
import sqlite3 
import functools


query_cache = {}

def with_db_connection(func):
    with sqlite3.connect('users.db') as conn:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(conn, *args, **kwargs)
        return wrapper
    
def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query', None)
        if query in query_cache:
            print("Using cached result for query:", query)
            return query_cache[query]
        else:
            print("Executing query:", query)
            result = func(*args, **kwargs)
            query_cache[query] = result
            return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")