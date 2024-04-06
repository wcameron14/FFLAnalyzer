# Installation and Loading of Packages
install.packages("reticulate")
library(reticulate)
library(nflreadr)
library(ffscrapr)
library(DBI)
library(RPostgreSQL)

# Import Python module
leagues_py <- import("leagues")

# Get league IDs from Python script
league_ids <- leagues_py$get_league_ids()

# Connect to PostgreSQL database
con <- dbConnect(
  PostgreSQL(),
  dbname = Sys.getenv("GAMEDATA_DB"),
  host = Sys.getenv("GAMEDATA_HOST"),
  port = Sys.getenv("GAMEDATA_PORT"),
  user = Sys.getenv("GAMEDATA_USER"),
  password = Sys.getenv("GAMEDATA_PW")
)

# Function to create table based on data frame
create_table_from_df <- function(con, table_name, df) {
  fields <- paste0(names(df), " TEXT", collapse = ", ")
  query <- paste0("CREATE TABLE ", table_name, "(", fields, ");")
  dbExecute(con, query)
}

# Loop through the league IDs and pull data
for(league_id in league_ids) {
  print(paste("Fetching data for league ID:", league_id))
  
  # Connect to Your League on the "sleeper" platform
  conn <- ff_connect(platform = "sleeper", league_id = league_id)

  # Fetch Scoring History
  scoring_history <- ff_scoringhistory(conn, season = 1999:nflreadr::most_recent_season())

  # Define table name
  table_name <- paste0("scoring_history_", league_id)

  # Check if table exists
  table_exists <- dbExistsTable(con, table_name)

  # Create table if it doesn't exist
  if (!table_exists) {
    create_table_from_df(con, table_name, scoring_history)
  }

  # Insert into PostgreSQL database
  dbWriteTable(con, name=table_name, value=scoring_history, append=TRUE, row.names=FALSE)
}

# Disconnect from the database
dbDisconnect(con)

print("Scoring history loaded successfully.")