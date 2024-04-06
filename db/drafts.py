import requests
import app.database.queries as queries
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(
    filename='debug.log',  # Log to this file
    format='%(asctime)s %(levelname)-8s %(message)s',  # Include timestamp
    level=logging.DEBUG  # Log all severity levels
)

logger = logging.getLogger()
conn, cur = queries.connect_to_db()

def get_draft_picks(conn, cur, draft_id):
    try:
        response = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks")
        response.raise_for_status()  # Raise an HTTPError if the response contains an HTTP status error code.
    except requests.exceptions.RequestException as err:
        logger.error(f"Error fetching draft picks for draft {draft_id}: {err}")
        return None

    return response.json()

def check_field(value):
    return None if value == "" else value

def insert_draft_picks(conn, cur, draft_id):
    draft_picks_data = get_draft_picks(conn, cur, draft_id)
    if draft_picks_data is not None:
        for pick in tqdm(draft_picks_data, desc=f"Inserting draft picks data for draft {draft_id}"):
            # Query remains the same
            query = """
            INSERT INTO draft_picks (player_id, picked_by, roster_id, round, draft_slot, pick_no, amount, team, status, sport, position, number, news_updated, last_name, injury_status, first_name, is_keeper, draft_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, draft_id)
            DO NOTHING;
            """
            # Check for the presence of "amount" and provide a default value if missing
            amount = pick["amount"] if "amount" in pick else None
            pick_data = (pick["player_id"], pick["picked_by"], check_field(pick["roster_id"]), check_field(pick["round"]), check_field(pick["draft_slot"]), check_field(pick["pick_no"]), amount, pick["metadata"]["team"], pick["metadata"]["status"], pick["metadata"]["sport"], pick["metadata"]["position"], check_field(pick["metadata"]["number"]), pick["metadata"]["news_updated"], pick["metadata"]["last_name"], pick["metadata"]["injury_status"], pick["metadata"]["first_name"], pick["is_keeper"], pick["draft_id"])
            try:
                logger.info(f"SQL query: {query}")  # Added logging output
                logger.info(f"Pick data: {pick_data}")  # Added logging output
                cur.execute(query, pick_data)
            except Exception as e:
                logger.error(f"Error inserting draft picks for draft {draft_id}: {e}")
                logger.error(f"Pick data: {pick_data}")
        conn.commit()
        logger.info(f"Successfully inserted draft picks for draft {draft_id}")
