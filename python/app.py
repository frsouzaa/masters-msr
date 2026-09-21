import dotenv
from commits import get_commits
from trends import get_trends
from parse import parse_file
from ewma import ewma
from plot import plot

config = dotenv.dotenv_values()
OUTPUT_DIR = "outputs"
FEATURES = [
    {"key": "commits"},
    {"key": "forks"},
    {
        "key": "created_issues",
        "perDayFile": f"{OUTPUT_DIR}/issuesPerDay.csv",
        "date": "created_at",
    },
    {
        "key": "closed_issues",
        "perDayFile": f"{OUTPUT_DIR}/issuesPerDay.csv",
        "date": "closed_at",
    },
    {
        "key": "created_pulls",
        "perDayFile": f"{OUTPUT_DIR}/pullsPerDay.csv",
        "date": "created_at",
    },
    {
        "key": "closed_pulls",
        "perDayFile": f"{OUTPUT_DIR}/pullsPerDay.csv",
        "date": "closed_at",
    },
    {
        "key": "merged_pulls",
        "perDayFile": f"{OUTPUT_DIR}/pullsPerDay.csv",
        "date": "merged_at",
    },
    {"key": "stars"},
    {"key": "interest"},
]
REPO_NAME = config.get("REPO_URL").strip("/").split("/")[-1]

get_commits(f"{OUTPUT_DIR}/commitsPerDay.csv", config.get("REPO_URL"))
get_trends(f"{OUTPUT_DIR}/interestPerDay.csv", REPO_NAME)

for feature in FEATURES:
    key = feature["key"]
    per_day = feature.get("perDayFile", f"{OUTPUT_DIR}/{key}PerDay.csv")
    date = feature.get("date", "date")

    final = f"{OUTPUT_DIR}/{key}Final.csv"
    ewmas = f"{OUTPUT_DIR}/{key}EMA.csv"
    svg = f"{OUTPUT_DIR}/{key}.svg"

    parse_file(
        per_day,
        final,
        date,
        "MONTHLY",
    )
    ewma(final, ewmas)
    plot(ewmas, svg, date, key, REPO_NAME)
