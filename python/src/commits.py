from pydriller import Repository
import pandas as pd


def get_commits(output_file, repo_url):
    commits = [
        [
            commit.author.name,
            commit.author.email,
            commit.hash,
            commit.committer_date.strftime("%Y-%m-%d"),
            1,
        ]
        for commit in Repository(repo_url, include_refs=True).traverse_commits()
    ]

    pd.DataFrame(commits, columns=["author_name", "author_email", "hash", "date", "count"]).to_csv(
        output_file, index=False
    )

if __name__ == "__main__":
    OUTPUT_FILE = "outputs/commitsPerDay.csv"
    REPO_URL = "https://github.com/junit-team/junit4"
    get_commits(OUTPUT_FILE, REPO_URL)
