from datetime import datetime
import pandas as pd

TYPE = "commits"
PERIOD = "MONTHLY" # DAILY | MONTHLY
INPUT = f"outputs/{TYPE}PerDay.csv"
OUTPUT = f"outputs/{TYPE}Final.csv"

df = pd.read_csv(INPUT)

df = df.groupby("date")["count"].sum().reset_index()

if PERIOD == "DAILY":
    pattern = "%Y-%m-%d"
    offset = pd.DateOffset(days=1)
if PERIOD == "MONTHLY":
    pattern = "%Y-%m"
    offset = pd.DateOffset(months=1)
    df = df.groupby(df["date"].str[:7])["count"].sum().reset_index()

minDate = datetime.strptime(df["date"].agg("min"), pattern)
maxDate = datetime.strptime(df["date"].agg("max"), pattern)
df["summation"] = None
summation = 0

while minDate <= maxDate:
    if not df[df["date"] == minDate.strftime(pattern)].any().any():
        df = pd.concat([df, pd.DataFrame([[minDate.strftime(pattern), 0, summation]], columns=["date", "count", "summation"])])
    else:
        summation += df.loc[df["date"] == minDate.strftime(pattern), "count"].values[0]
        df.loc[df["date"] == minDate.strftime(pattern), "summation"] = summation
    minDate = minDate + offset

df = df.sort_values(by="date").reset_index(drop=True)

df.to_csv(OUTPUT, index=False)
