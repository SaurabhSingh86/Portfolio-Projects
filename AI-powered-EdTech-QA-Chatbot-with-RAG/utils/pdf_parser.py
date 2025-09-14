import pdfplumber
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_pdfplumber(file) -> str:
    """Try extracting text with pdfplumber"""
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def extract_text_pypdf2(file) -> str:
    """Fallback using PyPDF2"""
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        try:
            txt = page.extract_text()
            if txt:
                text.append(txt)
        except:
            continue
    return "\n".join(text)


def extract_text_ocr(file) -> str:
    """Final fallback: OCR for scanned PDFs"""
    text = []
    images = convert_from_bytes(file.read())  # convert each page to image
    for i, img in enumerate(images):
        txt = pytesseract.image_to_string(img)
        if txt.strip():
            text.append(txt)
    return "\n".join(text)


def extract_text_from_pdf(file) -> str:
    """
    Extract text from PDF with multiple fallbacks.
    Priority: pdfplumber → PyPDF2 → OCR.
    """
    text = ""
    try:
        text = extract_text_pdfplumber(file)
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    if not text.strip():
        try:
            text = extract_text_pypdf2(file)
        except Exception as e:
            print(f"PyPDF2 failed: {e}")

    if not text.strip():
        try:
            # reset file pointer for OCR
            file.seek(0)
            text = extract_text_ocr(file)
        except Exception as e:
            print(f"OCR failed: {e}")

    if not text.strip():
        return "⚠️ Could not extract text from this PDF. Even OCR failed."
    
    return text

