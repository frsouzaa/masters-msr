import dotenv
from commits import get_commits
from trends import get_trends
from parse import parse_file
from ewma import ewma
from plot import plot
from merge import merge_features
from correlation import calculate_correlation

config = dotenv.dotenv_values()

REPO_NAME = config.get("REPO_URL").strip("/").split("/")[-1]

OUTPUT_DIR = "outputs"
PERIOD = "MONTHLY"  # DAILY | MONTHLY

PER_DAY_COMMITS_FILE = f"{OUTPUT_DIR}/per_day_commits.csv"
PER_DAY_FORKS_FILE = f"{OUTPUT_DIR}/per_day_forks.csv"
PER_DAY_ISSUES_FILE = f"{OUTPUT_DIR}/per_day_issues.csv"
PER_DAY_PULLS_FILE = f"{OUTPUT_DIR}/per_day_pulls.csv"
PER_DAY_STARS_FILE = f"{OUTPUT_DIR}/per_day_stars.csv"
PER_DAY_INTEREST_FILE = f"{OUTPUT_DIR}/per_day_interest.csv"

MERGED_FILE = f"{OUTPUT_DIR}/merged_features.csv"

FEATURES = [
    {
        "id": "commits",
        "perDayFile": PER_DAY_COMMITS_FILE,
    },
    {
        "id": "commited_by",
        "perDayFile": PER_DAY_COMMITS_FILE,
        "main": "author_name",
        "mode": "AGG",
    },
    {
        "id": "forks",
        "perDayFile": PER_DAY_FORKS_FILE,
    },
    {
        "id": "created_issues",
        "perDayFile": PER_DAY_ISSUES_FILE,
        "date": "created_at",
    },
    {
        "id": "closed_issues",
        "perDayFile": PER_DAY_ISSUES_FILE,
        "date": "closed_at",
    },
    {
        "id": "issues_created_by",
        "perDayFile": PER_DAY_ISSUES_FILE,
        "date": "created_at",
        "main": "created_by",
        "mode": "AGG",
    },
    {
        "id": "issues_closed_by",
        "perDayFile": PER_DAY_ISSUES_FILE,
        "date": "closed_at",
        "main": "closed_by",
        "mode": "AGG",
    },
    {
        "id": "created_pulls",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "created_at",
    },
    {
        "id": "closed_pulls",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "closed_at",
    },
    {
        "id": "merged_pulls",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "merged_at",
    },
    {
        "id": "pulls_created_by",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "created_at",
        "main": "created_by",
        "mode": "AGG",
    },
    {
        "id": "pulls_closed_by",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "closed_at",
        "main": "closed_by",
        "mode": "AGG",
    },
    {
        "id": "pulls_merged_by",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "merged_at",
        "main": "merged_by",
        "mode": "AGG",
    },
    {"id": "stars", "perDayFile": PER_DAY_STARS_FILE},
    {"id": "interest", "perDayFile": PER_DAY_INTEREST_FILE},
]

for feature in FEATURES:
    feature["finalFile"] = f"{OUTPUT_DIR}/final_{feature["id"]}.csv"
    feature["emaFile"] = f"{OUTPUT_DIR}/ema_{feature["id"]}.csv"
    feature["svgFile"] = f"{OUTPUT_DIR}/plot_{feature["id"]}.svg"

get_commits(PER_DAY_COMMITS_FILE, config.get("REPO_URL"))
get_trends(PER_DAY_INTEREST_FILE, REPO_NAME)

for feature in FEATURES:
    date = feature.get("date", "date")
    mode = feature.get("mode", "SUM")

    parse_file(feature["perDayFile"], feature["finalFile"], date, feature.get("main", "count"), PERIOD, mode, only_full_months=True)
    ewma(feature["finalFile"], feature["emaFile"])
    plot(
        feature["emaFile"],
        feature["svgFile"],
        feature["id"].replace("_", " ").title(),
        REPO_NAME,
    )

merge_features(FEATURES, MERGED_FILE)

calculate_correlation(MERGED_FILE)
