import pandas as pd
import matplotlib.pyplot as plt

filename = 'commits_by_date.csv'
df = pd.read_csv(filename)

print(df)

# df["DATE"] = pd.to_datetime(df['DATE'], format="%Y-%m-%d")

fig, ax = plt.subplots()
ax.plot(df["Committer Date"], df["Count"])
fig.autofmt_xdate()
fig.savefig('commits_by_date.png', dpi=300)
