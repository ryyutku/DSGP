import os
import pandas as pd

# ------------------- 1. Set Project Root -------------------

# Get the directory where this script is located
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ------------------- 2. Set Input and Output Paths -------------------

# Paths to the input data files
data_dir = os.path.join(PROJECT_ROOT, 'data')
ciec_csv_path = os.path.join(data_dir, 'ciec.csv')
gazette_csv_path = os.path.join(data_dir, 'gazette_insights.csv')

# Output directory
processed_dir = os.path.join(PROJECT_ROOT, 'processed')
os.makedirs(processed_dir, exist_ok=True)

# Output file path
output_csv_path = os.path.join(processed_dir, 'merged_fuel_data.csv')

# ------------------- 3. Debug Paths -------------------

print(f"📁 CIEC file path: {ciec_csv_path}")
print(f"📁 Gazette file path: {gazette_csv_path}")
print(f"📄 Output file will be saved to: {output_csv_path}")

# ------------------- 4. Check File Existence -------------------

if not os.path.exists(ciec_csv_path):
    raise FileNotFoundError(f"❌ Could not find CIEC data at: {ciec_csv_path}")
if not os.path.exists(gazette_csv_path):
    raise FileNotFoundError(f"❌ Could not find Gazette data at: {gazette_csv_path}")

# ------------------- 5. Load Data -------------------

ciec_df = pd.read_csv(ciec_csv_path)
gazette_df = pd.read_csv(gazette_csv_path)

# ------------------- 6. Convert 'Date' Columns -------------------

ciec_df['Date'] = pd.to_datetime(ciec_df['Date'])
gazette_df['Date'] = pd.to_datetime(gazette_df['Date'])

# ------------------- 7. Clean Gazette Data -------------------

gazette_df.fillna('', inplace=True)

# ------------------- 8. Merge Data -------------------

# Merge on 'Date', keeping all rows from CIEC
merged_df = pd.merge(ciec_df, gazette_df, on='Date', how='left')

# ------------------- 9. Save Output -------------------

merged_df.to_csv(output_csv_path, index=False)
print("✅ Merge successful! Saved merged data to:", output_csv_path)
