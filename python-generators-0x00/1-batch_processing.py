import sqlite3

def stream_users_in_batches(batch_size):
    """Generator that yields users in batches from the database"""
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield [dict(row) for row in rows]

    cursor.close()
    conn.close()

def batch_processing(batch_size):
    """Processes batches to filter users over the age of 25"""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)

# "return"
