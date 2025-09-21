# fast_api.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ocr import process_documents, scan_qr_barcode
from llm import parse_with_llm
import pandas as pd
from pydantic import BaseModel
import uuid
import dbApi
import mysql.connector

app = FastAPI(title="Document Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def transform_data(response):
    return {
        "File Name": response.get("filename"),
        "Doc Type": response.get("Doc Type"),
        "Name": response.get("parsed_data", {}).get("name") or response.get("parsed_data", {}).get("Name"),
        "DOB": response.get("parsed_data", {}).get("dob") or response.get("parsed_data", {}).get("DOB"),
        "Gender": response.get("parsed_data", {}).get("gender") or response.get("parsed_data", {}).get("Gender"),
        "Aadhaar Number": response.get("parsed_data", {}).get("aadhaar_no") or response.get("parsed_data", {}).get("Aadhaar Number"),
        "Address": response.get("parsed_data", {}).get("address") or response.get("parsed_data", {}).get("Address"),
        "Father/Husband Name": response.get("parsed_data", {}).get("Father/Husband Name") or response.get("parsed_data", {}).get("S/O (Son Of)"),
        "PAN Number": response.get("parsed_data", {}).get("PAN Number"),
        "Passport Number": response.get("parsed_data", {}).get("Passport Number") or response.get("parsed_data", {}).get("barcode_data"),
        "Expiry Date": response.get("parsed_data", {}).get("Expiry Date"),
        "Nationality": response.get("parsed_data", {}).get("Nationality"),
    }

@app.post("/doc-ai/upload/")
async def upload(file: UploadFile = File(...), doc_type: str = Form(...)):
    try:
        file_bytes = await file.read()

        parsed = scan_qr_barcode(file_bytes, doc_type, file.filename)
        if not parsed:
            print("\n---------------- LLM ----------------------------")
            raw_text = process_documents(file_bytes, file.filename)
            parsed = parse_with_llm(doc_type.lower(), raw_text)

        response = {
            "filename": file.filename,
            "Doc Type": doc_type,
            "parsed_data": parsed
        }

        print("\n API response: ", response)
        # 👇 Transform into clean tabular format
        cleaned = transform_data(response)

        return JSONResponse(content=cleaned)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})




# ---------- Request Model ----------
class SaveRequest(BaseModel):
    data: dict
    

@app.post("/doc-ai/save/")
def save_document(req: SaveRequest):
    print("📩 Incoming request:", req.dict())
    try:
        cleaned_data = {k: v for k, v in req.data.items() if k and v}
        print("cleaned_data: ", cleaned_data)
        print("cleaned_data: ", type(cleaned_data))
        employee_id = dbApi.save_emp_info(cleaned_data)

        return {"status": "ok", "employee_id": f"E{employee_id:03d}"}

    except mysql.connector.IntegrityError as e:
        if "aadhaar_number" in str(e):
            raise HTTPException(status_code=400, detail="❌ Duplicate Aadhaar Number found!")
        elif "pan_number" in str(e):
            raise HTTPException(status_code=400, detail="❌ Duplicate PAN Number found!")
        elif "passport_number" in str(e):
            raise HTTPException(status_code=400, detail="❌ Duplicate Passport Number found!")
        else:
            raise HTTPException(status_code=400, detail="❌ Duplicate entry found!")


    except Exception as e:
        # Handle MySQL duplicate entry error explicitly
        if "1062" in str(e):  
            raise HTTPException(
                status_code=400, 
                detail="⚠️ Employee with this Aadhaar Number already exists."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")