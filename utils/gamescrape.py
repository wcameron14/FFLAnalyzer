import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import logging
from time import sleep

# Initialize logging
logging.basicConfig(filename='gamescrape.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def scrape_game_ids():
    try:
        with open('game_ids.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Matchup', 'GameId'])
            
            season_type = 2
            current_year = datetime.now().year
            headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
            for year in range(2000, current_year + 1):
                total_weeks = 18 if year > 2020 else 17
                for week in range(1, total_weeks + 1):
                    url = f"https://www.espn.com/nfl/schedule/_/week/{week}/year/{year}/seasontype/{season_type}"
                    response = requests.get(url)
                    print(f"Status code for {url}: {response.status_code}")  # Debug print 1
                    print(response.text[:1000])  # Debug print 2: Print first 1000 characters of HTML
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Iterate through each date section
                    date_sections = soup.find_all('div', class_='Table__Title')
                    print(f"Found {len(date_sections)} date sections")  # Debug print 3
                    for date_section in date_sections:
                        date = date_section.text.strip()
                        print(f"Processing date: {date}")  # Debug print 4

                        # Get the corresponding table
                        table_body = date_section.find_next('tbody', class_='Table__TBODY')
                        for row in table_body.find_all('tr', class_='Table__TR'):
                            team1 = row.find('span', class_='Table__Team away').find('a', class_='AnchorLink').text
                            team2 = row.find('span', class_='Table__Team').find('a', class_='AnchorLink').text
                            matchup = f"{team1} @ {team2}"
                            print(f"Matchup: {matchup}")  # Debug print 5
                            print(f"Game URL: {game_url}")  # Debug print 6
                            game_url = row.find('a', class_='AnchorLink', href=True)['href']
                            if 'gameId' in game_url:
                                game_id = game_url.split('gameId=')[1]
                                writer.writerow([date, matchup, game_id])
                                logging.info(f'Saved gameId: {game_id} for {date} - {matchup}')
        sleep(5)  # Delay of 5 seconds between requests
    except Exception as e:
        logging.error(f'An error occurred: {e}')

# Call the function to start scraping
scrape_game_ids()
