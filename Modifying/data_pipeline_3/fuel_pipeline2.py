import os
import pandas as pd

# ------------------- 1. Set Folder Paths -------------------

# Get the absolute path to the folder this script is in (src/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the root project directory
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Construct path to the raw data directory (data/raw)
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')

# Define paths to the CSV files
main_csv_path = os.path.join(RAW_DATA_DIR, 'ciec.csv')
gazette_csv_path = os.path.join(RAW_DATA_DIR, 'gazette_insights.csv')

# ------------------- 2. Verify File Existence -------------------

# Print out paths for debugging
print(f"Main data path: {main_csv_path}")
print(f"Gazette data path: {gazette_csv_path}")

# Raise an error if files are not found
if not os.path.exists(main_csv_path):
    raise FileNotFoundError(f"Main CSV not found at {main_csv_path}")
if not os.path.exists(gazette_csv_path):
    raise FileNotFoundError(f"Gazette insights CSV not found at {gazette_csv_path}")

# ------------------- 3. Load CSV Files -------------------

# Read the main dataset (this is your time series / fuel data)
main_df = pd.read_csv(main_csv_path)

# Read the gazette insights (news/policy/economic events)
gazette_df = pd.read_csv(gazette_csv_path)

# Convert 'Date' columns to datetime objects for comparison/merge
main_df['Date'] = pd.to_datetime(main_df['Date'])
gazette_df['Date'] = pd.to_datetime(gazette_df['Date'])

# ------------------- 4. Clean & Process Gazette Data -------------------

# Fill missing gazette entries with empty strings (avoid NaNs during merge)
gazette_df = gazette_df.fillna('')

# ------------------- 5. Merge Gazette into Main Data -------------------

# This is a left join: Keep all rows from main_df, attach matching gazette entries if dates match
merged_df = pd.merge(main_df, gazette_df, how='left', on='Date')

# ------------------- 6. Save Merged Data -------------------

# Create output directory if it doesn't exist
output_dir = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(output_dir, exist_ok=True)

# Define output file path
output_csv_path = os.path.join(output_dir, 'merged_fuel_data.csv')

# Save the new merged dataset
merged_df.to_csv(output_csv_path, index=False)

# ------------------- 7. Status Message -------------------
print(f"Merged dataset saved to: {output_csv_path}")
