import pandas as pd
import os

# Load the Excel file
excel_file_path = '/Users/andresrdrgz_/Documents/PACIFICO/financiera/pacifico/fideicomiso/patronos.xlsx'
df = pd.read_excel(excel_file_path)

# Define the JSON file path
json_file_path = '/Users/andresrdrgz_/Documents/PACIFICO/financiera/pacifico/fideicomiso/patronos.json'

# Ensure the directory exists
os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

# Convert the DataFrame to a JSON file
df.to_json(json_file_path, orient='records', lines=True)

print(f"Excel file has been converted to JSON and saved to {json_file_path}")