import sys
from commits import get_commits
from trends import get_trends
from parse import parse_file, pre_parse_pulls_closed
from ewma import ewma
from plot import plot_ema, plot_correlation_matrix
from merge import merge_features
from statistic import anderson_darling, correlation, merge_correlation_by_anderson_darling

REPO_URL = sys.argv[-1]
REPO_NAME = REPO_URL.strip("/").split("/")[-1]

OUTPUT_DIR = f"outputs/{REPO_NAME}"
PERIOD = "MONTHLY"  # DAILY | MONTHLY

PER_DAY_COMMITS_FILE = f"{OUTPUT_DIR}/per_day_commits.csv"
PER_DAY_FORKS_FILE = f"{OUTPUT_DIR}/per_day_forks.csv"
PER_DAY_ISSUES_FILE = f"{OUTPUT_DIR}/per_day_issues.csv"
PER_DAY_PULLS_FILE = f"{OUTPUT_DIR}/per_day_pulls.csv"
PER_DAY_STARS_FILE = f"{OUTPUT_DIR}/per_day_stars.csv"
PER_DAY_INTEREST_FILE = f"{OUTPUT_DIR}/per_day_interest.csv"
PER_DAY_CLOSED_PULLS_FILE = f"{OUTPUT_DIR}/per_day_closed_pulls.csv"

MERGED_FILE = f"{OUTPUT_DIR}/merged_features.csv"
ANDERSON_DARLING_FILE = f"{OUTPUT_DIR}/anderson_darling_test.csv"
CORRELATION_FINAL_FILE = f"{OUTPUT_DIR}/correlation_final.csv"

FEATURES_PIPELINE = [
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
        "id": "issues_created",
        "perDayFile": PER_DAY_ISSUES_FILE,
        "date": "created_at",
    },
    {
        "id": "issues_closed",
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
        "id": "pulls_created",
        "perDayFile": PER_DAY_PULLS_FILE,
        "date": "created_at",
    },
    {
        "id": "pulls_closed",
        "perDayFile": PER_DAY_CLOSED_PULLS_FILE,
        "date": "closed_at",
        "pre_parse_func": pre_parse_pulls_closed,
        "pre_parse_kwargs": {
            "input_file": PER_DAY_PULLS_FILE,
            "output_file": PER_DAY_CLOSED_PULLS_FILE,
            "closed_column": "closed_at",
            "merged_column": "merged_at",
        }
    },
    {
        "id": "pulls_merged",
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
        "perDayFile": PER_DAY_CLOSED_PULLS_FILE,
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

for feature in FEATURES_PIPELINE:
    feature["finalFile"] = f"{OUTPUT_DIR}/final_{feature["id"]}.csv"
    feature["emaFile"] = f"{OUTPUT_DIR}/ema_{feature["id"]}.csv"
    feature["svgFile"] = f"{OUTPUT_DIR}/plot_{feature["id"]}.svg"

get_commits(PER_DAY_COMMITS_FILE, REPO_URL)
get_trends(PER_DAY_INTEREST_FILE, REPO_NAME)

for feature in FEATURES_PIPELINE:
    date = feature.get("date", "date")
    mode = feature.get("mode", "SUM")

    try:
        if "pre_parse_func" in feature:
            feature["pre_parse_func"](**feature.get("pre_parse_kwargs", {}))
        parse_file(
            feature["perDayFile"],
            feature["finalFile"],
            date,
            feature.get("main", "count"),
            PERIOD,
            mode,
            only_full_months=True,
        )
    except Exception as e:
        print(f"Error parsing {feature["perDayFile"]}: {e}")
        continue
    ewma(feature["finalFile"], feature["emaFile"])
    plot_ema(
        feature["emaFile"],
        feature["svgFile"],
        feature["id"].replace("_", " ").title(),
        REPO_NAME,
    )

merge_features(FEATURES_PIPELINE, MERGED_FILE)

anderson_darling(MERGED_FILE, ANDERSON_DARLING_FILE)

spearman_file, pearson_file = correlation(MERGED_FILE, OUTPUT_DIR)

merge_correlation_by_anderson_darling(spearman_file, pearson_file, ANDERSON_DARLING_FILE, CORRELATION_FINAL_FILE)

plot_correlation_matrix(CORRELATION_FINAL_FILE, f"{OUTPUT_DIR}/plot_correlation_final_{REPO_NAME.replace("-", "_")}.svg")
