import json
import os
import glob
import pandas as pd
from datetime import datetime

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'agoda_reviews_cleaned.json')

def clean_and_merge():
    # 1. Find all JSON files (exclude buffer/temp files if any)
    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    json_files = [f for f in json_files if 'cleaned' not in f and 'schema' not in f]
    
    if not json_files:
        print("No JSON files found to process.")
        return

    print(f"Found {len(json_files)} files: {[os.path.basename(x) for x in json_files]}")

    all_reviews = []

    # 2. Extract and Flatten
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both list of hotels or single hotel dict
                if isinstance(data, dict): data = [data]
                
                for hotel in data:
                    hotel_name = hotel.get('hotel_name', 'Unknown')
                    reviews = hotel.get('reviews', [])
                    
                    for r in reviews:
                        # Flatten for DataFrame
                        item = r.copy()
                        item['hotel_name'] = hotel_name
                        all_reviews.append(item)
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if not all_reviews:
        print("No reviews extracted.")
        return

    # 3. Deduplicate using Pandas
    df = pd.DataFrame(all_reviews)
    
    # Check duplicates based on composite key
    initial_count = len(df)
    
    # Ensure review_date is consistent for dedup
    # We don't parse it to date object here to keep JSON serializable easily, 
    # but we rely on string exact match. 
    # If date formats vary, we might need normalization. 
    # For now assuming consistent "Reviewed Month DD, YYYY" from scraper.
    
    df.drop_duplicates(subset=['hotel_name', 'reviewer_name', 'review_date'], keep='first', inplace=True)
    
    final_count = len(df)
    print(f"Removed {initial_count - final_count} duplicate reviews. Total unique: {final_count}")

    # 4. Reconstruct JSON Structure (List of Hotels -> List of Reviews)
    # Group by hotel_name to match original structure expected by init_db.py
    grouped = df.groupby('hotel_name')
    
    output_data = []
    for hotel_name, group in grouped:
        # Convert group back to list of dicts, removing hotel_name from inner dict if desired
        # or keeping it is fine. init_db expects 'reviews' list.
        
        # Drop hotel_name from inner dicts to match original schema (optional but cleaner)
        reviews_list = group.drop(columns=['hotel_name']).to_dict(orient='records')
        
        hotel_entry = {
            "hotel_name": hotel_name,
            "reviews": reviews_list,
            "reviews_count": len(reviews_list)
        }
        output_data.append(hotel_entry)

    # 5. Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved cleaned data to: {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_and_merge()
