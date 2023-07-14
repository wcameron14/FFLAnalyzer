import psycopg2
from psycopg2 import sql
import os

# Establish database connection
DATABASE_URL = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PW')} host=localhost port=5432"

def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    print("Database opened successfully")
    return conn, conn.cursor()

def create_table(conn, cur, table_name, fields):
    # This function creates a table with the given fields
    query = sql.SQL(f"""CREATE TABLE IF NOT EXISTS {table_name} ({fields});""")
    cur.execute(query)
    conn.commit()

def insert_data(conn, cur, table, columns, data, conflict_column):
    # Replace Python's None with SQL's NULL
    data = ['NULL' if value is None else value for value in data]

    try:
        # Prepare the INSERT statement
        query = f"""
            INSERT INTO {table} ({columns}) 
            VALUES ({', '.join(['%s' if value != 'NULL' else value for value in data])}) 
            ON CONFLICT ({conflict_column}) DO NOTHING
        """
       
        # Execute the query
        cur.execute(query, [value for value in data if value != 'NULL'])
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")
