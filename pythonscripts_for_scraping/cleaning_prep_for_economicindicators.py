import pandas as pd

# Load the dataset
df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/raw/economic indicators dataset  copy.csv')

# Dropping unnamed columns
df = df.drop(columns=['Unnamed: 7', 'Unnamed: 8'], errors='ignore')

# Renaming and formatting the date column
df.rename(columns={'observation_date': 'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

# Sorting by date and reset index
df = df.sort_values('Date').reset_index(drop=True)

# Forward fill missing values
df = df.fillna(method='ffill')

# Saving the cleaned version
df.to_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/economic_indicators_cleaned.csv', index=False)

print("Economic indicators data cleaned and saved.")
