from pydriller import Repository, Commit
from datetime import datetime
import pandas as pd

REPO_URL = "https://github.com/react/react"

commit: Commit
# since: datetime = datetime(
#     2020, 1, 1
# )

commits = [
    [
        commit.author.name,
        commit.committer,
        commit.hash,
        commit.committer_date.strftime("%Y-%m"),
        commit.project_name,
        # commit.deletions,
        # commit.insertions,
        # commit.msg,
        # commit.branches
        1
    ]
    for commit in Repository(
        REPO_URL, include_refs=True
    ).traverse_commits()
]

df = pd.DataFrame(commits, columns=["Author", "Committer", "Hash", "Committer Date", "Project Name", "Count"])

# df.to_csv("commits.csv", index=False)

df = df.groupby("Committer Date")["Count"].sum().reset_index()

minDate = datetime.strptime(df["Committer Date"].agg("min"), "%Y-%m")
today = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

while minDate < today:
    if not df[df["Committer Date"] == minDate.strftime("%Y-%m")].any().any():
        df = pd.concat([df, pd.DataFrame([[minDate.strftime("%Y-%m"), 0]], columns=["Committer Date", "Count"])])
        df = df.sort_index()
    minDate = minDate + pd.DateOffset(months=1)

df.to_csv("commits_by_date.csv", index=False)
