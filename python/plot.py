import pandas as pd
import matplotlib.pyplot as plt

TYPE = "commits"
INPUT = f"outputs/{TYPE}FinalEMA.csv"
OUTPUT = f"outputs/{TYPE}EMA.svg"

df = pd.read_csv(INPUT)

# df["DATE"] = pd.to_datetime(df['DATE'], format="%Y-%m-%d")

plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
fig, ax = plt.subplots()

ax.plot(df["date"], df["count"], label="count")
ax.plot(df["date"], df["ema6"], label="ema6")
ax.plot(df["date"], df["ema12"], label="ema12")
ax.plot(df["date"], df["ema24"], label="ema24")
ax.plot(df["date"], df["ema48"], label="ema48")
pace = len(df["date"].values) / 15
ax.set_xticks(df["date"].values[0::int(pace)])
ax.legend()
ax.set_title(f"{TYPE} history for <some_repo>")

fig.autofmt_xdate()
fig.savefig(OUTPUT, dpi=1000)
