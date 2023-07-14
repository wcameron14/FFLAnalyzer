import requests
import json
import psycopg2
from psycopg2 import sql
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

# establish database connection
DATABASE_URL = "dbname=fflanalyzerSQL user=POSTGRES_DB password=postgres host=localhost port=5432"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database="fflanalyzerSQL",
        user="POSTGRES_DB",
        password="postgres")
    print("Database opened successfully")
    return conn
    
def create_table(cur, table_name, fields):
    # This function creates a table with the given fields
    query = sql.SQL(f"""CREATE TABLE IF NOT EXISTS {table_name} ({fields});""")
    cur.execute(query)
    conn.commit()

def insert_data(cur, table, columns, data, conflict_column):
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
        conn.commit()
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")




conn = connect_to_db()
cur = conn.cursor()

def get_all_players():
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    data = r.json()
    players = []
    for player_id, player_info in data.items():
        players.append((player_id, player_info.get('full_name'), player_info.get('position'), player_info.get('team'), player_info.get('age'),player_info.get('years_exp')))
    return players

def get_user(username):
    url = f"https://api.sleeper.app/v1/user/{username}"
    response = requests.get(url)
    user_data = response.json()
    return user_data

def get_all_leagues_for_user(user_id, start_year):
    logger.debug(f'Running get_all_leagues_for_user for user_id: {user_id} and start_year: {start_year}')
    r = requests.get(f'https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{start_year}')
    data = r.json()
    leagues = []
    for league in data:
        leagues.append((league['league_id'], league['name'], league['season'], league['status'], league['sport'], league['total_rosters'], league['previous_league_id'], league['draft_id'], league['avatar']))
    logger.debug(f'Fetched leagues for user_id: {user_id}')  # logging statement to check the user_id
    logger.debug(leagues)  # logging fetched leagues
    return leagues

def get_users_in_league(league_id):
    logger.debug(f'Running get_users_in_league for league_id: {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(url)
    response.raise_for_status()
    users = response.json()
    logger.debug(f'Fetched users for league_id: {league_id}')  # logging statement to check the league_id
    logger.debug(users)  # logging fetched users
    return users

#Get Roster Data for a given league
def get_rosters_in_league(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(url)
    response.raise_for_status()
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
# Get Matchup Data for a given league
def get_matchups_in_league(league_id, week):
    logger.debug(f'Running get_matchups_in_league for league_id: {league_id} and week: {week}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
    response = requests.get(url)
    response.raise_for_status()
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



# Creating tables
create_table(cur, 'Users', "user_id VARCHAR PRIMARY KEY, username VARCHAR, display_name VARCHAR, avatar VARCHAR")
create_table(cur, 'Leagues', "league_id VARCHAR PRIMARY KEY, name text, season INTEGER, status text, sport text, total_rosters integer, previous_league_id text, draft_id text, avatar VARCHAR")
create_table(cur, 'Players', "player_id VARCHAR PRIMARY KEY, full_name VARCHAR, position VARCHAR, team VARCHAR, age INTEGER, years_exp INTEGER")
create_table(cur, 'League_owners', "league_id VARCHAR, user_id VARCHAR, is_owner boolean, PRIMARY KEY (league_id, user_id)")
create_table(cur, 'Team_Name', "user_id VARCHAR PRIMARY KEY, league_id VARCHAR, team_name VARCHAR")
create_table(cur, 'Rosters', """league_id VARCHAR, owner_id VARCHAR, roster_id VARCHAR, players VARCHAR, reserve VARCHAR, starters VARCHAR, wins INTEGER, waiver_position INTEGER, waiver_budget_used INTEGER, total_moves INTEGER, ties INTEGER, losses INTEGER, fpts_decimal INTEGER, fpts_against_decimal INTEGER, fpts_against INTEGER, fpts INTEGER, PRIMARY KEY (league_id, owner_id)""")
create_table(cur, 'matchups', "roster_id VARCHAR, matchup_id VARCHAR, starters VARCHAR, players VARCHAR, points FLOAT, custom_points FLOAT, PRIMARY KEY (roster_id, matchup_id)")

# Inserting data into Users
def insert_user(cur, user_data):
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


# Inserting data into Leagues
def insert_leagues(cur, league):
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

# Inserting data into Players
def insert_players(player_data):
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

# Inserting data into League_owners
def insert_league_owners(cur, conn, league_id):
    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users")
    response.raise_for_status()
    users = response.json()

    for user in users:
        insert_user(cur, user)
        league_owner = {
            'league_id': user['league_id'],
            'user_id': user['user_id'],
            'is_owner': user.get('is_owner', False)
        }
        # Check for 'NULL' string and replace it with None
        if league_owner['is_owner'] == 'NULL':
            league_owner['is_owner'] = None
        insert_data(cur, 'league_owners', 'league_id, user_id, is_owner', tuple(league_owner.values()), 'league_id, user_id')

        if 'metadata' in user and 'team_name' in user['metadata']:
            team_name = {
                'user_id': user['user_id'],
                'league_id': user['league_id'],
                'team_name': user['metadata']['team_name']
            }
            insert_data(cur, 'team_name', 'user_id, league_id, team_name', tuple(team_name.values()), 'user_id')

#Inserting data into Rosters
def insert_rosters(cur, rosters):
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

#Insert Matchups
def insert_matchups(cur, matchup_data):
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
    

def get_all_data(start_year, username):
    logging.debug(f'Running get_all_data for username: {username} and start_year: {start_year}')
    
    # User
    user_data = get_user(username)
    logging.debug(f'User data fetched for username: {username}')
    insert_user(cur, user_data)  

    # Players
    player_data = get_all_players()
    logging.debug(f'Player data fetched')
    insert_players(player_data)  
    
    # Leagues
    user_id = user_data['user_id']
    table = 'Leagues'
    columns = 'league_id, name, season, status, sport, total_rosters, previous_league_id, draft_id, avatar'
    conflict_target = 'league_id'

    # League_owners & Team_name
    for year in range(start_year, datetime.now().year + 1):
        leagues = get_all_leagues_for_user(user_id, year)
        logging.debug(f'League data fetched for year: {year}')
        
        for league in leagues:
            # Skip the problematic league
            if league[0] == '467385771892928512':
                continue

            insert_leagues(cur, league)

            league_id = league[0]
            users_in_league = get_users_in_league(league_id)
            logging.debug(f'Users in league data fetched for league_id: {league_id}')
            insert_league_owners(cur, conn, league_id)  
            
            rosters = get_rosters_in_league(league_id)
            insert_rosters(cur, rosters)  

            # Matchups
            for week in range(1, 17 if year < 2021 else 18):
                matchups = get_matchups_in_league(league_id, week)
                insert_matchups(cur, matchups)


if __name__ == "__main__":
    get_all_data(2018, 'RVAPanthersFan')

# Close database connection
cur.close()
conn.close()
