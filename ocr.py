# Install required packages
# python3 -m venv venv
# pip install pytesseract pdf2image opencv-python numpy
# Also install tesseract-ocr and Hebrew language data
# brew install tesseract
# brew install poppler
# brew install tesseract-lang


import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
import sys

# Set the TESSDATA_PREFIX environment variable (do this before importing pytesseract)
os.environ['TESSDATA_PREFIX'] = '~/workspace/ocr-hebpdf2text/venv/bin/pytesseract'  # Modify this path to where you have the language data

# Configure Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'tesseract'  # Change if needed

# Test if Hebrew language is available
try:
    langs = pytesseract.get_languages()
    print(f"Available languages: {langs}")
    if 'heb' not in langs:
        print("Hebrew language pack not found. Please install it following the instructions.")
        sys.exit(1)
except Exception as e:
    print(f"Error checking languages: {e}")
    sys.exit(1)

def process_pdf(pdf_path, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Process each image (each containing two pages)
    for i, img in enumerate(images):
        # Convert PIL image to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Get dimensions
        height, width = img_cv.shape[:2]
        
        # Split into left and right pages
        left_page = img_cv[:, :width//2]
        right_page = img_cv[:, width//2:]
        
        # Process each page
        process_page(left_page, f"{output_dir}/page_{i}_left.txt")
        process_page(right_page, f"{output_dir}/page_{i}_right.txt")
    
    # Combine all text files
    combine_text_files(output_dir)

def process_page(img, output_file):
    # For Hebrew documents with two columns
    height, width = img.shape[:2]
    
    # Split into right and left columns (for a single page)
    right_column = img[:, :width//2]  # In Hebrew, this is the first column
    left_column = img[:, width//2:]   # Second column
    
    # Extract text from each column
    # Note: For Hebrew, we use 'heb' language
    right_text = pytesseract.image_to_string(right_column, lang='heb')
    left_text = pytesseract.image_to_string(left_column, lang='heb')
    
    # Save to file (right column first as Hebrew reads right-to-left)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(right_text + '\n\n' + left_text)

def combine_text_files(directory):
    # Combine all text files in the correct order
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
    with open(f"{directory}/complete_book.txt", 'w', encoding='utf-8') as outfile:
        for file in files:
            with open(f"{directory}/{file}", 'r', encoding='utf-8') as infile:
                outfile.write(infile.read() + '\n\n')

if __name__ == "__main__":
    pdf_path = "sefer.pdf"  # Replace with your PDF path
    output_dir = "extracted_text"
    
    process_pdf(pdf_path, output_dir)
    print(f"Text extraction complete. Full text available at: {output_dir}/complete_book.txt")