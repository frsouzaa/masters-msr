from src.parse import pre_parse_pulls_closed


def get_pipeline(output_dir):
    PER_DAY_COMMITS_FILE = f"{output_dir}/per_day_commits.csv"
    PER_DAY_FORKS_FILE = f"{output_dir}/per_day_forks.csv"
    PER_DAY_ISSUES_FILE = f"{output_dir}/per_day_issues.csv"
    PER_DAY_PULLS_FILE = f"{output_dir}/per_day_pulls.csv"
    PER_DAY_STARS_FILE = f"{output_dir}/per_day_stars.csv"
    PER_DAY_INTEREST_FILE = f"{output_dir}/per_day_interest.csv"
    PER_DAY_CLOSED_PULLS_FILE = f"{output_dir}/per_day_closed_pulls.csv"

    features_pipeline = [
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
            },
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
        {
            "id": "forks",
            "perDayFile": PER_DAY_FORKS_FILE,
        },
        {"id": "interest", "perDayFile": PER_DAY_INTEREST_FILE},
    ]

    for feature in features_pipeline:
        feature["finalFile"] = f"{output_dir}/final_{feature["id"]}.csv"
        feature["emaFile"] = f"{output_dir}/ema_{feature["id"]}.csv"
        feature["svgFile"] = f"{output_dir}/plot_{feature["id"]}.svg"

    return features_pipeline
