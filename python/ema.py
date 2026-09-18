from datetime import datetime
import pandas as pd

TYPE = "commits"
INPUT = f"outputs/{TYPE}Final.csv"
OUTPUT = f"outputs/{TYPE}FinalEMA.csv"

df = pd.read_csv(INPUT)

df["ema6"] = df["count"].ewm(span=6).mean()
df["ema12"] = df["count"].ewm(span=12).mean()
df["ema24"] = df["count"].ewm(span=24).mean()
df["ema48"] = df["count"].ewm(span=48).mean()

df.to_csv(OUTPUT, index=False)
