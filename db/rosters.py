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

#Get Roster Data for a given league
def get_rosters_in_league(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching rosters for league {league_id}: {e}")
        return []
    rosters = response.json()
    rosters_data = []
    for roster in rosters:
        if roster['owner_id'] is None:
            continue
        settings = roster['settings']
        players = ','.join(roster['players']) if isinstance(roster['players'], list) else None
        starters = ','.join(roster['starters']) if isinstance(roster['starters'], list) else None
        reserves = ','.join(roster['reserve']) if isinstance(roster['reserve'], list) else None
        rosters_data.append((
            roster['league_id'],
            roster['owner_id'],
            roster['roster_id'],
            players,
            starters,
            reserves,
            settings['wins'],
            settings['waiver_position'],
            settings['waiver_budget_used'],
            settings['total_moves'],
            settings['ties'],
            settings['losses'],
            settings.get('fpts_decimal', 0),
            settings.get('fpts_against_decimal', 0),
            settings.get('fpts_against', 0),
            settings.get('fpts', 0)
        ))
    return rosters_data

#Inserting data into Rosters
def insert_rosters(conn, cur, rosters):
    try:
        print("Inserting rosters data...")
        query = """
            INSERT INTO Rosters (league_id, owner_id, roster_id, starters, players, reserve, wins, waiver_position, waiver_budget_used, total_moves, ties, losses, fpts_decimal, fpts_against_decimal, fpts_against, fpts) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (league_id, owner_id) 
            DO UPDATE SET 
                starters = EXCLUDED.starters,
                players = EXCLUDED.players,
                reserve = EXCLUDED.reserve,
                wins = EXCLUDED.wins,
                waiver_position = EXCLUDED.waiver_position,
                waiver_budget_used = EXCLUDED.waiver_budget_used,
                total_moves = EXCLUDED.total_moves,
                ties = EXCLUDED.ties,
                losses = EXCLUDED.losses,
                fpts_decimal = EXCLUDED.fpts_decimal,
                fpts_against_decimal = EXCLUDED.fpts_against_decimal,
                fpts_against = EXCLUDED.fpts_against,
                fpts = EXCLUDED.fpts
        """
        cur.executemany(query, rosters)
        conn.commit()
        print("Rosters data inserted successfully")
    except Exception as e:
        print("An error occurred while inserting rosters data:", e)
        print("Rosters data:", rosters)