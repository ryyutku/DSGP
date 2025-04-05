
# pip install pdfplumber camelot-py[cv] pytesseract opencv-python

"""## **Extract Text and Tables from PDFs**"""

import pdfplumber # extracts paragraph style text and sometimes basic tables
import camelot # extracting well structured tables
# pytesseract - reads images from an image, like a human would (readable -> searchable text)
import os

def extract_text_from_pdf(pdf_path):
  text = ""
  with pdfplumber.open(pdf_path) as pdf: #opens pdf as an object with .pages
    for page in pdf.pages:
      text += page.extract_text() # extract all visible paragraphs-like text (ignoring images)
      #concatenate text from each page with new lines
      # result will be a raw text dump
  return text

# Extracting tables from PDF
def extract_tables_from_pdf(pdf_path, output_dir):
  tables = camelot.read_pdf(pdf_path, pages='all') # scans pdf for visually availabe tables
  print(f"Found {tables.n} tables.") # tells how many tables are present
  for i, table in enumerate(tables): # each table is a camelot table that acts as pd dataframe
    output_file = os.path.join(output_dir, f"table_{i+1}.csv")
    table.to_csv(output_file) # to get the results in csv
    print(f"saved table to {output_file}")
  return tables

# Running the Script
if __name__ == "__main__":
    input_dir = "gazettes"        #  Folder containing your gazette PDFs
    output_dir = "extracted_data" #  Folder to save the extracted text and tables

    os.makedirs(output_dir, exist_ok=True)

    # Loop through all PDF files in the input folder
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(input_dir, filename)
            print(f"\n Processing: {filename}")

            # 1. Extract and save text
            text = extract_text_from_pdf(pdf_file)
            text_filename = f"{os.path.splitext(filename)[0]}_text.txt"
            with open(os.path.join(output_dir, text_filename), "w", encoding="utf-8") as f:
                f.write(text)
            print(f" Text saved to {text_filename}")

            # 2. Extract and save tables
            file_output_dir = os.path.join(output_dir, os.path.splitext(filename)[0])
            os.makedirs(file_output_dir, exist_ok=True)
            extract_tables_from_pdf(pdf_file, file_output_dir)
