import pandas as pd
import os

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "datasets", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "datasets", "processed")

fuel_file = os.path.join(DATA_DIR, "full_sri_lanka_fuel_prices.csv")
crude_file = os.path.join(DATA_DIR, "cleaned_global_crude_oil_prices.csv")
merged_output = os.path.join(OUTPUT_DIR, "merged_fuel_crude_prices.csv")

# Loading data
df_fuel = pd.read_csv(fuel_file)
df_crude = pd.read_csv(crude_file)

# Converting date columns to datetime
df_fuel['Date'] = pd.to_datetime(df_fuel['Date'])
df_crude['Date'] = pd.to_datetime(df_crude['Date'])

# Merging
merged_df = pd.merge(df_fuel, df_crude, on='Date', how='inner')
merged_df = merged_df.sort_values('Date').reset_index(drop=True)

# Saving merged file
merged_df.to_csv(merged_output, index=False)
print(f"✅ Merged dataset saved at: {merged_output}")
