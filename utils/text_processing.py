import fitz
import re

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a given PDF file.
    Accepts either a file path (str) or a file-like object (e.g. from Streamlit's file_uploader).
    """
    text = ""
    try:
        # If pdf_file is a file-like object, read its bytes
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc = fitz.open(pdf_file)
            
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
            
        doc.close()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        
    return text

def clean_text(text: str) -> str:
    """
    Cleans the input text by removing URLs, newlines, and extra whitespaces.
    Keeps punctuation because sentence transformers benefit from full context.
    """
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Replace newlines and tabs with spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespaces
    return text.strip()
