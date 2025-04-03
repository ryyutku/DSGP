import pandas as pd

# Loading the cleaned central bank monetary data
monetary_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/central_bank_monetary_cleaned.csv')
monetary_df['Date'] = pd.to_datetime(monetary_df['Date'])

# Loading main modeling dataset
main_df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/final_model_ready_dataset.csv')
main_df['Date'] = pd.to_datetime(main_df['Date'])

# Merge on 'Date'
merged_df = pd.merge(main_df, monetary_df, on='Date', how='left')  

# Checking for remaining missing values
missing_report = merged_df.isnull().sum()
print("Missing values after merge:\n", missing_report[missing_report > 0])

# Filling remaining missing values 
merged_df = merged_df.fillna(method='ffill').fillna(method='bfill')

# Saving the merged dataset
merged_df.to_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/final_dataset_with_monetary.csv', index=False)

print("Merged dataset with monetary indicators saved.")
