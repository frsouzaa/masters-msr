import pandas as pd
import matplotlib.pyplot as plt

TYPE = "commits"
INPUT = f"outputs/{TYPE}FinalEMA.csv"
OUTPUT = f"outputs/{TYPE}EMA.svg"

def plot(input_file, output_file, date_column, feature, repo_name):
    df = pd.read_csv(input_file)

    plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
    fig, ax = plt.subplots()

    ax.plot(df[date_column], df["count"], label="count")
    ax.plot(df[date_column], df["ema6"], label="ema6")
    ax.plot(df[date_column], df["ema12"], label="ema12")
    ax.plot(df[date_column], df["ema24"], label="ema24")
    ax.plot(df[date_column], df["ema48"], label="ema48")
    pace = len(df[date_column].values) / 15
    ax.set_xticks(df[date_column].values[0::int(pace)])
    ax.legend()
    ax.set_title(f"{feature} history for {repo_name}")

    fig.autofmt_xdate()
    fig.savefig(output_file, dpi=1000)
