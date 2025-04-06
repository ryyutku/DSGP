import os
import re
import spacy
import pandas as pd
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

# Load text files
def load_text_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith("_text.txt"):
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                files.append((file, f.read()))
    return files

# Most relevant value extractor (returns float)
def extract_most_relevant_value(pattern, text):
    matches = re.findall(pattern, text)
    values = []
    for match in matches:
        numbers = re.findall(r"[\d.,]+", match)
        if numbers:
            try:
                val = float(numbers[0].replace(",", ""))
                values.append(val)
            except:
                continue
    return max(values) if values else None

# Core keyword logic
def process_text(filename, text):
    lowered = text.lower()

    acts_count = sum(1 for w in gazette_keywords["policy_actions"] if w.lower() in lowered)
    rescinded_flag = 1 if "rescinded" in lowered or "revoked" in lowered else 0
    fuel_related_flag = any(word.lower() in lowered for word in gazette_keywords["fuel_types"])

    # Special use case weights
    special_weight = 0
    for word in gazette_keywords["special_use_cases"]:
        if word.lower() in lowered:
            special_weight += special_case_weights.get(word, 1)

    # Impact classification (1: Positive, 0: Negative/Default)
    if any(w in lowered for w in ["exempt", "concession", "reduction", "remove", "decrease"]):
        impact = 1
    elif any(w in lowered for w in ["duty", "levy", "increase", "tax imposed", "additional"]):
        impact = 0
    else:
        impact = 0

    # Clean numeric value extraction
    money = extract_most_relevant_value(r"(?:LKR|Rs\.?|rupees)?\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?", text)
    percent = extract_most_relevant_value(r"\d{1,3}(?:\.\d+)?\s?%", text)

    return {
        "filename": filename,
        "acts_count": acts_count,
        "rescinded_flag": rescinded_flag,
        "special_case_weight": special_weight,
        "impact": impact,
        "most_relevant_money": money,
        "most_relevant_percent": percent,
        "fuel_related_flag": 1 if fuel_related_flag else 0
    }

# Pipeline
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
