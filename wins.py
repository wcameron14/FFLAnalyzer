import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
import database

# Establish a connection to the database
database.connect_to_db()
conn, cur = database.connect_to_db()



# Execute the SQL query and fetch the data into a pandas DataFrame
query = """
SELECT
    roster_id,
    league_id,
    COUNT(*) as total_games,
    SUM(wins) as total_wins,
    SUM(losses) as total_losses,
    SUM(fpts + fpts_decimal / 100.0) as total_points_for,
    SUM(fpts_against + fpts_against_decimal / 100.0) as total_points_against
FROM
    rosters
GROUP BY
    roster_id, league_id;
"""
df = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Create a bar chart
plt.figure(figsize=(10, 6))
plt.bar(df['roster_id'], df['total_wins'])
plt.xlabel('roster_id')
plt.ylabel('Total Wins')
plt.title('Total Wins for Each Team')
plt.show()
