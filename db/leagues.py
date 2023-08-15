import requests
import logging
import app.database.queries as queries
from datetime import datetime
import json
from user import get_user, insert_user


conn, cur = queries.connect_to_db()

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

# Get All Leagues for User
def get_all_leagues_for_user(user_id, start_year):
    logger.debug(f'Running get_all_leagues_for_user for user_id: {user_id} and start_year: {start_year}')

    try:
        response = requests.get(f'https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{start_year}')
        response.raise_for_status()  # This will raise an exception if the request failed
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching leagues for user {user_id}: {e}")
        return []  # return an empty list if an error occurred

    data = response.json()
    leagues = []
    for league in data:
        leagues.append((league['league_id'], league['name'], league['season'], league['status'], league['sport'], league['total_rosters'], league['previous_league_id'], league['draft_id'], league['avatar']))

    logger.debug(f'Fetched leagues for user_id: {user_id}')  # logging statement to check the user_id
    logger.debug(leagues)  # logging fetched leagues

    return leagues

# Get Users in League
def get_users_in_league(league_id):
    logger.debug(f'Running get_users_in_league for league_id: {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(url)
    response.raise_for_status()
    users = response.json()
    logger.debug(f'Fetched users for league_id: {league_id}')  # logging statement to check the league_id
    logger.debug(users)  # logging fetched users
    return users

def get_league_settings(league_id):
    try:
        print(f"Getting settings for league {league_id}...")
        url = f"https://api.sleeper.app/v1/league/{league_id}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        settings = response.json()
        logger.debug(f"Got settings for league {league_id}")
        return settings
    except Exception as e:
        logger.error(f"An error occurred while getting settings for league {league_id}: {e}")


# Inserting data into Leagues
def insert_leagues(conn, cur, league):
    # Unpack the values from the league tuple, replacing None with Python's None
    league_id, name, season, status, sport, total_rosters, previous_league_id, draft_id, avatar = league

    # Prepare the INSERT statement
    query = f"""
        INSERT INTO Leagues (league_id, name, season, status, sport, total_rosters, previous_league_id, draft_id, avatar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (league_id) DO NOTHING
    """

    # Prepare the values
    values = (league_id or None, name or None, season or None, status or None, sport or None, total_rosters or None, previous_league_id or None, draft_id or None, avatar or None)

    try:
        # Execute the query
        cur.execute(query, values)
    except Exception as e:
        print(f"Error inserting data into Leagues: {e}")
conn.commit()

# Inserting data into League_owners
def insert_league_owners(conn, cur, league_id):
    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users")
    response.raise_for_status()
    users = response.json()

    for user in users:
        insert_user(conn, cur, user)
        league_owner = {
            'league_id': league_id,
            'display_name': user['display_name'],
            'user_id': user['user_id'],
            'is_owner': user.get('is_owner', False)
        }
        # Check for 'NULL' string and replace it with None
        if league_owner['is_owner'] == 'NULL':
            league_owner['is_owner'] = None
        queries.insert_data(conn, cur, 'league_owners', 'league_id, display_name, user_id, is_owner', tuple(league_owner.values()), 'league_id, user_id')

        if 'metadata' in user and 'team_name' in user['metadata']:
            team_name = {
                'user_id': user['user_id'],
                'display_name': user['display_name'],
                'league_id': user['league_id'],
                'team_name': user['metadata']['team_name']
            }
            queries.insert_data(conn, cur, 'team_name', 'user_id, display_name, league_id, team_name', tuple(team_name.values()), 'user_id')

#Insert League Settings
def insert_league_settings(conn, cur, settings):
    try:
        print(f"Inserting settings for league {settings['league_id']}...")
        query = """
            INSERT INTO League_Settings (league_id, total_rosters, status, sport, settings, season_type, season, scoring_settings, roster_positions, previous_league_id, name, draft_id, avatar) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (league_id) 
            DO UPDATE SET 
                total_rosters = EXCLUDED.total_rosters,
                status = EXCLUDED.status,
                sport = EXCLUDED.sport,
                settings = EXCLUDED.settings,
                season_type = EXCLUDED.season_type,
                season = EXCLUDED.season,
                scoring_settings = EXCLUDED.scoring_settings,
                roster_positions = EXCLUDED.roster_positions,
                previous_league_id = EXCLUDED.previous_league_id,
                name = EXCLUDED.name,
                draft_id = EXCLUDED.draft_id,
                avatar = EXCLUDED.avatar
        """
        data = (
            settings['league_id'], settings['total_rosters'], settings['status'], settings['sport'], 
            json.dumps(settings['settings']), settings['season_type'], settings['season'], 
            json.dumps(settings['scoring_settings']), json.dumps(settings['roster_positions']), 
            settings['previous_league_id'], settings['name'], settings['draft_id'], settings['avatar']
        )
        cur.execute(query, data)
        conn.commit()
        logger.debug(f"Inserted settings for league {settings['league_id']}")
    except Exception as e:
        logger.error(f"An error occurred while inserting settings for league {settings['league_id']}: {e}")
