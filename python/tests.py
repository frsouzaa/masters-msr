import pandas as pd


df = pd.read_csv("outputs/per_day_pulls.csv")

diferentes = 0

for row in df.iloc:
    if row["merged_by"] != row["closed_by"] and type(row["merged_by"]) == str and type(row["closed_by"]) == str:
        diferentes += 1

print(f"Total de PRs com merged_by diferente de closed_by: {diferentes}")
