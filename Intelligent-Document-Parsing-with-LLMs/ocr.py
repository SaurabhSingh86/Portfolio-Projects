import pytesseract
from PIL import Image
import io
from pyzbar.pyzbar import decode
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF for PDF handling

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def process_documents(file_bytes, filename):
    """Extract raw text using OCR from image or PDF"""
    text = ""
    
    print("OCR filename: ", filename)

    # Handle PDF files
    if filename and filename.lower().endswith("pdf"):
        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(pdf_doc)):
            # Process PDF
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text += pytesseract.image_to_string(img) + "\n"
            pdf_doc.close()
        return text.strip()

    # Handle image files (jpg, jpeg, png, etc.)
    else:
        # Process Image (JPG, PNG, etc.)
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image).strip()


def scan_qr_barcode(file_bytes, doc_type, filename):
    """
    Scan QR/Barcode for different documents
    """
    images = []
    print("scan_qr_barcode_file_name: ", filename)

    # Handle PDF
    if filename.lower().endswith(".pdf"):
        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            pix = page.get_pixmap()
            images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    else:
        images.append(Image.open(io.BytesIO(file_bytes)))

    # Try decoding QR/Barcode in each image
    for image in images:
        decoded_objs = decode(image)
        if not decoded_objs:
            continue

        qr_data = decoded_objs[0].data.decode("utf-8")
        print("\nqr_data: ", qr_data)

        # Aadhaar & PAN (XML QR)
        if doc_type.lower() in ["aadhaar", "pan"]:
            try:
                root = ET.fromstring(qr_data)
                data = {
                    "Name": root.attrib.get("name"),
                    "DOB": root.attrib.get("dob"),
                    "Gender": root.attrib.get("gender"),
                }
                if doc_type.lower() == "aadhaar":
                    address = root.attrib.get("Address", "")
                    Father_Husband_Name = root.attrib.get("co", "")
                    Father_Husband_Name = Father_Husband_Name.replace("S/O:", "").strip() # S/O (Son Of)
                    Father_Husband_Name = Father_Husband_Name.replace("D/O:", "").strip() # S/O (Son Of)
                    # Father_Husband_Name = Father_Husband_Name.replace("S/O:", "").strip()
                    
                    if not address:
                        house = root.attrib.get("house", "")
                        street = root.attrib.get("street", "")
                        loc = root.attrib.get("loc", "")
                        vtc = root.attrib.get("vtc", "")
                        po = root.attrib.get("po", "")
                        dist = root.attrib.get("dist", "")
                        subdist = root.attrib.get("subdist", "")
                        state = root.attrib.get("state", "")
                        pc = root.attrib.get("pc")
                        
                        address = f"{house} {street} {loc} {vtc} {po} {dist} {subdist} {state} {pc}"
                        
                    data.update({
                        "Aadhaar Number": root.attrib.get("uid"),
                        "Father/Husband Name": Father_Husband_Name,
                        "Address": address
                    })
                elif doc_type.lower() == "pan":
                    data.update({
                        "PAN Number": root.attrib.get("pan"),
                        "Father Name": root.attrib.get("fathers_name")
                    })
                    
                print("data: ", data)
                return data
            except Exception:
                return None

        # Passport (PDF417 Barcode)
        elif doc_type.lower() == "passport":
            try:
                return {"barcode_data": qr_data}
            except Exception:
                return None

    return None


if __name__ == "__main__":
    pass
