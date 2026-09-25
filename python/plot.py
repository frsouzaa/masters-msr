import pandas as pd
import matplotlib.pyplot as plt


LINE_WIDTH = 1

def plot(input_file, output_file, date_column, main_column, feature, name, concat_file=None, concat_name=None):
    df = pd.read_csv(input_file).set_index(date_column)

    if concat_file:
        df2 = pd.read_csv(concat_file).set_index(date_column)
        df2.rename(
            columns={
                main_column: f"{main_column}_2",
                "ema6": "ema6_2",
                "ema12": "ema12_2",
                "ema24": "ema24_2",
                "ema48": "ema48_2",
                "summation": "summation_2",
            },
            inplace=True,
        )
        df = pd.concat(
            [df, df2],
            axis=1,
        )
        df.sort_index(inplace=True)

    # plt.style.use(
        # "https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle"
    # )
    fig, ax = plt.subplots()
    
    ax.plot(df.index, df[main_column], label=f"{name}: # {feature}", linewidth=LINE_WIDTH, linestyle="--")
    # ax.plot(df.index, df["ema6"], label=f"{name}: EMA-6", linewidth=LINE_WIDTH)
    ax.plot(df.index, df["ema12"], label=f"{name}: EMA-12", linewidth=LINE_WIDTH)
    ax.plot(df.index, df["ema24"], label=f"{name}: EMA-24", linewidth=LINE_WIDTH)
    # ax.plot(df.index, df["ema48"], label=f"{name}: EMA-48", linewidth=LINE_WIDTH)
    if concat_file:
        ax.plot(df.index, df[f"{main_column}_2"], label=f"{concat_name}: # {feature}", linewidth=LINE_WIDTH, linestyle="--")
        # ax.plot(df.index, df["ema6_2"], label=f"{concat_name}: EMA-6", linewidth=LINE_WIDTH)
        ax.plot(df.index, df["ema12_2"], label=f"{concat_name}: EMA-12", linewidth=LINE_WIDTH)
        ax.plot(df.index, df["ema24_2"], label=f"{concat_name}: EMA-24", linewidth=LINE_WIDTH)
        # ax.plot(df.index, df["ema48_2"], label=f"{concat_name}: EMA-48", linewidth=LINE_WIDTH)
    pace = len(df.index.values) / 22
    ax.set_xticks(df.index.values[0 :: int(pace)])
    ax.legend()
    ax.set_title(f"{feature} for {name}{f" and {concat_name}" if concat_name else ""}")
    
    fig.tight_layout()
    fig.autofmt_xdate()
    fig.set_size_inches(10, 6)
    fig.savefig(output_file, dpi=1000)


if __name__ == "__main__":
    OUTPUT_DIR = "outputs"
    FEATURE = "authors"
    DATE_COLUMN = "date"
    MAIN_COLUMN = "author_name"
    NAME = "junit-framework"
    CONCAT_NAME = "junit4"
    INPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}EMA.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}.svg"
    CONCAT_FILE = f"{OUTPUT_DIR}/junit4/{FEATURE}EMA.csv"
    plot(INPUT_FILE, OUTPUT_FILE, DATE_COLUMN, MAIN_COLUMN, FEATURE.replace("_", " ").title(), NAME, CONCAT_FILE, CONCAT_NAME)
