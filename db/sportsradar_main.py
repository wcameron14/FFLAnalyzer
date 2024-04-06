import app.database.queries as queries
from app.database.queries import connect_to_db
from nfl_schedules import get_nfl_schedule, insert_nfl_schedule
from datetime import datetime
from nfl_rush_stats import get_rush_stats, insert_rush_stats

start_year = 2018
conn, cur = connect_to_db()

queries.create_sportsradar_table(conn, cur, 'nfl_schedules',"schedule_id TEXT, year INTEGER, schedule_type TEXT, schedule_name TEXT, week_id TEXT, sequence INTEGER, game_id TEXT, home_name TEXT, away_name TEXT, PRIMARY KEY ( schedule_id, week_id, game_id)")
queries.create_table(conn, cur, 'game_rushing_stats', "game_id TEXT, player_id TEXT, first_downs INTEGER, rush_avg_yards FLOAT, rush_attempts INTEGER, rush_touchdowns INTEGER, rush_yards INTEGER, rush_longest INTEGER, rush_redzone_attempts INTEGER, tlost INTEGER, tlost_yards INTEGER, broken_tackles INTEGER, kneel_downs INTEGER, scrambles INTEGER, yards_after_contact INTEGER, PRIMARY KEY (game_id, player_id)")


def main():
    # Connect to the database
    conn, cur = connect_to_db()

    # Fetch and insert NFL schedule data for each year
    for year in range(start_year, datetime.now().year + 1):
        nfl_schedule_data = get_nfl_schedule(year)
        insert_nfl_schedule(conn, cur, nfl_schedule_data)

    # Fetch and insert NFL game rushing statistics data for each game
    cur.execute("SELECT game_id FROM nfl_schedules")
    game_ids = [row[0] for row in cur.fetchall()]
    for game_id in game_ids:
        rushing_data = get_rush_stats(game_id)  # make sure this now returns rushing data
        insert_rush_stats(conn, cur, rushing_data)


    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
