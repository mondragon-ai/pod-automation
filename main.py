import csv
from collections import Counter

# Function to read CSV and extract SKU information
def process_csv(file_path):
    sku_dict = {} 

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            sku = row['SKU']  
            parsed_sku = parse_sku(sku)
            if parsed_sku:
                base_sku, size_category = parsed_sku
                key = f"{base_sku}-{size_category}"
                if key in sku_dict:
                    sku_dict[key] += 1
                else:
                    sku_dict[key] = 1

    return sku_dict

# Function to parse SKU
def parse_sku(sku):
    parts = sku.split('-')
    
    if len(parts) < 4:
        return None  

    sku_type = parts[1] 
    if sku_type not in ["HD", "TS"]:
        return None 
    design = parts[2] 
    size = parts[-1]

    # Not sure if we should add more if the SKU is greater
    if len(parts) > 5:
        design += '-' + parts[3] 

    size_category = categorize_size(size)

    base_sku = f"{sku_type}-{design}"
    return base_sku, size_category

# Function to categorize size
def categorize_size(size):
    if size in ['S', 'M', 'L', 'XL', '2XL', '3XL']:
        return 'S-3XL'
    elif size in ['4XL', '5XL']:
        return '4XL-5XL'
    else:
        return 'Other' 

# Example usage
def main():
    file_path = 'pick.csv' 
    sku_count = process_csv(file_path)

    # Print the result
    for sku, count in sku_count.items():
        print(f"{sku}: {count}")

if __name__ == "__main__":
    main()
