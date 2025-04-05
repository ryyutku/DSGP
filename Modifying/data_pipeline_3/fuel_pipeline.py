import pandas as pd
import ast
import os
from glob import glob # To grab multiple files that match the pattern *.csv

# Defines where your input data is, where the files should be saved
Data_Folder = "data/" # path of the data
Processed_Folder = "processed_data/" # Save individual outputs
Merged_Output_File = "processed_data/merged_features.csv"

# Functions

def parse_list_column(val):
    # convert stringified list to a real python list
    try:
        if pd.isna(val) or val.strip() == "":
            return[]
        return ast.literal_eval(val)
    except Exception:
        return []
    
def clean_dataframe(df):
    # cleans list-based and string features in the dataframe
    list_columns = ['dates', 'money_values', 'percentages']
    for col in list_columns:
        df[col] = df[col].apply(parse_list_column)
    return df

def extract_features(df):
    # creates fearture columns from lists and strings
    df['num_dates'] = df['dates'].apply(len) # no.of dates found in the text
    df['num_prices'] = df['money_values'].apply(len) # no.of prices values in the article
    df['num_percentages'] = df['percentages'].apply(len) # no.of percentages mentioned
    df['num_fuel_types'] = df['fuel_types'].fillna('').apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0) # no.of fuel types mentioned
    return df

def process_file(file_path):
    # Reads and process a single file
    try:
        df = pd.read_csv(file_path)
        df = clean_dataframe(df)
        df = extract_features(df)
        return df
    except Exception as e:
        print("Failed to process {file_path}: {e}")
        return None

def main():
    print("Scanning folder:", Data_Folder)
    os.makedirs(Processed_Folder, exist_ok = True)

    all_csv_files = glob(os.path.join(Data_Folder, "*.csv"))
    print(f"Found {len(all_csv_files)} file(s).")

    processed_dfs = []

    for file_path  in all_csv_files:
        print(f"Processing: {os.path.basename(file_path)}")
        processed_df = process_file(file_path)
        if processed_df is not None:
            processed_dfs.append(processed_df)
            base_name = os.path.basename(file_path).replace(".csv", "_fearuers.csv")
            out_path = os.path.join(Processed_Folder, base_name)
            processed_df.to_csv(out_path, index=False)
            print(f"Saved processed: {out_path}")

        if processed_dfs:
            final_df = pd.concat(processed_dfs, ignore_index= True)
            final_df.to_csv(Merged_Output_File, index= False)
            print(f"\n All processed data merged and saved to {Merged_Output_File}")

if __name__ == "__main__":
    main()