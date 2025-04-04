import pandas as pd

# Loading the dataset
df = pd.read_csv('/Users/yehana2002/Projects/DSGP/datasets/processed/model_ready_dataset.csv')

# Converting 'Date' to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# Forward-fill and backward-fill missing values
df = df.ffill().bfill()

# Creating lag features for key fuel price columns
lag_columns = [
    'petrol_price',
    'diesel_price',
    'formula_price_with_tax_petrol',
    'formula_price_with_tax_diesel'
]

lags = [1, 2, 3]

for col in lag_columns:
    if col in df.columns:
        for lag in lags:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)

# Saving the cleaned and lag-feature-augmented dataset
df.to_csv('datasets/processed/model_ready_dataset_cleaned.csv', index=False)

print("Cleaned and saved: model_ready_dataset_cleaned.csv")
