#!/usr/bin/env python3
"""
PDF text extraction script for automated content extraction from source PDFs.
This script uses pdfplumber to extract text from PDF files and save it to text files.
"""

import pdfplumber
import os
import sys
import argparse
from pathlib import Path

def extract_text_from_pdf(pdf_path, output_path=None):
    """
    Extract text from a PDF file and save it to a text file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str): Path to the output text file (optional)
    
    Returns:
        str: Extracted text content
    """
    try:
        # Extract text from PDF
        text_content = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text()
                text_content += "\n\n"  # Add spacing between pages
        
        # If no output path specified, create one based on PDF name
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}_extracted.txt"
        
        # Save extracted text to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Successfully extracted text from {pdf_path}")
        print(f"Output saved to {output_path}")
        return text_content
    
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def extract_multiple_pdfs(source_dir, output_dir):
    """
    Extract text from all PDF files in a directory.
    
    Args:
        source_dir (str): Directory containing PDF files
        output_dir (str): Directory to save extracted text files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all PDF files in source directory
    pdf_files = list(Path(source_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {source_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        output_file = Path(output_dir) / f"{pdf_file.stem}_extracted.txt"
        extract_text_from_pdf(str(pdf_file), str(output_file))

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("pdf_path", nargs="?", help="Path to PDF file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory path")
    parser.add_argument("-d", "--directory", action="store_true", 
                        help="Process all PDFs in a directory")
    
    args = parser.parse_args()
    
    if not args.pdf_path:
        print("Please provide a PDF file or directory path")
        parser.print_help()
        sys.exit(1)
    
    if args.directory:
        extract_multiple_pdfs(args.pdf_path, args.output or "extracted_text")
    else:
        extract_text_from_pdf(args.pdf_path, args.output)

if __name__ == "__main__":
    main()