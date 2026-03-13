import pandas as pd
df = pd.read_csv("experiments/cardekho_clean.csv")
print(df.head())
print(df.dtypes)
print(df.isna().sum())
print(df["selling_price"].describe())