from pydriller import Repository, Commit
import pandas as pd

REPO_URL = "https://github.com/rails/rails"

commit: Commit
# since: datetime = datetime(
#     2020, 1, 1
# )

commits = [
    [
        commit.author.email,
        commit.hash,
        commit.committer_date.strftime("%Y-%m-%d"),
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

df = pd.DataFrame(commits, columns=["author_email", "hash", "date", "count"])

df.to_csv("outputs/commitsPerDay.csv", index=False)
