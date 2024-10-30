from datetime import datetime

import pandas
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score

pd.set_option('display.max_columns', None)

matches = pd.read_csv("premier_league_matches.csv", index_col=0)

#print(matches.dtypes)
matches["date"] = pd.to_datetime(matches["date"])
matches["venue_code"] = matches["venue"].astype("category").cat.codes

matches["opp_code"] = matches["opponent"].astype("category").cat.codes
matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")
matches["day_code"] = matches["date"].dt.dayofweek
matches["target"] = (matches["result"] == "W").astype("int")

rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
train = matches[matches["date"] < '2024-01-01']
test = matches[matches["date"] > '2024-01-01']
predictors = ["venue_code", "opp_code", "hour", "day_code"]
rf.fit(train[predictors], train["target"])

preds = rf.predict(test[predictors])
acc = accuracy_score(test["target"], preds)
#print(acc)

#This part is for checking how often we where correct vs incorrect in our predictions
combined = pd.DataFrame(dict(actual=test["target"], prediction=preds))
#print(pd.crosstab(index=combined["actual"], columns=combined["prediction"]))

#How often we where correct in guessing which team was going to win
#print(precision_score(test["target"], preds))

#Create a dataframe for every squad in our data
grouped_matches = matches.groupby("team")

group = grouped_matches.get_group("Manchester City")

#Computes rolling averages to calculate form of team, if they lost the last 3 games it's most likely they will lose again because of bad form...
def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group

cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]

matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols,new_cols))
matches_rolling = matches_rolling.droplevel('team')

matches_rolling.index = range(matches_rolling.shape[0])

def make_predictions(data, predictors):
    train_start = '2024-08-01'
    train_end = '2024-10-01'
    test_start = '2024-10-02'
    today = datetime.today().strftime('%Y-%m-%d')  # Get today's date as a string

    # Filter for the train and test sets based on date range
    train = data[(data['date'] >= train_start) & (data['date'] <= train_end)]
    test = data[(data['date'] >= test_start) & (data['date'] <= today)]
    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual=test["target"], predicted=preds), index=test.index)
    error = precision_score(test["target"], preds)
    return combined, error

combined, error = make_predictions(matches_rolling, predictors + new_cols)


combined = combined.merge(matches_rolling[["date", "team", "opponent", "result"]], left_index=True, right_index=True)


class MissingDict(dict):
    __missing__ = lambda self, key: key

map_values = {"Brighton and Hove Albion": "Brighton", "Manchester United": "Manchester Utd", "Newcastle United": "Newcastle Utd", "Tottenham Hotspur": "Tottenham", "West Ham United": "West Ham", "Wolverhampton Wanderers": "Wolves"}
mapping = MissingDict(**map_values)

combined["new_team"] = combined["team"].map(mapping)
merged = combined.merge(combined, left_on=["date", "new_team"], right_on=["date", "opponent"])

print(merged[(merged["predicted_x"] == 1) & (merged["predicted_y"] ==0)]["actual_x"].value_counts())


