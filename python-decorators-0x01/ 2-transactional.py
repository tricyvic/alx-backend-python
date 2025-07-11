import sqlite3 
import functools

def with_db_connection(func):
    with sqlite3.connect('users.db') as conn:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(conn, *args, **kwargs)
        return wrapper
    
# transactional(func) that ensures a function running a database operation is wrapped inside a transaction.If the function raises an error, rollback; otherwise commit the transaction.
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit the transaction if no exception occurs
            return result
        except Exception as e:
            conn.rollback()  # Rollback the transaction on error
            raise e  # Re-raise the exception for further handling
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')