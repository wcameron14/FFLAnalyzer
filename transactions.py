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

#Get Transactions
def get_transactions(league_id):
    logger.debug(f'Running get_transactions for league_id: {league_id}')
    round = 1
    transactions = []
    while True:
        url = f"https://api.sleeper.app/v1/league/{league_id}/transactions/{round}"
        response = requests.get(url)
        if response.status_code != 200:
            break
        transaction_data = response.json()
        if not transaction_data:
            break
        transactions.extend(transaction_data)
        round += 1
    logger.debug(f'Fetched transactions for league_id: {league_id}')
    return transactions

#Inserting traded draft picks
def insert_traded_draft_pick(conn, cur, transaction_id, pick):
    try:
        print("Inserting traded draft pick data...")
        # Log the draft pick data
        logger.debug(f"Traded draft pick data being inserted is {pick}")

        query = """
            INSERT INTO Traded_Draft_Picks (transaction_id, season, round, roster_id, previous_owner_id, owner_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id, season, round, roster_id, previous_owner_id)
            DO UPDATE SET 
                season = EXCLUDED.season,
                round = EXCLUDED.round,
                roster_id = EXCLUDED.roster_id,
                previous_owner_id = EXCLUDED.previous_owner_id,
                owner_id = EXCLUDED.owner_id
        """

        data = (transaction_id, pick['season'], pick['round'], pick['roster_id'], pick['previous_owner_id'], pick['owner_id'])
        cur.execute(query, data)
        conn.commit()
        logger.debug("Traded draft pick data inserted successfully")

    except Exception as e:
        logger.error(f"An error occurred while inserting traded draft pick data: {e}")

#Inserting traded waiver budget
def insert_traded_waiver_budget(conn, cur, transaction_id, budget):
    try:
        print("Inserting traded waiver budget data...")
        # Log the waiver budget data
        logger.debug(f"Traded waiver budget data being inserted is {budget}")

        query = """
            INSERT INTO Traded_Waiver_Budgets (transaction_id, sender, receiver, amount) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (transaction_id) 
            DO UPDATE SET 
                sender = EXCLUDED.sender,
                receiver = EXCLUDED.receiver,
                amount = EXCLUDED.amount
        """
        data = (transaction_id, budget['sender'], budget['receiver'], budget['amount'])
        cur.execute(query, data)
        conn.commit()
        logger.debug("Traded waiver budget data inserted successfully")

    except Exception as e:
        logger.error(f"An error occurred while inserting traded waiver budget data: {e}")

#Insert Trades    
def insert_trade(conn, cur, transaction):
    try:
        print("Inserting trade data...")
        # Log the trade data
        logger.debug(f"Trade data being inserted is {transaction}")
        # Replace 'None' with an empty dictionary
        if transaction['drops'] is None:
            transaction['drops'] = {}

        # Convert 'adds' 'drops' and 'settings' to a string if necessary
        if isinstance(transaction['adds'], dict):
            transaction['adds'] = json.dumps(transaction['adds'])
        if isinstance(transaction['drops'], dict):
            transaction['drops'] = json.dumps(transaction['drops'])

        query = """
            INSERT INTO Trades (transaction_id, type, status, roster_ids, creator, week, consenter_ids, drops, adds) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (transaction_id) 
            DO UPDATE SET 
                type = EXCLUDED.type,
                status = EXCLUDED.status,
                roster_ids = EXCLUDED.roster_ids,
                creator = EXCLUDED.creator,
                week = EXCLUDED.week,
                consenter_ids = EXCLUDED.consenter_ids,
                drops = EXCLUDED.drops,
                adds = EXCLUDED.adds
        """

        values = [transaction[key] for key in ('transaction_id', 'type', 'status', 'roster_ids', 'creator', 'leg', 'consenter_ids', 'drops', 'adds')]
        cur.execute(query, values)
        conn.commit()
        logger.debug("Trade data inserted successfully")

        # Insert traded draft picks
        if 'draft_picks' in transaction and transaction['draft_picks']:
            for pick in transaction['draft_picks']:
                insert_traded_draft_pick(conn, cur, transaction['transaction_id'], pick)


        # Insert traded waiver budgets
        if 'waiver_budget' in transaction and transaction['waiver_budget']:
            for budget in transaction['waiver_budget']:
                insert_traded_waiver_budget(conn, cur, transaction['transaction_id'], budget)

    except Exception as e:
        logger.error(f"An error occurred while inserting trade data: {e}")


#Insert Waivers
def insert_waivers(conn, cur, transaction):
    try:
        print("Inserting waiver data...")
        logger.debug(f"Waiver data being inserted is {transaction}")
        # Replace 'None' with an empty dictionary
        if transaction['drops'] is None:
            transaction['drops'] = {}

        # Convert 'adds', 'drops and, 'settings' to a string if necessary
        if isinstance(transaction['adds'], dict):
            transaction['adds'] = json.dumps(transaction['adds'])
        if isinstance(transaction['drops'], dict):
            transaction['drops'] = json.dumps(transaction['drops'])
        if isinstance(transaction['settings'], dict):
            transaction['settings'] = json.dumps(transaction['settings'])

        
        # Define values and query
        values = [transaction[key] for key in ('transaction_id', 'type', 'status', 'roster_ids', 'drops', 'adds', 'creator', 'created', 'leg', 'consenter_ids', 'settings')]
        query = """
            INSERT INTO Waivers (transaction_id, type, status, roster_ids, drops, adds, creator, created, week, consenter_ids, settings) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (transaction_id) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                roster_ids = EXCLUDED.roster_ids,
                drops = EXCLUDED.drops,
                adds = EXCLUDED.adds,
                creator = EXCLUDED.creator,
                created = EXCLUDED.created,
                week = EXCLUDED.week,
                consenter_ids = EXCLUDED.consenter_ids,
                settings = EXCLUDED.settings
        """

        # Execute the SQL command
        cur.execute(query, values)
        conn.commit()
        logger.debug("Waiver data inserted successfully")
    except Exception as e:
        logger.error(f"An error occurred while inserting waiver data: {e}")