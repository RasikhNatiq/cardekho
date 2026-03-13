# experiments/prepare_data.py
import pandas as pd

# 1. Load the raw dataset
df = pd.read_csv("app/cardekho.csv")

# 2. Work on a copy so we don't overwrite the original
df_clean = df.copy()

# 3. Feature engineering
# Age of car (newer cars usually sell higher)
current_year = df_clean["year"].max()
df_clean["age"] = current_year - df_clean["year"]

# Convert max_power to numeric (some entries are strings)
df_clean["max_power"] = pd.to_numeric(df_clean["max_power"], errors="coerce")

# Extract brand from name (first word)
df_clean["brand"] = df_clean["name"].apply(lambda s: s.split()[0].lower())

# 4. Handle missing values
# Fill numeric columns with 0
for col in ["mileage(km/ltr/kg)", "engine", "max_power", "seats"]:
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0)

# Fill categorical columns with "unknown"
for col in ["fuel", "seller_type", "transmission", "owner"]:
    df_clean[col] = df_clean[col].fillna("unknown")

# 5. Save cleaned dataset separately
df_clean.to_csv("experiments/cardekho_clean.csv", index=False)

# 6. Print a preview
print("Cleaned dataset preview:")
print(df_clean.head())
print("\nMissing values after cleaning:")
print(df_clean.isna().sum())