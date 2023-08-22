from app.database.queries import connect_to_db
import pandas as pd
import numpy as np

conn, cur = connect_to_db()

def get_draft_type(conn):
    query = "SELECT settings->>'type' as draft_type FROM league_settings"
    draft_type = pd.read_sql_query(query, conn)['draft_type'][0]
    print("Result: ", draft_type)
    return draft_type


def get_snake_value_data(conn):
    print("Entering snake block")
    query = "SELECT picked_by, round, draft_slot, player_id, position, team, season FROM draft_picks"
    df = pd.read_sql_query(query, conn)
    owners = pd.read_csv('River_City_Draft_Data.csv', usecols=['Owner_id', 'Owner', 'season'])
    owners['Owner_id'] = owners['Owner_id'].astype(str)
    print("Owners columns: ", owners.columns)
    df = pd.merge(df, owners, how='left', on=['picked_by', 'season'])
    print("Result: ", df)
    return df

def get_auction_value_data(conn):
    print("Entering auction block")
    query = "SELECT picked_by, price, player_id, position, team, season FROM draft_picks"
    df = pd.read_sql_query(query, conn)
    owners = pd.read_csv('River_City_Draft_Data.csv', usecols=['Owner_id', 'Owner', 'season'])
    owners['Owner_id'] = owners['Owner_id'].astype(str)
    print("Owners columns: ", owners.columns)
    df = pd.merge(df, owners, how='left', on=['picked_by', 'season'])
    print("Result: ", df)
    return df

def analyze_snake_draft(df):
    df['Owner'] = df['picked_by'].map(df.set_index(['picked_by', 'season'])['Owner'])
    position_counts = df.groupby(['Owner', 'position', 'season']).size()
    position_counts = position_counts.to_frame(name='counts').reset_index()
    return position_counts

def analyze_auction_draft(df):
    df['Owner'] = df['picked_by'].map(df.set_index(['picked_by', 'season'])['Owner'])
    position_values = df.groupby(['Owner', 'position', 'season'])['price'].sum()
    position_values = position_values.to_frame(name='total_value').reset_index()
    return position_values


owner = pd.read_csv('River_City_Draft_Data.csv', usecols=['Owner_id', 'Owner'])
owner['Owner_id'] = owner['Owner_id'].astype(str)

draft_type = get_draft_type(conn)

if draft_type == '1':  # Auction draft
    df = get_auction_value_data(conn)
    result = analyze_auction_draft(df)
elif draft_type == '2':  # Snake draft
    df = get_snake_value_data(conn)
    result = analyze_snake_draft(df)
