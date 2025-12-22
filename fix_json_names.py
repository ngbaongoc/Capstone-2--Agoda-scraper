import json
import re

def fix_names(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    fixed_count = 0
    for hotel in data:
        if hotel.get('hotel_name') == "Unknown Hotel":
            url = hotel.get('hotel_url', '')
            # Extract name from URL: https://www.agoda.com/NAME-OF-HOTEL/hotel/...
            # Regex to find the part between .com/ and /hotel/
            match = re.search(r'\.com/([^/]+)/hotel/', url)
            if match:
                raw_name = match.group(1)
                # Clean up: replace hyphens with spaces, title case
                new_name = raw_name.replace('-', ' ').title()
                # Remove random suffixes if any (like digits) although title case helps
                hotel['hotel_name'] = new_name
                fixed_count += 1
                print(f"Fixed: {new_name}")
            else:
                print(f"Could not extract name for URL: {url}")

    print(f"Total fixed: {fixed_count}")
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    fix_names('data/custom_list_crawl.json')
