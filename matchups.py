import requests
import logging
import database
from datetime import datetime
import json

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

# Get Matchup Data for a given league
def get_matchups_in_league(league_id, week):
    logger.debug(f'Running get_matchups_in_league for league_id: {league_id} and week: {week}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching matchups for league {league_id} and week {week}: {e}")
        return []    
    matchups_json = response.json()
    logger.debug(f'Fetched matchups for league_id: {league_id} and week: {week}')

    matchups = []
    for matchup in matchups_json:
        starters = ','.join(matchup.get('starters', []))
        players = ','.join(matchup.get('players', []))
        points = matchup.get('points')
        custom_points = matchup.get('custom_points')
        roster_id = matchup.get('roster_id')

        # Assign a default value to matchup_id if it is not present or None
        matchup_id = matchup.get('matchup_id')
        if matchup_id is None:
            matchup_id = 99
            logger.debug(f"Default matchup_id assigned for league_id: {league_id}, week: {week}, roster_id: {roster_id}")

        matchups.append((roster_id, matchup_id, starters, players, points, custom_points))

    return matchups

#Insert Matchups
def insert_matchups(conn, cur, matchup_data):
    try:
        print("Inserting matchups data...")
        # Log the matchup data
        logger.debug(f"Matchup data being inserted is {matchup_data}")

        query = """
            INSERT INTO Matchups (roster_id, matchup_id, starters, players, points, custom_points) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON CONFLICT (roster_id, matchup_id) 
            DO UPDATE SET 
                starters = EXCLUDED.starters, 
                players = EXCLUDED.players, 
                points = EXCLUDED.points,
                custom_points = EXCLUDED.custom_points
        """
        cur.executemany(query, matchup_data)
        conn.commit()
        print("Matchups data inserted successfully")
    except Exception as e:
        print("An error occurred while inserting matchups data:", e)