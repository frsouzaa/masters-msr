import numpy as np
import pandas as pd
from scipy.stats import anderson, MonteCarloMethod
from itertools import permutations


def anderson_darling(input_file, output_file):
    df = pd.read_csv(input_file)
    df.drop(columns=["date"], inplace=True)
    df_output = pd.DataFrame(columns=["feature", "pvalue", "distribution"])
    for c in df.columns:
        result = anderson(df[c].values, dist="norm", method=MonteCarloMethod())
        df_output = pd.concat(
            [
                df_output,
                pd.DataFrame(
                    [
                        [
                            c,
                            result.pvalue,
                            (
                                "normal"
                                if result.pvalue >= np.float64("0.05")
                                else "non-normal"
                            ),
                        ]
                    ],
                    columns=df_output.columns.values,
                ),
            ],
            ignore_index=True,
        )
    df_output.to_csv(output_file, index=False)


def correlation(input_file, output_folder, verbose=False):
    df = pd.read_csv(input_file)

    spearman = df.corr(method="spearman", numeric_only=True)
    pearson = df.corr(method="pearson", numeric_only=True)

    if verbose:
        print("Spearman Correlation:")
        search_correlation(spearman)
        print("Pearson Correlation:")
        search_correlation(pearson)

    spearman_file = f"{output_folder}/correlation_spearman.csv"
    pearson_file = f"{output_folder}/correlation_pearson.csv"
    spearman.to_csv(spearman_file)
    pearson.to_csv(pearson_file)

    return spearman_file, pearson_file


def search_correlation(df):
    correlations_found = set()
    for column in df.columns:
        for row in df[column].index:
            if (
                column != row
                and abs(df[column][row]) > 0.7
                and f"{column}-{row}" not in correlations_found
            ):
                correlations_found.add(f"{column}-{row}")
                correlations_found.add(f"{row}-{column}")
                print(f"High correlation between {column} and {row}: {df[column][row]}")


def merge_correlation_by_anderson_darling(
    spearman_file, pearson_file, anderson_darling_file, output_file
):
    spearman = pd.read_csv(spearman_file, index_col=0)
    pearson = pd.read_csv(pearson_file, index_col=0)
    anderson_darling = pd.read_csv(anderson_darling_file)

    normal_distributions = permutations(
        anderson_darling.loc[(anderson_darling["distribution"] == "normal")][
            "feature"
        ].values,
        2,
    )

    for normal_distribution in normal_distributions:
        value = pearson[normal_distribution[0]][normal_distribution[1]]
        spearman.loc[normal_distribution[0], normal_distribution[1]] = value

    spearman.to_csv(output_file)
