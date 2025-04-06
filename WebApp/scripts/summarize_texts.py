# scripts/summarize_texts.py

import os
import re
import spacy
import pandas as pd
from dateutil import parser
from gazette_keywords import gazette_keywords

nlp = spacy.load("en_core_web_sm")

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
    return [
        (file, open(os.path.join(directory, file), "r", encoding="utf-8").read())
        for file in os.listdir(directory) if file.endswith("_text.txt")
    ]

def extract_most_relevant_value(pattern, text):
    values = []
    for match in re.findall(pattern, text):
        try:
            val = float(re.findall(r"[\d.,]+", match)[0].replace(",", ""))
            values.append(val)
        except:
            continue
    return max(values) if values else None

def extract_latest_month_year(text, filename=None):
    date_strings = re.findall(
        r"(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(?:January|February|...|December)\s+\d{4}", 
        text, re.IGNORECASE
    )
    if filename:
        date_strings += re.findall(r"\d{4}[_\-]?\d{2}", filename)
    parsed_dates = [parser.parse(ds, fuzzy=True) for ds in date_strings if ds]
    return max(parsed_dates).strftime("%B %Y") if parsed_dates else None

def process_text(filename, text):
    lowered = text.lower()
    acts_count = sum(1 for word in gazette_keywords["policy_actions"] if word.lower() in lowered)
    rescinded_flag = int("rescinded" in lowered or "revoked" in lowered)
    fuel_related_flag = int(any(w.lower() in lowered for w in gazette_keywords["fuel_types"]))

    special_weight = sum(
        special_case_weights.get(word, 1) 
        for word in gazette_keywords["special_use_cases"] if word.lower() in lowered
    )

    if any(w in lowered for w in ["exempt", "concession", "reduction"]):
        impact = 1
    elif any(w in lowered for w in ["duty", "levy", "increase"]):
        impact = 0
    else:
        impact = -1

    money = extract_most_relevant_value(r"(?:LKR|Rs\.?)?\s?\d+(?:,\d{3})*(?:\.\d+)?", text)
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
        "fuel_related_flag": fuel_related_flag,
        "effective_date": effective_date
    }

if __name__ == "__main__":
    input_dir = "data/extracted_data"
    df = pd.DataFrame([process_text(file, text) for file, text in load_text_files(input_dir)])
    df.to_csv("data/gazette_summary.csv", index=False)
    print("✔ Gazette summary saved.")
