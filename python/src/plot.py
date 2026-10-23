import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

LINE_WIDTH = 1


def plot_ema(
    input_file,
    output_file,
    feature,
    name,
    concat_file=None,
    concat_name=None,
    date_column="date",
    main_column="count",
):
    df = pd.read_csv(input_file).set_index(date_column)
    df.rename(
        columns={
            main_column: f"{name}_{main_column}",
            "short_ema": f"{name}_short_ema",
            "long_ema": f"{name}_long_ema",
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
                "short_ema": f"{concat_name}_short_ema",
                "long_ema": f"{concat_name}_long_ema",
                "summation": f"{concat_name}_summation",
            },
            inplace=True,
        )
        concat = [df1, df2]
        min1 = min(df1.index.values)
        min2 = min(df2.index.values)
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

    ax.plot(
        df.index,
        df[f"{name}_{main_column}"],
        label=f"{name}: # {feature}",
        linewidth=LINE_WIDTH,
        linestyle="--",
    )
    ax.plot(
        df.index,
        df[f"{name}_short_ema"],
        label=f"{name}: Short EMA",
        linewidth=LINE_WIDTH,
    )
    ax.plot(
        df.index,
        df[f"{name}_long_ema"],
        label=f"{name}: Long EMA",
        linewidth=LINE_WIDTH,
    )
    if concat_file:
        ax.plot(
            df.index,
            df[f"{concat_name}_{main_column}"],
            label=f"{concat_name}: # {feature}",
            linewidth=LINE_WIDTH,
            linestyle="--",
        )
        ax.plot(
            df.index,
            df[f"{concat_name}_short_ema"],
            label=f"{concat_name}: Short EMA",
            linewidth=LINE_WIDTH,
        )
        ax.plot(
            df.index,
            df[f"{concat_name}_long_ema"],
            label=f"{concat_name}: Long EMA",
            linewidth=LINE_WIDTH,
        )
    pace = len(df.index.values) / 20
    ax.set_xticks(df.index.values[0 :: max(1, int(pace))])
    ax.legend()
    ax.set_title(f"{feature} for {name}{f" and {concat_name}" if concat_name else ""}")

    fig.autofmt_xdate()
    fig.set_size_inches(10, 6)
    fig.savefig(output_file, dpi=1000, bbox_inches="tight", pad_inches=0)


def msr_plot(
    input_file,
    output_file,
    name,
    concat_file=None,
    concat_name=None,
    date_column="date",
    main_column="count",
):
    df = pd.read_csv(input_file).set_index(date_column)
    df.rename(
        columns={
            main_column: f"{name}_{main_column}",
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
                "summation": f"{concat_name}_summation",
            },
            inplace=True,
        )
        concat = [df1, df2]
        min1 = min(df1.index.values)
        min2 = min(df2.index.values)
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

    ax.plot(
        df.index,
        df[f"{name}_{main_column}"],
        label=f"# Created Pull Requests",
        linewidth=LINE_WIDTH,
        linestyle="--",
    )
    if concat_file:
        ax.plot(
            df.index,
            df[f"{concat_name}_{main_column}"],
            label=f"# Pull Request Creators",
            linewidth=LINE_WIDTH,
            linestyle="--",
        )
    pace = len(df.index.values) / 20
    ax.set_xticks(df.index.values[0 :: max(1, int(pace))])
    ax.legend()

    fig.autofmt_xdate()
    fig.set_size_inches(10, 6)
    fig.savefig(output_file, dpi=1000, bbox_inches="tight", pad_inches=0)


def plot_correlation_matrix(input_file, output_file):
    df = pd.read_csv(input_file, index_col=0)

    fig, ax = plt.subplots(nrows=1, ncols=1)

    cax = ax.matshow(df, interpolation="nearest", vmin=-1, vmax=1, cmap="Spectral")

    fig.colorbar(cax)

    ticks = list(range(len(df.columns)))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)

    ax.set_xticklabels(df.columns, rotation=90)
    ax.set_yticklabels(df.columns)

    for i, row in enumerate(df.values):
        for j, value in enumerate(row):
            ax.text(
                i,
                j,
                str(np.round(value, 2)),
                va="center",
                ha="center",
                color="black" if abs(value) < 0.7 else "white",
            )

    fig.set_size_inches(10, 8)

    plt.savefig(output_file, dpi=1000, bbox_inches="tight", pad_inches=0)


def plot_merged_features(input_file, output_file):
    df = pd.read_csv(input_file).set_index("date")

    fig, ax = plt.subplots()

    for feature in df.columns.values:
        ax.plot(df.index, df[feature], label=feature, linewidth=LINE_WIDTH)

    pace = len(df.index.values) / 20
    ax.set_xticks(df.index.values[0 :: max(1, int(pace))])
    ax.legend()

    fig.autofmt_xdate()
    fig.set_size_inches(16, 12)
    fig.savefig(output_file, dpi=1000, bbox_inches="tight", pad_inches=0)


if __name__ == "__main__":
    FEATURE = "pulls"
    DATE_COLUMN = "date"
    MAIN_COLUMN = "count"
    NAME = "created"
    OUTPUT_DIR = "outputs"
    INPUT_FILE = f"{OUTPUT_DIR}/vue/final_pulls_created.csv"

    CONCAT_NAME = "authors"
    CONCAT_FILE = f"{OUTPUT_DIR}/vue/final_pulls_created_by.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/vue.svg"
    msr_plot(
        INPUT_FILE,
        OUTPUT_FILE,
        FEATURE.replace("_", " ").title(),
        NAME,
        CONCAT_FILE,
        CONCAT_NAME,
        DATE_COLUMN,
        MAIN_COLUMN,
    )

    # plot_ema(INPUT_FILE, OUTPUT_FILE, FEATURE.replace("_", " ").title(), NAME, date_column=DATE_COLUMN, main_column=MAIN_COLUMN)

    # REPO = "express"
    # OUTPUT_DIR = "outputs"
    # INPUT_FILE = f"{OUTPUT_DIR}/{REPO}/correlation_final.csv"
    # OUTPUT_FILE = f"{OUTPUT_DIR}/{REPO}/plot_correlation_final.svg"
    # plot_correlation_matrix(INPUT_FILE, OUTPUT_FILE)

    # REPO = "electron"
    # OUTPUT_DIR = "outputs"
    # INPUT_FILE = f"{OUTPUT_DIR}/{REPO}/merged_features.csv"
    # OUTPUT_FILE = f"{OUTPUT_DIR}/{REPO}/plot_merged_features.svg"
    # plot_merged_features(INPUT_FILE, OUTPUT_FILE)
