# scripts/merge_pipeline.py

import pandas as pd
from dateutil.parser import parse
import re

main_df = pd.read_csv("data/data_ciec_pipeline.csv", parse_dates=["date"])
main_df.set_index("date", inplace=True)
main_df.sort_index(inplace=True)

gazette_df = pd.read_csv("data/gazette_summary.csv")

def extract_date_from_filename(filename):
    for match in re.findall(r"\d{4}[.-]\d{2}[.-]\d{2}|\d{2}[.-]\d{2}[.-]\d{4}", filename):
        try:
            return pd.Timestamp(parse(match, dayfirst=True))
        except:
            continue
    return None

def parse_effective_date(eff_date_str):
    try:
        if pd.isna(eff_date_str) or re.fullmatch(r"\d{4}", eff_date_str.strip()):
            return None
        return pd.Timestamp(parse("01 " + eff_date_str, fuzzy=True))
    except:
        return None

first_main_date = main_df.index.min()

def get_effective_date(row):
    return (
        parse_effective_date(row.get("effective_date", "")) or
        extract_date_from_filename(row["filename"]) or
        first_main_date
    )

gazette_df["effective_datetime"] = gazette_df.apply(get_effective_date, axis=1)
gazette_df = gazette_df.dropna(subset=["effective_datetime"])
gazette_df = gazette_df.sort_values("effective_datetime").reset_index(drop=True)

columns_to_fill = [
    "acts_count", "rescinded_flag", "special_case_weight", "impact",
    "most_relevant_money", "most_relevant_percent", "fuel_related_flag"
]

for col in columns_to_fill:
    if col not in main_df.columns:
        main_df[col] = None

for i, row in gazette_df.iterrows():
    start_date = row["effective_datetime"]
    end_date = gazette_df["effective_datetime"].iloc[i + 1] if i + 1 < len(gazette_df) else main_df.index.max()
    mask = (main_df.index >= start_date) & (main_df.index < end_date)
    for col in columns_to_fill:
        main_df.loc[mask, col] = row[col]

main_df.to_csv("data/merged_ciec_with_gazette.csv")
print("✔ Merged dataset saved.")
