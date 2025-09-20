# confirm_page.py
import streamlit as st
import pandas as pd
from datetime import datetime
import requests
# import dbApi

API_SAVE_URL = "http://127.0.0.1:8003/doc-ai/save/" 

st.set_page_config(page_title="Confirm Employee Data", layout="wide")
st.title("✅ Confirm Extracted Employee Data")

# ------------------- Check for results -------------------
if "results" not in st.session_state or not st.session_state.results:
    st.error("⚠️ No extracted data found. Please upload documents first.")
    st.stop()

# ------------------- Extract & merge results -------------------
results = st.session_state.results

data = {}
EXCLUDE_KEYS = ["file name", "doc type", "doc_type"]

for res in results:
    for key, value in res.items():
        if key.lower() in EXCLUDE_KEYS:
            continue
        if key not in data:
            data[key] = []
        if value and value not in data[key]:
            data[key].append(value)

# ------------------- Editable form -------------------
st.subheader("📋 Review & Edit Data")

final_data = {}
col1, col2 = st.columns(2)

def parse_date(value):
    """Convert string date to datetime.date object"""
    if not value:
        return None
    try:
        # If already YYYY-MM-DD from calendar
        return datetime.fromisoformat(value).date()
    except Exception:
        try:
            # If string in DD/MM/YYYY format
            return datetime.strptime(value, "%d/%m/%Y").date()
        except Exception:
            return None

# Split fields into two columns
col1_fields = list(data.items())[: len(data)//2 + 1]
col2_fields = list(data.items())[len(data)//2 + 1:]

def render_fields(fields, column):
    for key, values in fields:
        if key.lower() == "gender":
            gender_map = {"M": "Male", "Male": "Male", "F": "Female", "Female": "Female", "O": "Other", "Other": "Other"}
            default_gender = gender_map.get(values[0], "Other") if values else "Other"
            final_data[key] = column.radio("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(default_gender))
        
        elif key.lower() in ["dob", "date of birth"]:
            dob_value = parse_date(values[0]) if values else datetime(1990,1,1).date()
            dob = column.date_input("Date of Birth (DOB)", value=dob_value, min_value=datetime(1900,1,1).date(), max_value=datetime.today().date())
            final_data[key] = dob.isoformat() if dob is not None else ""  # calendar returns YYYY-MM-DD
        
        elif key.lower() in ["expiry date", "expiry_date", "expiry"]:
            expiry_value = parse_date(values[0]) if values else datetime.today().date()
            # expiry = column.date_input("Expiry Date", value=expiry_value, min_value=datetime.today().date())
            expiry = column.date_input("Expiry Date", value=expiry_value)
            final_data[key] = expiry.isoformat()  # YYYY-MM-DD

        elif len(values) > 1:
            final_data[key] = column.selectbox(f"{key}", values, index=0)
        else:
            final_data[key] = column.text_input(f"{key}", values[0] if values else "")

with col1:
    render_fields(col1_fields, col1)
with col2:
    render_fields(col2_fields, col2)

# ------------------- Save Button -------------------
st.markdown("---")

def clean_payload(data: dict) -> dict:
    """
    Keep only key-value pairs where both key and value are present (non-empty).
    """
    FIELD_KEYS = {
    "Name": ["Name", "name", "Full Name", "full_name"],
    "DOB": ["DOB", "dob", "Date of Birth", "date_of_birth"],
    "Gender": ["Gender", "gender"],
    "Aadhaar Number": ["Aadhaar Number", "aadhaar_no", "aadhaar"],
    "Address": ["Address", "address"],
    "Father/Husband Name": ["Father/Husband Name", "Father Name", "father_name", "fathers_name", "Husband Name"],
    "PAN Number": ["PAN Number", "pan_no", "pan"],
    "Passport Number": ["Passport Number", "passport_no", "passport"],
    "Expiry Date": ["Expiry Date", "expiry_date", "expiry"],
    "Nationality": ["Nationality", "nationality"]
}
    
    
    db_col_name = {
        "Name": "full_name",
        "DOB": "dob",
        "Gender": "gender",
        "Aadhaar Number": "aadhaar_number",
        "PAN Number": "pan_number",
        "Passport Number": "passport_number",
        "Father/Husband Name": "father_husband_name",
        "Address": "address",
        "Expiry Date": "expiry_date",
        "Nationality": "nationality"   
    }
    clean_dict = {k: v for k, v in data.items() if k and v}
    return {db_col_name[k]: v for k, v in clean_dict.items() if k in db_col_name}

if st.button("💾 Save into Database", type="primary"):
    # Clean the data before sending
    payload = clean_payload(final_data)
    print("\npayload: ", payload)

    try:
        # Call FastAPI endpoint
        response = requests.post(API_SAVE_URL, json={"data": payload})

        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Data Saved Successfully! Assigned Employee ID: {result['employee_id']}")
            st.json(payload)  # show the cleaned payload
        else:
            error_msg = response.json().get("detail", "Unknown error occurred")
            st.error(f"❌ Failed to save data: {error_msg}")
    
    except Exception as e:
        st.error(f"🚨 Request failed: {str(e)}")


# Option to reset for next employee
if st.button("➕ Upload New Employee Data", width='content', type="secondary"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]  # clear all session state
    st.switch_page("form_ui.py")  # redirect to root page