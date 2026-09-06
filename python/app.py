from pydriller import Repository, Commit
from datetime import datetime
import pandas as pd

commit: Commit
since: datetime = datetime(
    2020, 1, 1
)

commits = [
    [
        commit.author.name,
        commit.committer,
        commit.hash,
        commit.committer_date.strftime("%Y-%m-%d"),
        commit.project_name,
        # commit.deletions,
        # commit.insertions,
        # commit.msg,
        # commit.branches
        1
    ]
    for commit in Repository(
        "https://github.com/pandas-dev/pandas", since=since, include_refs=True
    ).traverse_commits()
]

df = pd.DataFrame(commits, columns=["Author", "Committer", "Hash", "Committer Date", "Project Name", "Count"])

df.to_csv("commits.csv", index=False)

df.groupby("Committer Date")["Count"].sum().reset_index().to_csv("commits_by_date.csv", index=False)
