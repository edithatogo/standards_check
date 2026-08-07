import os
from utils.docx_utils import extract_text_from_docx

if __name__ == "__main__":
    # List all DOCX files in the directory
    docx_dir = "docx/variants"
    if os.path.exists(docx_dir):
        print(f"Available DOCX files in {docx_dir}:")
        for file in os.listdir(docx_dir):
            if file.endswith(".docx"):
                print(f"  {file}")
    
    # Try to extract content from consort-cluster-crossover.docx
    file_path = "docx/variants/consort-cluster-crossover.docx"
    if os.path.exists(file_path):
        print(f"\nExtracting content from {file_path}:")
        content = extract_text_from_docx(file_path)
        if content:
            # Save to a file
            with open("consort-cluster-crossover-content.txt", "w") as f:
                f.write(content)
            print("Content extracted and saved to consort-cluster-crossover-content.txt")
            # Print first 1000 characters
            print("\nFirst 1000 characters of content:")
            print(content[:1000])
        else:
            print("Failed to extract content")
    else:
        print(f"File {file_path} not found")
