library(nflfastR)
library(RPostgreSQL)

load_year_data <- function(year) {
  pg_conn <- dbConnect(PostgreSQL(), host="localhost", port="5433", user="gamedata", password="your_password", dbname="gamedata")
  table_name <- paste0("nfl_data_", year)

  # Check if the table exists
  if (dbExistsTable(pg_conn, table_name)) {
    print(paste0("Table '", table_name, "' already exists. Skipping loading."))
    return()
  }

  # Load play-by-play data
  nfl_data <- load_pbp(year)

  # Write the data to the table
  dbWriteTable(pg_conn, table_name, nfl_data)
  print(paste0("Data for year ", year, " loaded successfully."))
}

# Example usage
load_year_data(2018)
