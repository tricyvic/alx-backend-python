import mysql
import mysql.connector
from mysql.connector import errorcode
import csv
import uuid

DB_CONFIG = {
    'user': 'root',         # Change as needed
    'password': '',         # Change as needed
    'host': 'localhost',
    'port': 3306
}

DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_database(connection):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
    finally:
        cursor.close()

def connect_to_prodev():
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_table(connection):
    cursor = connection.cursor()
    table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        UNIQUE KEY unique_email (email),
        INDEX idx_user_id (user_id)
    )
    """
    try:
        cursor.execute(table_query)
    except mysql.connector.Error as err:
        print(f"Failed creating table: {err}")
    finally:
        cursor.close()

def insert_data(connection, data_file):
    cursor = connection.cursor()
    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if email already exists
            cursor.execute(f"SELECT user_id FROM {TABLE_NAME} WHERE email = %s", (row['email'],))
            if cursor.fetchone():
                continue  # Skip duplicates
            user_id = str(uuid.uuid4())
            try:
                cursor.execute(
                    f"INSERT INTO {TABLE_NAME} (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                    (user_id, row['name'], row['email'], row['age'])
                )
            except mysql.connector.Error as err:
                print(f"Error inserting row: {err}")
    connection.commit()
    cursor.close()