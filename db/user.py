import requests
import logging
import app.database.queries as queries
from datetime import datetime
import json
import os


conn, cur = queries.connect_to_db()

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

def get_user(username):
    url = f"https://api.sleeper.app/v1/user/{username}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception if the request failed
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching user data: {e}")
        return None  # You might want to return a default value or handle this case in your calling code
    return response.json()

# Inserting data into Users
def insert_user(conn, cur, user_data):
    user_id = user_data.get('user_id')
    username = user_data.get('username')
    display_name = user_data.get('display_name')
    avatar = user_data.get('avatar')

    if user_id and username and display_name and avatar:
        query = f"INSERT INTO Users (user_id, username, display_name, avatar) VALUES ('{user_id}', '{username}', '{display_name}', '{avatar}') ON CONFLICT (user_id) DO NOTHING"
        try:
            cur.execute(query)
            print(f"User {username} loaded successfully into database")
        except Exception as e:
            print(f"An error occurred while inserting user data: {e}")
    conn.commit()