from fastapi import APIRouter, UploadFile, Form, File
from ocr import process_documents
import os

router = APIRouter()

@router.post("/upload/")
async def upload_document(file: UploadFile, doc_type: str = Form(...)):
    
    print("Upload file: ", file)
    print("Upload filename: ", file.filename)
    
    # Read file bytes
    content = await file.read()
    
    # Extract file extension from uploaded file
    filename = file.filename or "uploaded_file"
    print("filename: ", filename)
    ext = os.path.splitext(filename)[1].lower()

    # Pass both file bytes & filename (extension matters for PDF check)
    result = process_documents(content, filename=filename)

    return {
        "status": "success",
        "Doc Type": doc_type,
        "file_type": ext,
        "data": result
    }


