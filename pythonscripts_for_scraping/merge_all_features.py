import pandas as pd

# Load cleaned datasets
fuel_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/petrol_diesel_merged.csv')
exchange_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/USD_LKR_Historical_Cleaned.csv')
macro_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/central_bank_monetary_cleaned.csv')
econ_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/economic_indicators_cleaned.csv')

# Ensuring datetime format
fuel_df['Date'] = pd.to_datetime(fuel_df['Date'])
exchange_df['Date'] = pd.to_datetime(exchange_df['Date'])
macro_df['Date'] = pd.to_datetime(macro_df['Date'])
econ_df['Date'] = pd.to_datetime(econ_df['Date'])

# Merging step-by-step
merged = pd.merge(fuel_df, exchange_df, on='Date', how='left')
merged = pd.merge(merged, macro_df, on='Date', how='left')
merged = pd.merge(merged, econ_df, on='Date', how='left')

# Sort and forward-fill missing values for macroeconomic columns
merged = merged.sort_values('Date').reset_index(drop=True)
merged.fillna(method='ffill', inplace=True)

# Save final merged dataset
merged.to_csv('datasets/processed/model_ready_dataset.csv', index=False)
print("Final dataset for modeling is ready.")
