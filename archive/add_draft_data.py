from app.database.queries import connect_to_db
import pandas as pd

#Run this code to update the draft_picks table with the budget_percent, draft_value and budget_amount columns

# Load your CSV data into a DataFrame
df = pd.read_csv(r"C:\Users\Admin\Desktop\FFLBot\GPT_FFL\River_City_Draft_Data.csv", dtype={'draft_id':str})

# Filter data from 2018 onwards and drop any rows that contain null values in Owner_id, League_id or player_id
df = df[df['Season'] >= 2018]
df = df.dropna(subset=['Owner_id', 'League_id', 'player_id'])

from app.database.queries import connect_to_db

def update_draft_picks_with_budget_percent(df):
    # Use the existing connect_to_db function to establish a connection to the PostgreSQL database
    conn, cur = connect_to_db()

    # Iterate through the rows of the DataFrame
    for _, row in df.iterrows():
        # Define the SQL query for updating the draft_picks table
        query = """
        UPDATE draft_picks
        SET budget_percent = %s, draft_value = %s, budget_amount = %s
        WHERE player_id = %s AND picked_by = %s AND draft_id = %s
        """
        # Execute the SQL query with the data from the DataFrame row
        # Convert Owner_id, League_id and draft_id to strings
        cur.execute(query, (row['Budget%'], row['Draft Value'], row['Budget'], row['Owner'], row['player_id'], str(row['Owner_id']), str(row['draft_id'])))
        
        # Check how many rows were affected
        rows_affected = cur.rowcount
        if rows_affected == 0:
            print(f"No rows updated for player_id {row['player_id']}, picked_by {str(row['Owner_id'])}, draft_id {str(row['draft_id'])}")
        else:
            print(f"{rows_affected} row(s) updated for player_id {row['player_id']}, picked_by {str(row['Owner_id'])}, draft_id {str(row['draft_id'])}")
    
    # Commit the changes and close the connection
    conn.commit()
    cur.close()
    conn.close()

    # Call the function with your DataFrame
    update_draft_picks_with_budget_percent(df)