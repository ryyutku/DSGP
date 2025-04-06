import os
import re
import spacy
import pandas as pd
from dateutil import parser
from gazette_keywords import gazette_keywords

nlp = spacy.load("en_core_web_sm")

# Assign weights to special use cases
special_case_weights = {
    "Disaster": 2,
    "Reconstruction": 2,
    "Exported articles": 1,
    "Passenger baggage exemption": 1,
    "Ship stores": 1,
    "Funeral undertakers": 1,
    "Locally assembled vehicles": 2,
    "Primary holder of Sri Lanka Nation Building Bond": 2,
    "SLNBB": 2,
    "Financial leasing": 1,
    "Consolidated Fund": 2,
    "Vehicles": 2,
    "Import": 3,
    "Harbour": 1,
    "Engine": 1,
}

def load_text_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith("_text.txt"):
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                files.append((file, f.read()))
    return files

def extract_most_relevant_value(pattern, text):
    matches = re.findall(pattern, text)
    values = []
    for m in matches:
        num = re.findall(r"[\d.,]+", m)
        if num:
            try:
                val = float(num[0].replace(",", ""))
                values.append(val)
            except:
                continue
    return max(values) if values else None

def extract_latest_month_year(text, filename=None):
    date_strings = []

    # Match things like "22nd November 2010" or "March 2010"
    text_matches = re.findall(r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", text, re.IGNORECASE)
    full_matches = re.findall(r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", text, re.IGNORECASE)
    date_strings.extend(full_matches)

    # From filename
    if filename:
        fname_clean = filename.replace("_", " ").replace("-", " ")
        fname_matches = re.findall(r"(?:\d{1,2}\s*)?(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}", fname_clean, re.IGNORECASE)
        full_fname_matches = re.findall(r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", fname_clean, re.IGNORECASE)
        alt_matches = re.findall(r"\d{4}[_\-]?\d{2}", filename)  # e.g., 2010_03
        date_strings.extend(full_fname_matches)
        for match in alt_matches:
            try:
                dt = parser.parse(match)
                date_strings.append(dt.strftime("%B %Y"))
            except:
                continue

    # Parse and return latest
    parsed_dates = []
    for ds in date_strings:
        try:
            parsed_dates.append(parser.parse(ds))
        except:
            continue

    if parsed_dates:
        latest = max(parsed_dates)
        return latest.strftime("%B %Y")
    return None

def process_text(filename, text):
    doc = nlp(text)
    lowered = text.lower()

    acts_count = sum(1 for w in gazette_keywords["policy_actions"] if w.lower() in lowered)
    rescinded_flag = 1 if "rescinded" in lowered or "revoked" in lowered else 0
    fuel_related_flag = any(word.lower() in lowered for word in gazette_keywords["fuel_types"])

    special_weight = 0
    for word in gazette_keywords["special_use_cases"]:
        if word.lower() in lowered:
            special_weight += special_case_weights.get(word, 1)

    if any(w in lowered for w in ["exempt", "concession", "reduction", "remove", "decrease"]):
        impact = 1
    elif any(w in lowered for w in ["duty", "levy", "increase", "tax imposed", "additional"]):
        impact = 0
    else:
        impact = -1

    money = extract_most_relevant_value(r"(?:LKR|Rs\.?|rupees)?\s?\d+(?:,\d{3})*(?:\.\d+)?", text)
    percent = extract_most_relevant_value(r"\d{1,3}(?:\.\d+)?%", text)

    effective_date = extract_latest_month_year(text, filename)

    return {
        "filename": filename,
        "acts_count": acts_count,
        "rescinded_flag": rescinded_flag,
        "special_case_weight": special_weight,
        "impact": impact,
        "most_relevant_money": money,
        "most_relevant_percent": percent,
        "fuel_related_flag": 1 if fuel_related_flag else 0,
        "effective_date": effective_date
    }

def process_all(directory):
    records = []
    files = load_text_files(directory)
    for file, text in files:
        print(f"Processing {file}")
        record = process_text(file, text)
        records.append(record)
    return pd.DataFrame(records)

if __name__ == "__main__":
    input_dir = "extracted_data"
    df = process_all(input_dir)
    df.to_csv("gazette_summary.csv", index=False)
    print("Saved summarized gazette data.")
