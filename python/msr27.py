import os
import pandas as pd
from src.pipeline import get_pipeline
from itertools import combinations

INPUT_FOLDER = "outputs"

directory = os.fsencode(INPUT_FOLDER)

features_pipeline = get_pipeline(INPUT_FOLDER)

pairs = list(combinations([f["id"] for f in features_pipeline], 2))

results_high = dict()
results_moderate = dict()
results_low = dict()

high = 0
high_repo = None
low = 1
low_repo = None

for file in os.listdir(directory):
    filename = os.fsdecode(file)

    df = pd.read_csv(f"{INPUT_FOLDER}/{filename}/correlation_final.csv", index_col=0)

    for pair in pairs:
        if abs(df[pair[0]][pair[1]]) > 0.7:
            results_high[f"{pair[0]} x {pair[1]}"] = (
                results_high.get(f"{pair[0]} x {pair[1]}", 0) + 1
            )
            if pair[0] == "pulls_created" and pair[1] == "pulls_created_by" and df[pair[0]][pair[1]] > high:
                high = df[pair[0]][pair[1]]
                high_repo = filename
        elif abs(df[pair[0]][pair[1]]) < 0.3:
            results_low[f"{pair[0]} x {pair[1]}"] = (
                results_low.get(f"{pair[0]} x {pair[1]}", 0) + 1
            )
            if pair[0] == "pulls_created" and pair[1] == "pulls_created_by" and df[pair[0]][pair[1]] < low:
                low = df[pair[0]][pair[1]]
                low_repo = filename
        else:
            results_moderate[f"{pair[0]} x {pair[1]}"] = (
                results_moderate.get(f"{pair[0]} x {pair[1]}", 0) + 1
            )
            # print(f"{pair[0]} x {pair[1]} - {filename} - {df[pair[0]][pair[1]]}")

print(high)
print(high_repo)
print(low)
print(low_repo)
print("\n\nfeatures | high | moderate | low | high percentage | moderate percentage | low percentage")
print("\nhigh")
for pair in [i[0] for i in sorted(results_high.items(), key=lambda item: item[1], reverse=True)]:
    high = results_high.get(pair, 0)
    moderate = results_moderate.get(pair, 0)
    low = results_low.get(pair, 0)
    print(f"{pair: <37} | {high: <2} | {moderate: <2} | {low: <2} | {(high/30)*100:.2f}% | {(moderate/30)*100:.2f}% | {(low/30)*100:.2f}%")
print("\n\n")
for pair in [i[0] for i in sorted(results_moderate.items(), key=lambda item: item[1], reverse=True)]:
    high = results_high.get(pair, 0)
    moderate = results_moderate.get(pair, 0)
    low = results_low.get(pair, 0)
    print(f"{pair: <37} | {high: <2} | {moderate: <2} | {low: <2} | {(high/30)*100:.2f}% | {(moderate/30)*100:.2f}% | {(low/30)*100:.2f}%")
print("\n\n")
for pair in [i[0] for i in sorted(results_low.items(), key=lambda item: item[1], reverse=True)]:
    high = results_high.get(pair, 0)
    moderate = results_moderate.get(pair, 0)
    low = results_low.get(pair, 0)
    print(f"{pair: <37} | {high: <2} | {moderate: <2} | {low: <2} | {(high/30)*100:.2f}% | {(moderate/30)*100:.2f}% | {(low/30)*100:.2f}%")

pulls_created = 0
pulls_closed = 0
pulls_merged = 0

pulls_creators = []
pulls_closers = []
pulls_mergers = []

issues_created = 0
issues_closed = 0

issues_creators = []
issues_closers = []

commits = []
commit_authors = []

for file in os.listdir(directory):
    filename = os.fsdecode(file)

    per_day_pulls = pd.read_csv(f"{INPUT_FOLDER}/{filename}/per_day_pulls.csv")
    created_pulls = pd.read_csv(f"{INPUT_FOLDER}/{filename}/final_pulls_created.csv")
    closed_pulls = pd.read_csv(f"{INPUT_FOLDER}/{filename}/final_pulls_closed.csv")
    merged_pulls = pd.read_csv(f"{INPUT_FOLDER}/{filename}/final_pulls_merged.csv")
    
    pulls_created += created_pulls["summation"].tolist()[-1]
    pulls_closed += closed_pulls["summation"].tolist()[-1]
    pulls_merged += merged_pulls["summation"].tolist()[-1]
    
    pulls_creators = pulls_creators + per_day_pulls["created_by"].tolist()
    pulls_closers = pulls_closers + per_day_pulls["closed_by"].tolist()
    pulls_mergers = pulls_mergers + per_day_pulls["merged_by"].tolist()
    
    per_day_issues = pd.read_csv(f"{INPUT_FOLDER}/{filename}/per_day_issues.csv")
    created_issues = pd.read_csv(f"{INPUT_FOLDER}/{filename}/final_issues_created.csv")
    closed_issues = pd.read_csv(f"{INPUT_FOLDER}/{filename}/final_issues_closed.csv")
    
    issues_created += created_issues["summation"].tolist()[-1]
    issues_closed += closed_issues["summation"].tolist()[-1]
    
    issues_creators = issues_creators + per_day_issues["created_by"].tolist()
    issues_closers = issues_closers + per_day_issues["closed_by"].tolist()
    
    per_day_commits = pd.read_csv(f"{INPUT_FOLDER}/{filename}/per_day_commits.csv")
    
    commits = commits + per_day_commits["hash"].tolist()
    commit_authors = commit_authors + per_day_commits["author_name"].tolist()
    
print("\n\n")

print(f"Commits: {len(set(commits))}")
print(f"Commit Authors: {len(set(commit_authors))}")

print(f"Pull requests created: {pulls_created}")
print(f"Pull requests closed: {pulls_closed}")
print(f"Pull requests merged: {pulls_merged}")
print(f"Pull requests creators: {len(set(pulls_creators))}")
print(f"Pull requests closers: {len(set(pulls_closers))}")
print(f"Pull requests mergers: {len(set(pulls_mergers))}")

print(f"Issues created: {issues_created}")
print(f"Issues closed: {issues_closed}")
print(f"Issues creators: {len(set(issues_creators))}")
print(f"Issues closers: {len(set(issues_closers))}")


trends = dict()

for file in os.listdir(directory):
    filename = os.fsdecode(file)

    merged_ema = pd.read_csv(f"{INPUT_FOLDER}/{filename}/merged_ema.csv")
    
    for i in range(len(merged_ema)):
        feature = merged_ema.iloc[i]["feature"]
        status = merged_ema.iloc[i]["status"]
        if not trends.get(feature):
            trends[feature] = dict()
        trends[feature][status] = 1 + trends[feature].get(status, 0)

print("\n\nfeature           | uptrend | downtrend | stable")
for key, value in trends.items():
    print(f"{key: <17} |      {value.get("uptrend", 0):02d} |        {value.get("downtrend", 0):02d} | {value.get("stable", 0):02d}")
