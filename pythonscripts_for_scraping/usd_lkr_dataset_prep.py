import pandas as pd

# Loading the dataset with proper encoding and delimiter
df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/raw/USD_LKR Historical Data.csv', encoding='utf-8')

# Renaming first column to 'Date'
if df.columns[0].strip().lower() != 'date':
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

# Converting to datetime with correct format: day/month/year
df['Date'] = pd.to_datetime(df['Date'].str.strip(), format='%d/%m/%Y', errors='coerce')

df = df.dropna(subset=['Date'])

# Sorting chronologically
df = df.sort_values('Date').reset_index(drop=True)

# Formatting back to standard ISO format (YYYY-MM-DD)
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Saving cleaned file
df.to_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/USD_LKR_Historical_Cleaned.csv', index=False, encoding='utf-8-sig')

print("Cleaned USD/LKR exchange rate dataset saved with properly formatted and sorted dates.")
