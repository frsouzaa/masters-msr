import pandas as pd
import matplotlib.pyplot as plt


LINE_WIDTH = 1

def plot(input_file, output_file, date_column, main_column, feature, name, concat_file=None, concat_name=None):
    df = pd.read_csv(input_file).set_index(date_column)
    df.rename(
        columns={
            main_column: f"{name}_{main_column}",
            "ema6": f"{name}_ema6",
            "ema12": f"{name}_ema12",
            "ema24": f"{name}_ema24",
            "ema48": f"{name}_ema48",
            "summation": f"{name}_summation",
        },
        inplace=True,
    )

    if concat_file:
        df1 = df
        df2 = pd.read_csv(concat_file).set_index(date_column)
        df2.rename(
            columns={
                main_column: f"{concat_name}_{main_column}",
                "ema6": f"{concat_name}_ema6",
                "ema12": f"{concat_name}_ema12",
                "ema24": f"{concat_name}_ema24",
                "ema48": f"{concat_name}_ema48",
                "summation": f"{concat_name}_summation",
            },
            inplace=True,
        )
        concat = [df1, df2]
        min1 = min(df1.index.values)
        min2 = min(df2  .index.values)
        if min2 < min1:
            concat = concat[::-1]
            name, concat_name = concat_name, name
        df = pd.concat(
            concat,
            axis=1,
        )
        df.sort_index(inplace=True)

    # plt.style.use(
        # "https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle"
    # )
    fig, ax = plt.subplots()
    
    ax.plot(df.index, df[f"{name}_{main_column}"], label=f"{name}: # {feature}", linewidth=LINE_WIDTH, linestyle="--")
    # ax.plot(df.index, df[f"{name}_ema6"], label=f"{name}: EMA-6", linewidth=LINE_WIDTH)
    ax.plot(df.index, df[f"{name}_ema12"], label=f"{name}: EMA-12", linewidth=LINE_WIDTH)
    ax.plot(df.index, df[f"{name}_ema24"], label=f"{name}: EMA-24", linewidth=LINE_WIDTH)
    # ax.plot(df.index, df[f"{name}_ema48"], label=f"{name}: EMA-48", linewidth=LINE_WIDTH)
    if concat_file:
        ax.plot(df.index, df[f"{concat_name}_{main_column}"], label=f"{concat_name}: # {feature}", linewidth=LINE_WIDTH, linestyle="--")
        # ax.plot(df.index, df[f"{concat_name}_ema6"], label=f"{concat_name}: EMA-6", linewidth=LINE_WIDTH)
        ax.plot(df.index, df[f"{concat_name}_ema12"], label=f"{concat_name}: EMA-12", linewidth=LINE_WIDTH)
        ax.plot(df.index, df[f"{concat_name}_ema24"], label=f"{concat_name}: EMA-24", linewidth=LINE_WIDTH)
        # ax.plot(df.index, df[f"{concat_name}_ema48"], label=f"{concat_name}: EMA-48", linewidth=LINE_WIDTH)
    pace = len(df.index.values) / 22
    ax.set_xticks(df.index.values[0 :: int(pace)])
    ax.legend()
    ax.set_title(f"{feature} for {name}{f" and {concat_name}" if concat_name else ""}")
    
    fig.tight_layout()
    fig.autofmt_xdate()
    fig.set_size_inches(10, 6)
    fig.savefig(output_file, dpi=1000)


if __name__ == "__main__":
    FEATURE = "pulls"
    DATE_COLUMN = "created_at"
    MAIN_COLUMN = "count"
    NAME = "csv"
    OUTPUT_DIR = "outputs"
    INPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}EMA.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}-{NAME}.png"
    
    # CONCAT_NAME = "junit4"
    # CONCAT_FILE = f"{OUTPUT_DIR}/junit4/{FEATURE}EMA.csv"
    # OUTPUT_FILE = f"{OUTPUT_DIR}/{FEATURE}-{NAME}-X-{CONCAT_NAME}.png"
    # plot(INPUT_FILE, OUTPUT_FILE, DATE_COLUMN, MAIN_COLUMN, FEATURE.replace("_", " ").title(), NAME, CONCAT_FILE, CONCAT_NAME)

    plot(INPUT_FILE, OUTPUT_FILE, DATE_COLUMN, MAIN_COLUMN, FEATURE.replace("_", " ").title(), NAME)
