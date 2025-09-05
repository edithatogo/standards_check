import docx
import sys

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file and return as string"""
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_docx.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        content = extract_text_from_docx(file_path)
        print(content)
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        sys.exit(1)