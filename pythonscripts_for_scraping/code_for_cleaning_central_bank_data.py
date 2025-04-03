import pandas as pd

# Loading the raw dataset
df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/raw/central-bank-monatery-data_copy.csv')

# Dropping completely empty columns
df = df.dropna(axis=1, how='all')

# Cleaning numeric columns: remove commas and convert to float
for col in df.columns:
    if df[col].dtype == 'object' and col != 'Date':
        df[col] = df[col].str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Converting Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Dropping rows without valid dates
df = df.dropna(subset=['Date'])

# Sorting by Date
df = df.sort_values('Date').reset_index(drop=True)

# Handling missing values - forward fill, then backfill as fallback
df = df.fillna(method='ffill').fillna(method='bfill')

# Saving cleaned version
df.to_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/central_bank_monetary_cleaned.csv', index=False)

print("Central Bank Monetary dataset cleaned and saved.")
