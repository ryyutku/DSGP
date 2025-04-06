import pandas as pd
from dateutil.parser import parse
import re

# Load main data and set datetime index
main_df = pd.read_csv("data_ciec_pipeline.csv", parse_dates=["date"])
main_df.set_index("date", inplace=True)
main_df.sort_index(inplace=True)

# Get the earliest date in main_df as a fallback
first_main_date = main_df.index.min()

# Load gazette summary
gazette_df = pd.read_csv("merged data.csv")

# Extract date from filename using regex
def extract_date_from_filename(filename):
    date_patterns = re.findall(r"\d{4}[.-]\d{2}[.-]\d{2}|\d{2}[.-]\d{2}[.-]\d{4}", filename)
    for date_str in date_patterns:
        try:
            dt = parse(date_str, dayfirst=True, fuzzy=True)
            return pd.Timestamp(dt.year, dt.month, 1)
        except:
            continue
    return None

# Parse effective_date field safely
def parse_effective_date(eff_date_str):
    try:
        if pd.isna(eff_date_str):
            return None
        eff_date_str = eff_date_str.replace("-", " ").strip()
        # Skip invalid cases like just '1747'
        if re.fullmatch(r"\d{4}", eff_date_str.strip()):
            return None
        dt = parse("01 " + eff_date_str, fuzzy=True)
        return pd.Timestamp(dt.year, dt.month, 1)
    except:
        return None

# Main function to get valid effective date
def get_effective_date(row):
    eff_date = parse_effective_date(row.get("effective_date", ""))
    if eff_date:
        return eff_date

    filename_date = extract_date_from_filename(row["filename"])
    if filename_date:
        return filename_date

    return first_main_date  # fallback if nothing works

# Apply the date extraction logic
gazette_df["effective_datetime"] = gazette_df.apply(get_effective_date, axis=1)

# Sort gazette_df by effective_datetime BEFORE merging — very important
gazette_df = gazette_df.dropna(subset=["effective_datetime"])
gazette_df = gazette_df.sort_values("effective_datetime").reset_index(drop=True)

# Define columns to be merged
columns_to_fill = [
    "acts_count", "rescinded_flag", "special_case_weight", "impact",
    "most_relevant_money", "most_relevant_percent", "fuel_related_flag"
]

# Add columns to main_df if missing
for col in columns_to_fill:
    if col not in main_df.columns:
        main_df[col] = None

# Forward-fill logic between gazette events
for i, row in gazette_df.iterrows():
    start_date = row["effective_datetime"]
    end_date = gazette_df["effective_datetime"].iloc[i + 1] if i + 1 < len(gazette_df) else main_df.index.max()
    mask = (main_df.index >= start_date) & (main_df.index < end_date)
    for col in columns_to_fill:
        main_df.loc[mask, col] = row[col]

# Save the final result
main_df.to_csv("merged_ciec_with_gazette.csv")
print(main_df.head())
