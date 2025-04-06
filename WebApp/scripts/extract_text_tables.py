# scripts/extract_text_tables.py

import os
import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # handle None values
    return text

if __name__ == "__main__":
    input_dir = "data/gazettes"
    output_dir = "data/extracted_data"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(input_dir, filename)
            print(f"\nProcessing: {filename}")

            text = extract_text_from_pdf(pdf_file)
            text_filename = f"{os.path.splitext(filename)[0]}_text.txt"
            with open(os.path.join(output_dir, text_filename), "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✔ Text saved to {text_filename}")
