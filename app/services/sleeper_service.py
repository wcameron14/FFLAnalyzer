import logging
import app.database.queries as queries
from datetime import datetime
from db.user import get_user, insert_user
from db.players import get_all_players, insert_players
from db.leagues import get_all_leagues_for_user, get_users_in_league, insert_leagues, insert_league_owners, get_league_settings, insert_league_settings
from db.rosters import get_rosters_in_league, insert_rosters
from db.matchups import get_matchups_in_league, insert_matchups
from db.transactions import get_transactions, insert_trade, insert_waivers, insert_traded_draft_pick, insert_traded_waiver_budget
from db.drafts import get_draft_picks, insert_draft_picks
from tqdm import tqdm

conn, cur = queries.connect_to_db()

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()

#Get All Data
def get_all_data(start_year, username):
    logging.debug(f'Running get_all_data for username: {username} and start_year: {start_year}')
    
    # User
    user_data = get_user(username)
    logging.debug(f'User data fetched for username: {username}')
    insert_user(conn, cur, user_data)  

    # Players
    player_data = get_all_players()
    logging.debug(f'Player data fetched')
    insert_players(conn, cur, player_data)  
    
    # Leagues
    user_id = user_data['user_id']
    table = 'Leagues'
    columns = 'league_id, name, season, status, sport, total_rosters, previous_league_id, draft_id, avatar'
    conflict_target = 'league_id'

    # League_owners & Team_name
    for year in tqdm(range(start_year, datetime.now().year + 1), desc='Processing years for leagues'):
        leagues = get_all_leagues_for_user(user_id, year)
        logging.debug(f'League data fetched for year: {year}')
        
        for league in leagues:
            # Skip the problematic league
            if league[0] == '467385771892928512':
                continue
            league_id = league[0]

            # Fetch and insert league settings
            league_settings = get_league_settings(league_id)
            insert_league_settings(conn, cur, league_settings)

            insert_leagues(conn, cur, league)

            league_id = league[0]
            users_in_league = get_users_in_league(league_id)
            logging.debug(f'Users in league data fetched for league_id: {league_id}')
            insert_league_owners(conn, cur, league_id)  
            
            rosters = get_rosters_in_league(league_id)
            insert_rosters(conn, cur, rosters)  

            # Matchups
            for week in range(1, 17 if year < 2021 else 18):
                matchups = get_matchups_in_league(league_id, week)
                insert_matchups(conn, cur, matchups)
            
            #Draft Picks
            cur.execute("SELECT draft_id FROM leagues")
            draft_ids = [row[0] for row in cur.fetchall()]

            # Get the draft picks for each draft ID
            for draft_id in draft_ids:
                draft_picks = get_draft_picks(conn, cur, draft_id)  # get_draft_picks() now returns draft picks data
                if draft_picks:  # Make sure there is data before trying to insert it
                    insert_draft_picks(conn, cur, draft_id)

    # Code to fetch and insert transactions
    for year in tqdm(range(start_year, datetime.now().year + 1), desc='Processing years for transactions'):
        leagues = get_all_leagues_for_user(user_id, year)
        for league in leagues:
            transactions = get_transactions(league[0])
            for transaction in transactions:
                if transaction['type'] == 'trade':
                    insert_trade(conn, cur, transaction)
                elif transaction['type'] in ['free_agent', 'waiver']:
                    insert_waivers(conn, cur, transaction)

    conn.commit()
