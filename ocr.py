# Install required packages
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
        
        # Extract all four columns in the correct Hebrew reading order (RTL)
        extract_hebrew_columns(img_cv, i, output_dir)
    
    # Combine all text files
    combine_text_files(output_dir)

def extract_hebrew_columns(img, page_num, output_dir):
    # Looking at the scan as a single image with columns numbered 1,2,3,4 from right to left
    # The correct Hebrew reading order is 1,2,3,4 (RTL)
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Calculate column widths
    col_width = width // 4
    
    # Extract each column in RIGHT-TO-LEFT order
    col1 = img[:, width - col_width:]       # Rightmost column (#1 in Hebrew)
    col2 = img[:, width - 2*col_width:width - col_width]  # Second from right (#2)
    col3 = img[:, col_width:width - 2*col_width]  # Third from right (#3)
    col4 = img[:, :col_width]               # Leftmost column (#4)
    
    # Extract text from each column in Hebrew reading order (right to left)
    text1 = pytesseract.image_to_string(col1, lang='heb')  # First in reading order
    text2 = pytesseract.image_to_string(col2, lang='heb')  # Second
    text3 = pytesseract.image_to_string(col3, lang='heb')  # Third
    text4 = pytesseract.image_to_string(col4, lang='heb')  # Fourth
    
    # Save to file in correct reading order (1,2,3,4)
    with open(f"{output_dir}/page_{page_num:03d}.txt", 'w', encoding='utf-8') as f:
        f.write(text1 + '\n\n' + text2 + '\n\n' + text3 + '\n\n' + text4)

def combine_text_files(directory):
    # Combine all text files in the correct order
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt') and not f == "complete_book.txt"])
    
    with open(f"{directory}/complete_book.txt", 'w', encoding='utf-8') as outfile:
        for file in files:
            with open(f"{directory}/{file}", 'r', encoding='utf-8') as infile:
                outfile.write(infile.read() + '\n\n')

if __name__ == "__main__":
    pdf_path = "sefer.pdf"  # Replace with your PDF path
    output_dir = "extracted_text"
    
    process_pdf(pdf_path, output_dir)
    print(f"Text extraction complete. Full text available at: {output_dir}/complete_book.txt")