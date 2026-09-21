from datetime import datetime
import pandas as pd


def parse_file(input_file, output_file, date_column, period):
    df = pd.read_csv(input_file)

    df = df.groupby(date_column)["count"].sum().reset_index()

    if period == "DAILY":
        pattern = "%Y-%m-%d"
        offset = pd.DateOffset(days=1)
    if period == "MONTHLY":
        pattern = "%Y-%m"
        offset = pd.DateOffset(months=1)
        df = df.groupby(df[date_column].str[:7])["count"].sum().reset_index()

    minDate = datetime.strptime(df[date_column].agg("min"), pattern)
    maxDate = datetime.strptime(df[date_column].agg("max"), pattern)
    df["summation"] = None
    summation = 0

    while minDate <= maxDate:
        if not df[df[date_column] == minDate.strftime(pattern)].any().any():
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [[minDate.strftime(pattern), 0, summation]],
                        columns=[date_column, "count", "summation"],
                    ),
                ]
            )
        else:
            summation += df.loc[
                df[date_column] == minDate.strftime(pattern), "count"
            ].values[0]
            df.loc[df[date_column] == minDate.strftime(pattern), "summation"] = (
                summation
            )
        minDate = minDate + offset

    df.sort_values(by=date_column).reset_index(drop=True).to_csv(
        output_file, index=False
    )
