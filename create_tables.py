import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Players (
            player_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """,
        # Add other table creation commands here
    )

    try:
        connection = psycopg2.connect(
            user=os.dotenv("POSTGRES_USER"),
            password=os.dotenv("POSTGRES_PW"),
            host= os.dotenv("POSTGRES_HOST"),
            port=os.dotenv("POSTGRES_PORT"),
            database=os.dotenv("POSTGRES_DB")
        )
        cursor = connection.cursor()
        for command in commands:
            cursor.execute(command)
        connection.commit()
        cursor.close()
        connection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    create_tables()
