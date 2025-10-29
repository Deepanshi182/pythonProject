import os
from pdfminer.high_level import extract_text as extract_pdf_text
import docx

ALLOWED_EXT = {'.pdf', '.docx'}

def extract_text_from_pdf(path):
    try:
        return extract_pdf_text(path)
    except Exception as e:
        print('PDF extraction error:', e)
        return ''




def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        full = []
        for para in doc.paragraphs:
            full.append(para.text)
        return '\n'.join(full)
    except Exception as e:
        print('DOCX extraction error:', e)
        return ''




def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.docx':
        return extract_text_from_docx(path)
    else:
        return ''
