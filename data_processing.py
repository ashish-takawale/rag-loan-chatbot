import json
import os
import re

# --- CONFIGURATION ---
# This is the (already clean) file you provided
INPUT_FILE = "loans_unstructured.json" 

# This is the final, official "knowledge base" file
OUTPUT_FILE = "loans_bom.json" 
# ---------------------

def clean_text(text):
    """A helper function to clean text fields."""
    if not isinstance(text, str):
        return text
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Fix common unicode issues (though not apparent in your file)
    text = text.replace(u'\u2019', "'").replace(u'\u201c', '"').replace(u'\u201d', '"')
    return text

def process_scheme(scheme):
    """
    Cleans and validates a single loan scheme.
    Since the input data is already very structured, this is mostly
    about standardizing formats and trimming whitespace.
    """
    cleaned_scheme = {}
    for key, value in scheme.items():
        if isinstance(value, str):
            cleaned_scheme[key] = clean_text(value)
        elif isinstance(value, list):
            cleaned_scheme[key] = [clean_text(item) for item in value if item]
        elif isinstance(value, dict):
            cleaned_scheme[key] = {k: clean_text(v) for k, v in value.items() if v}
        else:
            cleaned_scheme[key] = value
            
    # Ensure critical keys exist, even if empty
    if 'url' not in cleaned_scheme:
        cleaned_scheme['url'] = "No URL provided"
    if 'scheme_name' not in cleaned_scheme:
        cleaned_scheme['scheme_name'] = "Unnamed Scheme"
        
    return cleaned_scheme

def main():
    print(f"Starting data processing...")
    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")

    # Load the unstructured (but already clean) data
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Input file not found: {INPUT_FILE}")
        print("Please ensure your 'loans_unstructured.json' file is in the same directory.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: Could not decode JSON from {INPUT_FILE}.")
        return

    # This will be our new, clean data structure
    clean_data = {
        "bank_name": data.get("bank_name", "Unknown Bank"),
        "data_collection_date": data.get("data_collection_date", "Unknown Date"),
        "loan_categories": {}
    }

    if "loan_categories" not in data:
        print("Warning: 'loan_categories' key not found in input.")
        return

    # Iterate through and clean the data
    for category_key, category in data["loan_categories"].items():
        clean_category = {
            "category_name": category.get("category_name", "Unnamed Category"),
            "schemes": []
        }
        
        for scheme in category.get("schemes", []):
            cleaned_scheme = process_scheme(scheme)
            clean_category["schemes"].append(cleaned_scheme)
        
        clean_data["loan_categories"][category_key] = clean_category

    # Save the processed data to the new file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Success! Processed data saved to: {OUTPUT_FILE}")
    except IOError as e:
        print(f"❌ ERROR: Could not write to output file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main()