# pip install spacy pandas
# python -m spacy download en_core_web_sm

import os
import re
import spacy 
# for NLP tasks (NER) -> Named Entity Recognition
import pandas as pd # to structure the output
from gazette_keywords import gazette_keywords # importing keyword dictionary


nlp = spacy.load("en_core_web_sm")

# For reading the files
def load_text_files(directory): # gets folder path
    text_files = [] # store text files, as (filename, text) pairs
    for filename in os.listdir(directory): # go through every file in folder
        if filename.endswith("_text.txt"): # process file ending with txt
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
                text = f.read() # read entire content of file as a string
                text_files.append((filename, text)) # store contents of the file as a list

    return text_files # return list of file+text data

# Defining pattern Extraction Functions
def extract_dates(text): # Helps extract dates
    pattern = r"\b\d{1,2}(st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b"
    return re.findall(pattern, text)

def extract_money_percent(text): # For extracting money and percentages
    money_pattern = r"(?:LKR|Rs\.?|rupees)\s?\d+(?:,\d{3})*(?:\.\d+)?"
    percent_pattern = r"\d{1,3}%"
    return re.findall(money_pattern, text), re.findall(percent_pattern, text)

def extract_keywords(text, keywords): # If matching word is found from the dictionary we add it to the list of found words
    found = {}
    for category, words in keywords.items():
        found[category] = []
        for word in words:
            if word.lower() in text.lower():
                found[category].append(word)
    
    return found


# Process all text files and output data
def process_gazettes(directory):
    all_data = []
    files = load_text_files(directory) # load all gazette files with .txt

    for filename, text in files:
        print(f"Processing {filename}...")
        doc = nlp(text)
         
        # Loop through files and extract dates, money, percentages, keywords -> each result will be stord in data and save all into all_data
        dates = extract_dates(text)
        money, percents = extract_money_percent(text)
        keywords = extract_keywords(text, gazette_keywords)

        data = {
            "filename": filename,
            "dates": [f"{d[0]} {d[1]} {text.split(d[1])[1][:5]}" for d in dates],  # reconstruct readable format
            "money_values": money,
            "percentages": percents
        }

        # Add keywords categories
        for category, matches in keywords.items():
            data[category] = ", ".join(matches)

        all_data.append(data)
    return pd.DataFrame(all_data)


# Running the whole thing and save csv
if __name__ == "__main__":
    input_dir = "extracted_data"
    df = process_gazettes(input_dir)
    df.to_csv("gazette_insights.csv", index=False)
    print("Extracted data saved to file")