import requests
from tqdm import tqdm
from datetime import datetime
from time import sleep
import os
import app.database.queries as queries

def get_nfl_schedule(year):
    # API endpoint
    api_key = os.getenv('SPORTRADAR_API_KEY')
    url = f"http://api.sportradar.us/nfl/official/trial/v7/en/games/{year}/REG/schedule.json?api_key={api_key}"

    # Fetch the schedule data
    response = requests.get(url)
    data = response.json()

    # Extract the desired data
    schedule_data = []
    for week in data['weeks']:
        for game in week['games']:
            game_data = {
                'schedule_id': data['id'],
                'year': data['year'],
                'schedule_type': data['type'],
                'schedule_name': data['name'],
                'week_id': week['id'],
                'sequence': week['sequence'],
                'game_id': game['id'],
                'home_name': game['home']['name'],
                'away_name': game['away']['name']
            }
            schedule_data.append(game_data)

    return schedule_data

def insert_nfl_schedule(conn, cur, schedule_data):
    # SQL query
    query = """
    INSERT INTO nfl_schedules (
        schedule_id, year, schedule_type, schedule_name, week_id, sequence, game_id, home_name, away_name
    ) VALUES (%(schedule_id)s, %(year)s, %(schedule_type)s, %(schedule_name)s, %(week_id)s, %(sequence)s, %(game_id)s, %(home_name)s, %(away_name)s)
    ON CONFLICT DO NOTHING
    """

    # Insert the data into the database
    for game_data in tqdm(schedule_data, desc='Inserting NFL schedule data'):
        cur.execute(query, game_data)
        conn.commit()

    print('Finished inserting NFL schedule data')
