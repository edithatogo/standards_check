import docx
import os
import re

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

def convert_to_markdown_format(text, filename):
    """Convert extracted text to markdown format"""
    lines = text.split('\n')
    markdown_lines = []
    
    # Add title based on filename
    title = filename.replace('.docx', '').replace('-', ' ').title()
    markdown_lines.append(f"# {title} Checklist")
    markdown_lines.append("")
    
    # Add instructions
    markdown_lines.append("## Instructions")
    markdown_lines.append("- Use task list items for checklist boxes; these become interactive checkboxes in PDF.")
    markdown_lines.append("- Use a span with class `.textfield` for free‑text fields.")
    markdown_lines.append("- Report all applicable items from the checklist.")
    markdown_lines.append("")
    
    # Process lines to identify sections and items
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (all caps or title case)
        if line.isupper() or (line.istitle() and len(line.split()) <= 5):
            current_section = line
            markdown_lines.append(f"## {line}")
            markdown_lines.append("")
        # Check if this is a checklist item (starts with number or bullet)
        elif re.match(r'^\d+[\.\)]|^[a-zA-Z][\.\)]|^[\*\-\u2022]', line):
            # Clean up the line
            clean_line = re.sub(r'^[\d\w\*\-\u2022\.\)]+\s*', '', line)
            if clean_line:
                markdown_lines.append(f"- [ ] {clean_line}")
        # Regular text
        else:
            if line:
                markdown_lines.append(line)
    
    return '\n'.join(markdown_lines)

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
            # Convert to markdown format
            markdown_content = convert_to_markdown_format(content, safe_filename)
            
            # Create a temp markdown file name by replacing .docx with -extracted.md
            temp_file_name = safe_filename.replace(".docx", "-extracted.md")
            with open(temp_file_name, "w") as f:
                f.write(markdown_content)
            print(f"Content extracted and saved to {temp_file_name}")
        else:
            print(f"Failed to extract content from {safe_filename}")

if __name__ == "__main__":
    main()