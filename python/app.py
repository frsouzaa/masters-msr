import sys
from src.commits import get_commits
from src.trends import get_trends
from src.parse import parse_file
from src.ewma import ewma, calculate_trend
from src.plot import plot_ema, plot_correlation_matrix
from src.merge import merge_features
from src.statistic import (
    anderson_darling,
    correlation,
    merge_correlation_by_anderson_darling,
)
from src.pipeline import get_pipeline

REPO_URL = sys.argv[-1]
REPO_NAME = REPO_URL.strip("/").split("/")[-1]

BASE_OUTPUT = "outputs"
OUTPUT_DIR = f"{BASE_OUTPUT}/{REPO_NAME}"
PERIOD = "MONTHLY"  # DAILY | MONTHLY

MERGED_FILE = f"{OUTPUT_DIR}/merged_features.csv"
ANDERSON_DARLING_FILE = f"{OUTPUT_DIR}/anderson_darling_test.csv"
CORRELATION_FINAL_FILE = f"{OUTPUT_DIR}/correlation_final.csv"

FEATURES_PIPELINE = get_pipeline(OUTPUT_DIR)

get_commits(
    [f["perDayFile"] for f in FEATURES_PIPELINE if f["id"] == "commits"][0], REPO_URL
)
get_trends(
    [f["perDayFile"] for f in FEATURES_PIPELINE if f["id"] == "interest"][0], REPO_NAME
)

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

merge_correlation_by_anderson_darling(
    spearman_file, pearson_file, ANDERSON_DARLING_FILE, CORRELATION_FINAL_FILE
)

plot_correlation_matrix(
    CORRELATION_FINAL_FILE,
    f"{OUTPUT_DIR}/plot_correlation_final_{REPO_NAME.replace("-", "_")}.svg",
)

calculate_trend(FEATURES_PIPELINE, f"{OUTPUT_DIR}/merged_ema.csv")
