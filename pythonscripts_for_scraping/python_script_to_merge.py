import pandas as pd

# Load all datasets with correct date parsing
df_main = pd.read_csv("/Users/yehana2002/Projects/DSGP/datasets/processed/final_dataset_with_monetary.csv", parse_dates=["Date"])
df_usd = pd.read_csv("/Users/yehana2002/Projects/DSGP/datasets/processed/USD_LKR_Historical_Cleaned.csv", parse_dates=["Date"])
df_econ = pd.read_csv("/Users/yehana2002/Projects/DSGP/datasets/processed/economic_indicators_cleaned.csv", parse_dates=["Date"])

# Sorting them
df_main = df_main.sort_values("Date").reset_index(drop=True)
df_usd = df_usd.sort_values("Date").reset_index(drop=True)
df_econ = df_econ.sort_values("Date").reset_index(drop=True)

# Keeping only 'Date' and 'Price' from USD dataset
df_usd = df_usd[["Date", "Price"]].rename(columns={"Price": "USD_LKR"})

# Merging USD
df_merged = df_main.merge(df_usd, on="Date", how="left")

# Merging economic indicators
df_merged = df_merged.merge(df_econ, on="Date", how="left")

# Handling missing values
df_merged["USD_LKR"] = df_merged["USD_LKR"].ffill()

econ_cols = [col for col in df_econ.columns if col != "Date"]
df_merged[econ_cols] = df_merged[econ_cols].ffill().bfill()

# Saving final merged dataset
final_path = "datasets/processed/final_merged_dataset_ready.csv"
df_merged.to_csv(final_path, index=False)

print(f"Merged dataset saved to: {final_path}")