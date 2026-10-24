import pandas as pd


def ewma(input_file, output_file, main_column="count"):
    df = pd.read_csv(input_file)

    df["short_ema"] = df[main_column].ewm(alpha=0.16).mean()
    df["long_ema"] = df[main_column].ewm(alpha=0.08).mean()

    df.to_csv(output_file, index=False)


def calculate_trend(features, output_file):
    colunas = ["feature", "short_ema", "long_ema", "status"]
    merged_df = pd.DataFrame(columns=colunas)

    for feature in features:
        try:
            df = pd.read_csv(feature["emaFile"])
            short_ema = df.iloc[-1]["short_ema"]
            long_ema = df.iloc[-1]["long_ema"]
            status = None
            if short_ema == long_ema:
                status = "stable"
            if short_ema > long_ema:
                status = "uptrend"
            if short_ema < long_ema:
                status = "downtrend"
            merged_df = pd.concat(
                [
                    merged_df,
                    pd.DataFrame(
                        [[feature["id"], short_ema, long_ema, status]],
                        columns=colunas,
                    ),
                ]
            )
        except Exception as e:
            print(f"Error reading {feature["emaFile"]}: {e}")
            continue

    merged_df.to_csv(output_file, index=False)
