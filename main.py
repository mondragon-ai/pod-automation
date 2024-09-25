import csv
import os
from PIL import Image 
# import urllib.request



# Wasatch SoftRIP API connection details
wasatchSoftRIP = '127.0.0.1:80'  
printUnit = 1  

# Layout parameters for S-3XL and 4XL-5XL
layout_params = {
    "S-3XL": {"width": 11.0, "height": 0.0},
    "4XL-5XL": {"width": 12.0, "height": 0.0}  
}

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
    

# Function to create a layout and submit it to Wasatch SoftRIP for printing
def create_and_submit_layout(image_queue):
    url = f'http://{wasatchSoftRIP}/xmlSubmission.dyn?'
    data = '<WASATCH ACTION=JOB><PRINTUNIT>' + str(printUnit) + '</PRINTUNIT>'
    data += '<LAYOUT NOTES="From Python Hot Folder">'
    
    x = 0.0 
    y = 0.0 
    count = 0
    max_columns = 2
    horizontal_gap = 0.25
    vertical_gap = 0.5

    for image, sku_category in image_queue:
        width = layout_params[sku_category]["width"]
        image_height = get_image_height(image, width)
        
        # Add image to layout
        data += f'<PAGE XPOSITION={x} YPOSITION={y}>'
        data += f'<FILENAME>{image}</FILENAME>'
        data += '<DELETEAFTERPRINT /></PAGE>'
        
        # Update X and Y positions
        x += width + horizontal_gap
        count += 1

        # After filling a row, reset x and move to the next row
        if count >= max_columns:
            x = 0.0
            y += image_height + vertical_gap
            count = 0

    data += '</LAYOUT></WASATCH>'

    print(url)
    print(data)
    
    # Submit the job to Wasatch
    # url += urllib.parse.quote_plus(data)
    # try:
    #     p = urllib.request.urlopen(url)
    #     response = p.read()
    #     p.close()
    #     print("Layout submitted successfully.")
    # except Exception as e:
    #     print(f"Failed to submit layout: {e}")



# Function to get the real image height based on the width
def get_image_height(image_path, target_width):
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            
            # Calculate the new height proportional to the target width
            aspect_ratio = original_height / original_width
            target_height = target_width * aspect_ratio
            
            return target_height
    except Exception as e:
        print(f"Error getting image size for {image_path}: {e}")
        return layout_params['S-3XL']["height"] 

# Function to create an image queue based on SKU counts
def create_image_queue(sku_dict, images_folder):
    image_queue = []
    
    # Add 'S-3XL' SKUs to the queue first
    for sku, count in sorted(sku_dict.items()):
        if 'S-3XL' in sku:
            image_path = find_image_for_sku(sku, images_folder)
            if image_path:
                for _ in range(count):
                    image_queue.append((image_path, 'S-3XL'))

    # Add '4XL-5XL' SKUs to the queue afterward
    for sku, count in sorted(sku_dict.items()):
        if '4XL-5XL' in sku:
            image_path = find_image_for_sku(sku, images_folder)
            if image_path:
                for _ in range(count):
                    image_queue.append((image_path, '4XL-5XL'))

    return image_queue

# Function to find the image for a given SKU
def find_image_for_sku(sku, images_folder):
    image_file = f"{sku}.png"
    image_path = os.path.join(images_folder, image_file)
    
    if os.path.exists(image_path):
        return image_path
    else:
        print(f"Image not found for SKU: {sku}")
        return None

# Example usage
def main():
    file_path = 'pick.csv' 
    images_folder = './images' 

    sku_count = process_csv(file_path)

    # Print the result
    for sku, count in sku_count.items():
        print(f"{sku}: {count}")

    image_queue = create_image_queue(sku_count, images_folder)

    # Print the image queue (for testing purposes)
    for image in image_queue:
        print(image)

    create_and_submit_layout(image_queue)

if __name__ == "__main__":
    main()
