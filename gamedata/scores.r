# Installation and Loading of Packages
install.packages("DBI")
install.packages("RPostgreSQL")
install.packages("ffscrapr")
library(ffscrapr)
library(DBI)
library(RPostgreSQL)

# Connect to PostgreSQL database
con <- dbConnect(PostgreSQL(), dbname = Sys.getenv("GAMEDATA_DB"),
                 host = Sys.getenv("GAMEDATA_HOST"), port = Sys.getenv("GAMEDATA_PORT"),
                 user = Sys.getenv("GAMEDATA_USER"), password = Sys.getenv("GAMEDATA_PW"))

# Function to create table based on data frame
create_table_from_df <- function(con, table_name, df) {
  fields <- paste0(names(df), " TEXT", collapse = ", ")
  query <- paste0("CREATE TABLE IF NOT EXISTS ", table_name, " (", fields, ");")
  dbExecute(con, query)
}

# Check if table exists and create if not
table_name <- "player_scores"
table_exists <- dbExistsTable(con, table_name)
if (!table_exists) {
  # Placeholder DataFrame creation for table structure - Adjust as necessary
  # This is just a placeholder. You need to replace it with actual data fetching
  placeholder_df <- data.frame(player_id = character(), score = numeric(), stringsAsFactors = FALSE)
  create_table_from_df(con, table_name, placeholder_df)
}

# Connect to Your League on the "sleeper" platform
conn <- ff_connect(platform = "sleeper", league_id = "997510104398315520")

# Fetch Player Scores for the 2023 season
# Note: Ensure 'scoring_settings' variable is defined or fetched before this step
# This is a placeholder for fetching scoring settings. Replace or ensure it's defined.
scoring_settings <- list() # Placeholder, define this based on your needs
player_scores <- ff_player_scores(conn, scoring = scoring_settings, season = 2023)

# Assuming 'player_scores' is the DataFrame with the data you want to insert
# Ensure the structure of 'player_scores' matches the table structure
if (!table_exists) {
  create_table_from_df(con, table_name, player_scores)
}

# Insert data into the database
dbWriteTable(con, table_name, player_scores, append = TRUE, row.names = FALSE, overwrite = FALSE)

# Note: This script assumes that 'player_scores' DataFrame structure matches the database table structure.
# You might need to adjust the 'create_table_from_df' function or the 'player_scores' DataFrame accordingly.