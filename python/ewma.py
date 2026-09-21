import pandas as pd


def ewma(input_file, output_file):
    df = pd.read_csv(input_file)

    df["ema6"] = df["count"].ewm(span=6).mean()
    df["ema12"] = df["count"].ewm(span=12).mean()
    df["ema24"] = df["count"].ewm(span=24).mean()
    df["ema48"] = df["count"].ewm(span=48).mean()

    df.to_csv(output_file, index=False)
