install.packages("DBI")
install.packages("RPostgreSQL")
install.packages("nflreadr")
library(DBI)
library(nflreadr)
library(RPostgreSQL)

# Connect to PostgreSQL database
con <- dbConnect(PostgreSQL(), dbname = Sys.getenv("GAMEDATA_DB"),
                 host = Sys.getenv("GAMEDATA_HOST"), port = Sys.getenv("GAMEDATA_PORT"),
                 user = Sys.getenv("GAMEDATA_USER"), password = Sys.getenv("GAMEDATA_PW"))

# Function to create table based on data frame
create_table_from_df <- function(con, table_name, df) {
  fields <- paste0(names(df), " TEXT", collapse = ", ")
  query <- paste0("CREATE TABLE ", table_name, "(", fields, ");")
  dbExecute(con, query)
}

# Check if table exists
table_name <- "player_game_stats"
table_exists <- dbExistsTable(con, table_name)

# Loop through the years and pull data
for(year in 2000:2023) {
  print(paste("Fetching data for year:", year))
  
  # Fetch player stats
  stats_data <- load_player_stats(year)

  # Fetch kicking stats
  kicking_data <- nflreadr::load_player_stats(year, stat_type = 'kicking')

  # Merge player stats and kicking stats
  merged_data <- merge(stats_data, kicking_data, by = "player_id", all = TRUE)
  
    # Create table if it doesn't exist
  if (!table_exists) {
    create_table_from_df(con, table_name, stats_data)
    table_exists <- TRUE
  }
  # Insert into PostgreSQL database
  dbWriteTable(con, name='player_game_stats', value=merged_data, append=TRUE, row.names=FALSE)
}

# Disconnect from the database
dbDisconnect(con)

print("Player game stats loaded successfully.")
