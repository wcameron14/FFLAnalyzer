import requests
import database
import api
import logging
import os

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

conn, cur = database.connect_to_db()
# Creating tables
database.create_table(conn,cur, 'Users', "user_id VARCHAR PRIMARY KEY, username VARCHAR, display_name VARCHAR, avatar VARCHAR")
database.create_table(conn, cur, 'Leagues', "league_id VARCHAR PRIMARY KEY, name text, season INTEGER, status text, sport text, total_rosters integer, previous_league_id text, draft_id text, avatar VARCHAR")
database.create_table(conn, cur, 'Players', "player_id VARCHAR PRIMARY KEY, full_name VARCHAR, position VARCHAR, team VARCHAR, age INTEGER, years_exp INTEGER")
database.create_table(conn, cur, 'League_owners', "league_id VARCHAR, user_id VARCHAR, is_owner boolean, PRIMARY KEY (league_id, user_id)")
database.create_table(conn, cur, 'Team_Name', "user_id VARCHAR PRIMARY KEY, league_id VARCHAR, team_name VARCHAR")
database.create_table(conn, cur, 'Rosters', """league_id VARCHAR, owner_id VARCHAR, roster_id VARCHAR, players VARCHAR, reserve VARCHAR, starters VARCHAR, wins INTEGER, waiver_position INTEGER, waiver_budget_used INTEGER, total_moves INTEGER, ties INTEGER, losses INTEGER, fpts_decimal INTEGER, fpts_against_decimal INTEGER, fpts_against INTEGER, fpts INTEGER, PRIMARY KEY (league_id, owner_id)""")
database.create_table(conn, cur, 'matchups', "roster_id VARCHAR, matchup_id VARCHAR, starters VARCHAR, players VARCHAR, points FLOAT, custom_points FLOAT, PRIMARY KEY (roster_id, matchup_id)")
database.create_table(conn, cur, 'Trades', """transaction_id VARCHAR PRIMARY KEY, type VARCHAR, status VARCHAR, roster_ids VARCHAR, creator VARCHAR, week INTEGER, consenter_ids VARCHAR, drops JSONB, adds JSONB""")
database.create_table(conn, cur, 'Waivers',"""transaction_id VARCHAR PRIMARY KEY, type VARCHAR, status VARCHAR, roster_ids VARCHAR, drops JSONB, adds JSONB, creator VARCHAR, created BIGINT, week INTEGER, consenter_ids VARCHAR, settings JSONB""")
database.create_table(conn, cur, 'Traded_Draft_Picks', """transaction_id VARCHAR, season INT, round INT, roster_id INT, previous_owner_id INT, owner_id INT, PRIMARY KEY (transaction_id, season, round, roster_id, previous_owner_id)""")
database.create_table(conn, cur, 'Traded_Waiver_Budgets',"""transaction_id VARCHAR PRIMARY KEY, sender INT, receiver INT, amount INT""")
database.create_table(conn, cur, 'league_settings',"""league_id TEXT PRIMARY KEY, total_rosters INTEGER, status TEXT, sport TEXT, settings JSONB, season_type TEXT, season TEXT, scoring_settings JSONB, roster_positions JSONB, previous_league_id TEXT, name TEXT, draft_id TEXT, avatar TEXT""")

username = os.getenv('SLEEPER_USERNAME')

if __name__ == "__main__":
    api.get_all_data(2018, username)

# Close database connection
cur.close()
conn.close()