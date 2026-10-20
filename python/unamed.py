import os
import pandas as pd

INPUT_FOLDER = "outputs"

directory = os.fsencode(INPUT_FOLDER)

pairs = [
    ("issues_created", "issues_created_by"),
    ("issues_closed", "issues_closed_by"),
    ("pulls_created", "pulls_created_by"),
    ("pulls_closed", "pulls_closed_by"),
    ("pulls_merged", "pulls_merged_by"),
]

results = dict()

for file in os.listdir(directory):
    filename = os.fsdecode(file)

    df = pd.read_csv(f"{INPUT_FOLDER}/{filename}/correlation_final.csv", index_col=0)

    for pair in pairs:
        if df[pair[0]][pair[1]] > 0.7:
            results[f"{pair[0]} x {pair[1]}"] = (
                results.get(f"{pair[0]} x {pair[1]}", 0) + 1
            )
        else:
            print(f"{pair[0]} x {pair[1]} - {filename} - {df[pair[0]][pair[1]]}")

    # Iterar pelo triangulo superior
    # indexes = np.triu_indices_from(df, k=1)
    # for i in range(len(indexes[0])):
    #     print(df.columns[indexes[0][i]], df.columns[indexes[1][i]])

print()
for k, v in results.items():
    print(f"{k} - {v}")
