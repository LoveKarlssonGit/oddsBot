import pandas as pd

pd.set_option('display.max_columns', None)
matches = pd.read_csv("premier_league_matches12.csv", index_col=0)

print(matches.head())
#matches.drop_duplicates()