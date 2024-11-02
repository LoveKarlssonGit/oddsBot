from io import StringIO

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import time


# standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
#
# data = requests.get(standings_url)
#
# soup = BeautifulSoup(data.text, "html.parser")
# standings_table = soup.select('table.stats_table')[0]
# links = standings_table.find_all('a')
# links = [l.get("href") for l in links]
# links = [l for l in links if '/squads/' in l]
#
#
# team_urls = [f"https://fbref.com{l}" for l in links]
# team_url = team_urls[0]
# data = requests.get(team_url)
# data_io = StringIO(data.text)
#
# matches = pd.read_html(data_io, match="Scores & Fixtures")[0]
# #print(matches["Opponent"])
# #matches.info()
#
# soup = BeautifulSoup(data.text)
# links = soup.find_all('a')
# links = [l.get("href") for l in links]
# links = [l for l in links if l and 'all_comps/shooting/' in l]
# data = requests.get(f"https://fbref.com{links[0]}")
# shooting = pd.read_html(data.text, match="Shooting")[0]
# #shooting.info()
#
# shooting.columns = shooting.columns.droplevel()
# #print(shooting["Date"])
# team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
# # print(data.text)

years = list(range(2024, 2022, -1))


all_matches = []
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text, "html.parser")
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"

    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        time.sleep(12)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/keeper/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        goalkeeping = pd.read_html(data.text, match="Goalkeeping")[0]
        goalkeeping.columns = goalkeeping.columns.droplevel()
        time.sleep(12)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/passing/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        passing = pd.read_html(data.text, match="Passing")[0]
        passing.columns = passing.columns.droplevel()
        time.sleep(12)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/gca/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        gca = pd.read_html(data.text, match="Goal and Shot Creation")[0]
        gca.columns = gca.columns.droplevel()
        time.sleep(12)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/defense/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        defence = pd.read_html(data.text, match="Defensive Actions")[0]
        defence.columns = defence.columns.droplevel()
        time.sleep(12)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/misc/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        misc = pd.read_html(data.text, match="Miscellaneous Stats")[0]
        misc.columns = misc.columns.droplevel()
        time.sleep(12)
        try:
            # Start with the matches DataFrame
            team_data = matches
            # Merge shooting data
            team_data = team_data.merge(
                shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]],
                on="Date",
                how="left"
            )

            # Merge goalkeeping data
            team_data = team_data.merge(
                goalkeeping[["Date", "GA", "Saves", "CS", "PSxG"]],
                on="Date",
                how="left"
            )

            # Merge passing data
            team_data = team_data.merge(
                passing[["Date", "Cmp", "Att", "Cmp%", "PrgDist"]],
                on="Date",
                how="left"
            )

            # Merge goal creation (gca) data
            team_data = team_data.merge(
                gca[["Date", "SCA", "GCA"]],
                on="Date",
                how="left"
            )

            # Merge defense (defence) data
            team_data = team_data.merge(
                defence[["Date", "Tkl", "TklW", "Int", "Blocks"]],
                on="Date",
                how="left"
            )

            # Merge miscellaneous (misc) data
            team_data = team_data.merge(
                misc[["Date", "CrdY", "CrdR", "Fls", "Off"]],
                on="Date",
                how="left"
            )

        except ValueError:
            print(ValueError)
            continue
        team_data = team_data[team_data["Comp"] == "Premier League"]

        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)



match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
match_df = match_df[match_df.notes != "Head-to-Head"]
match_df.to_csv("premier_league_matches13.csv")

# Specify columns to merge for each stat (adjust as needed)
# merge_columns = {
#     'shooting': ["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt", "xGA"],
#     'goalkeeping': ["Date", "GA", "Saves", "CS", "PSxG"],  # Example columns for goalkeeping
#     'passing': ["Date", "Cmp", "Att", "Cmp%", "PrgDist"],  # Example columns for passing
#     'gca': ["Date", "SCA", "GCA"],  # Example columns for goal creation
#     'possession': ["Date", "Touches", "DribSucc", "Carries"],  # Example columns for possession
#     'defense': ["Date", "Tkl", "TklW", "Int", "Blocks"],  # Example columns for defense
#     'misc': ["Date", "CrdY", "CrdR", "Fls", "Off"]  # Example columns for miscellaneous
# }