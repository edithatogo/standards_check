import docx
import os

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file and return as string"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None

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
        safe_filename = os.path.basename(docx_file)
        file_path = os.path.join(docx_dir, safe_filename)
        print(f"\nExtracting content from {file_path}:")
        content = extract_text_from_docx(file_path)
        
        if content:
            # Create a temp markdown file name by replacing .docx with -temp.md
            temp_file_name = safe_filename.replace(".docx", "-temp.md")
            with open(temp_file_name, "w") as f:
                f.write(content)
            print(f"Content extracted and saved to {temp_file_name}")
        else:
            print(f"Failed to extract content from {safe_filename}")

if __name__ == "__main__":
    main()