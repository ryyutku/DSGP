import os
import pandas as pd
import numpy as np
import ast
from glob import glob
from datetime import datetime

# ------------------- 1. Define Constants -------------------

Data_Folder = "data/"
Processed_Folder = "processed_data/"
Merged_Output_File = "processed_data/merged_features.csv"

# ------------------- 2. Helper Functions -------------------

def parse_list_column(val):
    """
    Converts stringified lists into actual Python lists.
    """
    try:
        if pd.isna(val) or val.strip() == "":
            return []
        return ast.literal_eval(val)
    except Exception:
        return []

def clean_dataframe(df):
    """
    Cleans the dataframe by handling list-based and string-based columns.
    Converts date strings into datetime objects and handles list columns (like 'dates', 'money_values', etc.).
    """
    # Convert string-based list columns into actual lists
    list_columns = ['dates', 'money_values', 'percentages']
    for col in list_columns:
        df[col] = df[col].apply(parse_list_column)
        
    # Convert 'dates' into datetime objects for further time-based analysis
    df['date_list'] = df['dates'].apply(lambda x: [datetime.strptime(date, '%dth %B %Y') for date in x])
    return df

def extract_features(df):
    """
    Extracts meaningful features from the raw data, such as:
    - Number of dates mentioned.
    - Number of monetary mentions.
    - Number of percentage mentions.
    - Number of fuel types mentioned.
    """
    # Number of dates mentioned
    df['num_dates'] = df['dates'].apply(len)
    
    # Number of monetary values mentioned
    df['num_prices'] = df['money_values'].apply(len)
    
    # Number of percentages mentioned
    df['num_percentages'] = df['percentages'].apply(len)
    
    # Number of fuel types mentioned (split by commas)
    df['num_fuel_types'] = df['fuel_types'].fillna('').apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)
    
    # Create a feature for tax change magnitude based on 'money_values' and 'percentages'
    # This can be calculated by extracting monetary values and percentages
    df['tax_change_magnitude'] = df.apply(lambda x: sum([float(val.replace('Rs.', '').replace(',', '').strip()) for val in x['money_values']]) if x['money_values'] else 0, axis=1)
    
    return df

def assign_time_periods(df):
    """
    Assigns time periods (e.g., monthly or yearly) based on the 'dates' column.
    """
    # For simplicity, we will assign to a monthly period using the first date mentioned
    df['year_month'] = df['date_list'].apply(lambda x: x[0].strftime('%Y-%m') if x else None)
    return df

def process_gazette_file(file_path):
    """
    Reads and processes the Gazette data file.
    """
    try:
        df = pd.read_csv(file_path)
        df = clean_dataframe(df)
        df = extract_features(df)
        df = assign_time_periods(df)
        return df
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")
        return None

def merge_datasets(ciec_df, gazette_df):
    """
    Merges the CIEC dataset with the Gazette dataset on the 'year_month' time period.
    """
    merged_df = pd.merge(ciec_df, gazette_df, on='year_month', how='left')
    return merged_df

def main():
    """
    Main function to process all data files.
    """
    print("Scanning folder:", Data_Folder)
    os.makedirs(Processed_Folder, exist_ok=True)

    all_csv_files = glob(os.path.join(Data_Folder, "*.csv"))
    print(f"Found {len(all_csv_files)} file(s).")

    processed_dfs = []

    for file_path in all_csv_files:
        print(f"Processing: {os.path.basename(file_path)}")
        processed_df = process_gazette_file(file_path)
        if processed_df is not None:
            processed_dfs.append(processed_df)
            base_name = os.path.basename(file_path).replace(".csv", "_processed.csv")
            out_path = os.path.join(Processed_Folder, base_name)
            processed_df.to_csv(out_path, index=False)
            print(f"Saved processed: {out_path}")

    # Merge all processed Gazette files with the CIEC data
    if processed_dfs:
        # Load CIEC data
        ciec_df = pd.read_csv(os.path.join(Data_Folder, "ciec.csv"))
        ciec_df['Date'] = pd.to_datetime(ciec_df['Date'])
        ciec_df['year_month'] = ciec_df['Date'].dt.strftime('%Y-%m')

        # Merge datasets
        gazette_df = pd.concat(processed_dfs, ignore_index=True)
        merged_df = merge_datasets(ciec_df, gazette_df)

        # Save the merged data
        merged_df.to_csv(Merged_Output_File, index=False)
        print(f"\nAll processed data merged and saved to {Merged_Output_File}")

if __name__ == "__main__":
    main()
