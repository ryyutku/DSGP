import pandas as pd

# Load cleaned datasets
fuel_df = pd.read_csv('datasets/processed/merged_petrol_diesel_platts.csv')
exchange_df = pd.read_csv('datasets/processed/exchange_rates_cleaned.csv')
macro_df = pd.read_csv('datasets/processed/central_bank_monetary_cleaned.csv')
econ_df = pd.read_csv('datasets/processed/economic_indicators_cleaned.csv')

# Ensure datetime format
fuel_df['Date'] = pd.to_datetime(fuel_df['Date'])
exchange_df['Date'] = pd.to_datetime(exchange_df['Date'])
macro_df['Date'] = pd.to_datetime(macro_df['Date'])
econ_df['Date'] = pd.to_datetime(econ_df['Date'])

# Merge step-by-step
merged = pd.merge(fuel_df, exchange_df, on='Date', how='left')
merged = pd.merge(merged, macro_df, on='Date', how='left')
merged = pd.merge(merged, econ_df, on='Date', how='left')

# Sort and forward-fill missing values for macroeconomic columns
merged = merged.sort_values('Date').reset_index(drop=True)
merged.fillna(method='ffill', inplace=True)

# Save final merged dataset
merged.to_csv('datasets/processed/final_model_ready_dataset.csv', index=False)
print("✅ Final dataset for modeling is ready.")
