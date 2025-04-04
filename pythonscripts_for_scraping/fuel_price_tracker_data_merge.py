import pandas as pd

petrol_path = '/Users/yehana2002/Projects/DSGP/datasets/raw/PetrolFormulaAndMarketPrices.csv'
diesel_path = '/Users/yehana2002/Projects/DSGP/datasets/raw/DieselFormulaAndMarketPrices.csv'

petrol_df = pd.read_csv(petrol_path)
diesel_df = pd.read_csv(diesel_path)

print("Petrol DF columns:", petrol_df.columns)
print("Diesel DF columns:", diesel_df.columns)

# Strip any whitespace and normalize column names
petrol_df.columns = petrol_df.columns.str.strip()
diesel_df.columns = diesel_df.columns.str.strip()


# Converting date
petrol_df['Date'] = pd.to_datetime(petrol_df['Date'], errors='coerce')

# Drop unnamed or empty columns
petrol_df = petrol_df.loc[:, ~petrol_df.columns.str.contains('^Unnamed')]

# Converting all numeric columns to float
petrol_df.iloc[:, 1:] = petrol_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# Cleaning Diesel Dataset
diesel_df['Date'] = pd.to_datetime(diesel_df['Date'], errors='coerce')
diesel_df = diesel_df.loc[:, ~diesel_df.columns.str.contains('^Unnamed')]
diesel_df.iloc[:, 1:] = diesel_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# Saving cleaned versions
petrol_df.to_csv('datasets/processed/petrol_prices_cleaned.csv', index=False)
diesel_df.to_csv('datasets/processed/diesel_prices_cleaned.csv', index=False)
print("Cleaned petrol and diesel datasets saved.")

merged_df = pd.merge(petrol_df, diesel_df, on='Date', suffixes=('_petrol', '_diesel'))
merged_df = merged_df.sort_values('Date').reset_index(drop=True)

# Saving merged version
merged_df.to_csv('datasets/processed/petrol_diesel_merged.csv', index=False)
print("Merged petrol and diesel dataset saved.")
