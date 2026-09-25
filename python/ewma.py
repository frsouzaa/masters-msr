import pandas as pd


def ewma(input_file, output_file, main_column):
    df = pd.read_csv(input_file)

    df["ema6"] = df[main_column].ewm(span=6).mean()
    df["ema12"] = df[main_column].ewm(span=12).mean()
    df["ema24"] = df[main_column].ewm(span=24).mean()
    df["ema48"] = df[main_column].ewm(span=48).mean()

    df.to_csv(output_file, index=False)
