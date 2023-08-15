import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

# Establish database connection
#DATABASE_URL = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PW')} host=postgres port=5432"
""" DATABASE_URL = os.getenv('DATABASE_URL')

def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    print("Database opened successfully")
    return conn, conn.cursor() """

def connect_to_db():
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Check if running in Docker
    if os.getenv('RUNNING_IN_DOCKER') == 'true':
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PW'),
            host='localhost',
            port='5432'
            )
    
    cur = conn.cursor()

    return conn, cur


def create_table(conn, cur, table_name, fields):
    # This function creates a table with the given fields
    query = sql.SQL(f"""CREATE TABLE IF NOT EXISTS {table_name} ({fields});""")
    cur.execute(query)
    conn.commit()

def create_sportsradar_table(conn, cur, table_name, fields):
    # This function creates a table with the given fields
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
        sql.Identifier(table_name),
        sql.SQL(fields)
    )
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
