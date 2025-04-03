import pandas as pd

# Loading the cleaned exchange rate dataset
exchange_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/USD_LKR_Historical_Cleaned.csv')
exchange_df['Date'] = pd.to_datetime(exchange_df['Date'])

# Loading main modeling dataset
main_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/final_model_ready_dataset.csv')
main_df['Date'] = pd.to_datetime(main_df['Date'])

# Merging on 'Date'
merged_df = pd.merge(main_df, exchange_df, on='Date', how='left')  # Use 'inner' if you want only matching records

# Reporting missing values after merge
missing_report = merged_df.isnull().sum()
print("🧼 Missing values after merging exchange rates:\n", missing_report[missing_report > 0])

# Handling missing values (forward and backward fill)
merged_df = merged_df.fillna(method='ffill').fillna(method='bfill')

# Saving the updated merged dataset
merged_df.to_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/final_dataset_with_exchange.csv', index=False)

print("Exchange rate data merged and saved.")
