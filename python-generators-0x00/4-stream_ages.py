import sqlite3

def stream_user_ages():
    """Generator yielding ages one by one from the database"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    conn.close()

def calculate_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    average = total_age / count if count else 0
    print(f"Average age of users: {average}")

if __name__ == "__main__":
    calculate_average_age()
