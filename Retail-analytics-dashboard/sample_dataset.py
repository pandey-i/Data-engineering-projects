import pandas as pd

df = pd.read_csv("data/processed/final_data.csv")

df.head(1000).to_csv(
    "data/processed/sample_data.csv",
    index=False
)