from datetime import datetime
import pandas as pd


def parse_file(input_file, output_file, date_column, main_column, period, mode):
    df = pd.read_csv(input_file)

    if mode == "SUM":
        df = df.groupby(date_column)[main_column].sum().reset_index()
    if mode == "AGG":
        df = df.groupby(date_column).agg({main_column: "nunique"}).reset_index()

    if period == "DAILY":
        pattern = "%Y-%m-%d"
        offset = pd.DateOffset(days=1)
    if period == "MONTHLY":
        pattern = "%Y-%m"
        offset = pd.DateOffset(months=1)
        df = df.groupby(df[date_column].str[:7])[main_column].sum().reset_index()

    minDate = datetime.strptime(df[date_column].agg("min"), pattern)
    # maxDate = datetime.strptime(df[date_column].agg("max"), pattern)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    df["summation"] = None
    summation = 0

    while (
        minDate <= today
    ):  # the limit is today because if a project data ends one year ago (for exemple) it can mess up with the EMA analysis, so we complete the data with zero values
        if not df[df[date_column] == minDate.strftime(pattern)].any().any():
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [[minDate.strftime(pattern), 0, summation]],
                        columns=[date_column, main_column, "summation"],
                    ),
                ]
            )
        else:
            summation += df.loc[
                df[date_column] == minDate.strftime(pattern), main_column
            ].values[0]
            df.loc[df[date_column] == minDate.strftime(pattern), "summation"] = (
                summation
            )
        minDate = minDate + offset

    df.sort_values(by=date_column).reset_index(drop=True).to_csv(
        output_file, index=False
    )


if __name__ == "__main__":
    FEATURE = "issues"
    DATE_COLUMN = "created_at"
    MAIN_COLUMN = "count"
    PERIOD = "MONTHLY"
    MODE = "SUM"
    OUTPUT_DIR = "outputs"
    INPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}PerDay.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}Final.csv"
    parse_file(INPUT_FILE, OUTPUT_FILE, DATE_COLUMN, MAIN_COLUMN, PERIOD, MODE)
