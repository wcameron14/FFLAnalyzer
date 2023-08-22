import requests
import logging
import app.database.queries as queries
from datetime import datetime
import json


# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

def get_all_players():
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    data = r.json()
    players = []
    for player_id, player_info in data.items():
        players.append((player_id, player_info.get('full_name'), player_info.get('position'), player_info.get('team'), player_info.get('age'),player_info.get('years_exp')))
    return players

# Inserting data into Players
def insert_players(conn, cur, player_data):
    try:
        print("Inserting player data...")
        query = """
            INSERT INTO Players (player_id, full_name, team, position, age, years_exp) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON CONFLICT (player_id) 
            DO UPDATE SET 
                full_name = EXCLUDED.full_name, 
                team = EXCLUDED.team, 
                position = EXCLUDED.position,
                age = EXCLUDED.age,
                years_exp = EXCLUDED.years_exp
        """
        cur.executemany(query, player_data)
        conn.commit()
        print("Player data inserted successfully")
    except Exception as e:
        print("An error occurred while inserting player data:", e)
        print("Player data:", player_data)