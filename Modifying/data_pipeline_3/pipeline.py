import pandas as pd
from dateutil.parser import parse
import re

# Load main dataset and set index
main_df = pd.read_csv("data_ciec_pipeline.csv", parse_dates=["date"])
main_df.set_index("date", inplace=True)
main_df.sort_index(inplace=True)

# Load gazette summary
gazette_df = pd.read_csv("gazette_summary.csv")

# Function to extract date from filename (e.g., 2010-05-31 or 31.05.2010)
def extract_date_from_filename(filename):
    date_patterns = re.findall(r"\d{4}[.-]\d{2}[.-]\d{2}|\d{2}[.-]\d{2}[.-]\d{4}", filename)
    for date_str in date_patterns:
        try:
            dt = parse(date_str, dayfirst=True)
            return pd.Timestamp(dt.year, dt.month, 1)  # Only use Year-Month
        except:
            continue
    return None

# Normalize effective date from string like 'Mar-2010' or 'April 2010'
def parse_effective_date(eff_date_str):
    try:
        eff_date_str = eff_date_str.replace("-", " ")  # Handle 'Mar-2010' style
        dt = parse("01 " + eff_date_str)  # Add day to make it parseable
        return pd.Timestamp(dt.year, dt.month, 1)
    except:
        return None

# Combine logic: use parsed effective_date or fallback to filename
def get_effective_date(row):
    if pd.notna(row["effective_date"]):
        parsed_date = parse_effective_date(row["effective_date"])
        if parsed_date:
            return parsed_date
    return extract_date_from_filename(row["filename"])

# Apply date extraction
gazette_df["effective_datetime"] = gazette_df.apply(get_effective_date, axis=1)

# Remove rows with missing dates
gazette_df = gazette_df.dropna(subset=["effective_datetime"]).sort_values("effective_datetime")

# Columns we want to forward-fill into the main_df
columns_to_fill = [
    "acts_count", "rescinded_flag", "special_case_weight", "impact",
    "most_relevant_money", "most_relevant_percent", "fuel_related_flag"
]

# Initialize columns in main_df
for col in columns_to_fill:
    if col not in main_df.columns:
        main_df[col] = None

# Forward-fill each gazette row into main_df from its date onward, until next update
for i, row in gazette_df.iterrows():
    start_date = row["effective_datetime"]
    end_date = gazette_df["effective_datetime"].iloc[i + 1] if i + 1 < len(gazette_df) else main_df.index.max()
    mask = (main_df.index >= start_date) & (main_df.index < end_date)
    for col in columns_to_fill:
        main_df.loc[mask, col] = row[col]

# Save result
main_df.to_csv("merged_ciec_with_gazette.csv")
print(main_df.head())
