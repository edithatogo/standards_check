import docx

def extract_text_from_docx(file_path):
    """Return paragraph text, allowing callers to choose their error policy."""
    document = docx.Document(file_path)
    return '\n'.join(paragraph.text for paragraph in document.paragraphs)
