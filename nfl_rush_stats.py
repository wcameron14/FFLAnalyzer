import os
import requests
from tqdm import tqdm
from datetime import datetime
from time import sleep
import database
from psycopg2 import sql

# Establish a connection to the database
api_key = os.getenv('SPORTRADAR_API_KEY')
conn, cur = database.connect_to_db()

def extract_rushing_data(player, game_id, team_type):
    # Extract the player-level rushing data
    return {
        "game_id": game_id,
        "team_type": team_type,
        "player_id": player.get("id"),
        "name": player.get("name"),
        "position": player.get("position"),
        "first_downs": player.get("first_downs"),
        "rush_avg_yards": player.get("avg_yards"),
        "rush_attempts": player.get("attempts"),
        "rush_touchdowns": player.get("touchdowns"),
        "rush_yards": player.get("yards"),
        "rush_longest": player.get("longest"),
        "rush_redzone_attempts": player.get("redzone_attempts"),
        "tlost": player.get("tlost"),
        "tlost_yards": player.get("tlost_yards"),
        "broken_tackles": player.get("broken_tackles"),
        "kneel_downs": player.get("kneel_downs"),
        "scrambles": player.get("scrambles"),
        "yards_after_contact": player.get("yards_after_contact")
    }


def get_rush_stats(game_id):
    # Fetch all the game IDs
    cur.execute(f"SELECT game_id FROM nfl_schedules")
    game_ids = [row[0] for row in cur.fetchall()]

    # Initialize a list to hold all the game statistics data
    all_game_statistics = []

    # Loop over the game IDs
    for game_id in tqdm(game_ids, desc=f"Fetching NFL Rush Stats data"):
        # Make the API request
        response = requests.get(f"http://api.sportradar.us/nfl/official/trial/v7/en/games/{game_id}/statistics.json?api_key={api_key}")

        # Check the response
        if response.status_code == 200:
            # Parse the JSON data
            data = response.json()

    # Initialize the list for rushing data
    rushing_data = []

    # Loop over the 'home' and 'away' teams
    for team_type in ['home', 'away']:
        # Check if the team has rushing statistics
        if team_type in data['statistics'] and 'rushing' in data['statistics'][team_type] and 'players' in data['statistics'][team_type]['rushing']:
            # Loop over the players
            for player in data['statistics'][team_type]['rushing']['players']:
                # Extract the rushing data for the player
                player_rushing_data = extract_rushing_data(player, game_id, team_type)

                # Add the rushing data to the list
                rushing_data.append(player_rushing_data)
    
    # Return the rushing statistics data
    return rushing_data

# Function to insert rushing data
def insert_rush_stats(conn, cur, rushing_data):
    # Define the SQL query for inserting data
    query = sql.SQL("""
        INSERT INTO game_rushing_stats (game_id, player_id, first_downs, rush_avg_yards, rush_attempts, rush_touchdowns, rush_yards, rush_longest, rush_redzone_attempts, tlost, tlost_yards, broken_tackles, kneel_downs, scrambles, yards_after_contact)
        VALUES (%(game_id)s, %(player_id)s, %(first_downs)s, %(rush_avg_yards)s, %(rush_attempts)s, %(rush_touchdowns)s, %(rush_yards)s, %(rush_longest)s, %(rush_redzone_attempts)s, %(tlost)s, %(tlost_yards)s, %(broken_tackles)s, %(kneel_downs)s, %(scrambles)s, %(yards_after_contact)s)
        ON CONFLICT (game_id, player_id) DO NOTHING;
    """)

    # Loop over the rushing data
    for data in rushing_data:
        # Execute the SQL query
        cur.execute(query, data)

    # Commit the changes
    conn.commit()
