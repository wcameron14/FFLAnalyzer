import pandas as pd
import os
from sqlalchemy import create_engine, update
from dotenv import load_dotenv
from app.database.models import Players
from sqlalchemy.orm import sessionmaker
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

# Initialize the database
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Read the CSV into a DataFrame
df = pd.read_csv('player_ids.csv')

# To hold unmatched SleeperIDs
unmatched_ids = []

# Loop through the DataFrame and update the players table
for index, row in df.iterrows():
    if not pd.isna(row['sleeper_id']):
        sleeper_id = str(int(row['sleeper_id']))
    else:
        sleeper_id = None

    mfl_id = row['mfl_id']

    # Format the mfl_id
    formatted_gamedata_id = f"00-{str(mfl_id).zfill(7)}"

    # Update the gamedata_id field in the players table where player_id matches SleeperID
    stmt = update(Players).where(Players.player_id == sleeper_id).values(gamedata_id=mfl_id)
    result = session.execute(stmt)

    # Check if any row was updated, if not add the SleeperID to unmatched_ids
    if result.rowcount == 0:
        unmatched_ids.append(sleeper_id)

# Commit the transaction
session.commit()

# Log the unmatched SleeperIDs
if unmatched_ids:
    logging.info(f"Unmatched SleeperIDs: {unmatched_ids}")
else:
    logging.info("All records matched and updated successfully.")

print('Done!')