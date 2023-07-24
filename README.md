# Fantasy Football League Analyzer

This Python application collects data from the Sleeper API and stores it in a PostgreSQL database. The purpose of this application is to assist users in understanding patterns in fantasy football league data, specifically regarding manager behavior, player performance, and roster construction.

## Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed Python 3.7 or later.
* You have installed PostgreSQL.
* You have a Sleeper account and have access to the league ID and your username.

## Installation

1. Clone this repository to your local machine.
2. Install the required Python libraries by running `pip install -r requirements.txt` in your terminal.

## Configuration

1. Copy the `.env template` file in the root directory, rename it to `.env`, and update the environment variables with your own values. This includes:

    * `POSTGRES_USER`: Your PostgreSQL username.
    * `POSTGRES_PW`: Your PostgreSQL password.
    * `POSTGRES_DB`: Your PostgreSQL database name.
    * `LEAGUE_ID`: Your Sleeper league ID.
    * `SLEEPER_USERNAME`: Your Sleeper username.

2. Ensure that your PostgreSQL server is running and that the database specified in your `.env` file exists.

## Usage

Run `main.py` in your terminal to start the data collection process. The application will fetch data from the Sleeper API and insert it into the PostgreSQL database. The database schema includes the following tables:

* `Users`: Contains information about users in the leagues.
* `Players`: Contains information about players in the leagues.
* `Leagues`: Contains information about the leagues.
* `League_Owners`: Contains information about league ownership.
* `Rosters`: Contains information about rosters in the leagues.
* `Matchups`: Contains information about matchups in the leagues.
* `Transactions`: Contains information about transactions (trades and waivers) in the leagues.
* `League_Settings`: Contains league settings.

Error handling is built into each step of the data collection process. If an error occurs while fetching or inserting data, the application will log the error and continue with the next piece of data. If you encounter any problematic leagues that cause errors, you can exclude them from the data collection process by adding their IDs to the `problematic_league_ids` list in `api.py`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

Please feel free to reach out with any questions or comments. 

## Acknowledgements

Thanks to the team at Sleeper for providing the API that makes this project possible. 
