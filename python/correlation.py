import pandas as pd


def calculate_correlation(input_file):
    df = pd.read_csv(input_file)

    spearman = df.corr(method="spearman", numeric_only=True)
    pearson = df.corr(method="pearson", numeric_only=True)
    kendall = df.corr(method="kendall", numeric_only=True)

    print("Spearman Correlation:")
    search_correlation(spearman)
    print("Pearson Correlation:")
    search_correlation(pearson)
    print("Kendall Correlation:")
    search_correlation(kendall)

    spearman.to_csv("outputs/correlation_spearman.csv")
    pearson.to_csv("outputs/correlation_pearson.csv")
    kendall.to_csv("outputs/correlation_kendall.csv")


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
