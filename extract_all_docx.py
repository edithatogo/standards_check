import os
from utils.docx_utils import extract_text_from_docx

def main():
    # Directory containing DOCX files
    docx_dir = "docx/variants"
    
    if not os.path.exists(docx_dir):
        print(f"Directory {docx_dir} not found")
        return
    
    print(f"Available DOCX files in {docx_dir}:")
    docx_files = []
    for file in os.listdir(docx_dir):
        if file.endswith(".docx"):
            docx_files.append(file)
            print(f"  {file}")
    
    # Extract content from all DOCX files
    for docx_file in docx_files:
        file_path = os.path.join(docx_dir, docx_file)
        print(f"\nExtracting content from {file_path}:")
        content = extract_text_from_docx(file_path)
        
        if content:
            # Create a temp markdown file name by replacing .docx with -temp.md
            temp_file_name = docx_file.replace(".docx", "-temp.md")
            with open(temp_file_name, "w") as f:
                f.write(content)
            print(f"Content extracted and saved to {temp_file_name}")
        else:
            print(f"Failed to extract content from {docx_file}")

if __name__ == "__main__":
    main()
