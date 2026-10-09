import pandas as pd


def merge_features(features, output_file):
    merged_df = pd.DataFrame()

    for feature in features:
        try:
            df = pd.read_csv(feature["finalFile"])
        except Exception as e:
            print(f"Error reading {feature["finalFile"]}: {e}")
            continue
        df.drop(columns=["summation"], inplace=True)
        df.rename(columns={"count": f"{feature["id"]}"}, inplace=True)
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="date")

    merged_df.to_csv(output_file, index=False)
