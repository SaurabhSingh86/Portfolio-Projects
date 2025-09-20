import streamlit as st
import requests
import pandas as pd
import json
from io import BytesIO
from datetime import datetime

API_Upload_URL = "http://127.0.0.1:8003/doc-ai/upload/"

st.set_page_config(page_title="Document Upload & Parsing", layout="wide")
# st.title("📄🤖 Intelligent Document Parsing with LLMs")

st.markdown(
    "<h1 style='text-align: center; color: #2C3E50;'>📄✨ Intelligent Document Parsing with LLMs</h1>",
    unsafe_allow_html=True
)

# ---------------- session state init ----------------
if "results" not in st.session_state:
    st.session_state.results = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ---------------- helpers ----------------
FIELDS = [
    "Name",
    "Father/Husband Name",
    "DOB",
    "Gender",
    "Address",
    "Aadhaar Number",
    "PAN Number",
    "Passport Number",
    "Expiry Date",
    "Nationality",
]

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

DOC_PRIORITY = ["Aadhaar", "PAN", "Passport"]


def safe_get(result: dict, key: str):
    """Try to get a value from result in common placements."""
    if key in result and result[key] not in (None, ""):
        return result[key]
    parsed = result.get("parsed_data") if isinstance(result.get("parsed_data"), dict) else None
    if parsed and key in parsed and parsed[key] not in (None, ""):
        return parsed[key]
    low = key.lower().replace(" ", "_")
    if low in result and result[low] not in (None, ""):
        return result[low]
    if parsed and low in parsed and parsed[low] not in (None, ""):
        return parsed[low]
    return None


def build_extracted_data(results):
    """Collect field -> list of candidate values"""
    candidates = {f: [] for f in FIELDS}
    ordered = []

    for p in DOC_PRIORITY:
        for r in results:
            doc_label = r.get("doc_type") or r.get("Doc Type") or r.get("docType") or r.get("doctype")
            if doc_label and doc_label.lower() == p.lower():
                ordered.append(r)

    for r in results:
        if r not in ordered:
            ordered.append(r)

    for r in ordered:
        for field in FIELDS:
            for k in FIELD_KEYS[field]:
                val = safe_get(r, k)
                if val:
                    if isinstance(val, (int, float)):
                        val = str(val)
                    v = val.strip() if isinstance(val, str) else str(val)
                    if v and v not in candidates[field]:
                        candidates[field].append(v)
                    break
    return candidates


def get_primary_username_from_results(results):
    for r in results:
        dt = (r.get("doc_type") or r.get("Doc Type") or "").lower()
        if dt == "aadhaar":
            val = safe_get(r, "Name") or safe_get(r, "name")
            if val: return val.replace(" ", "_")
    for r in results:
        dt = (r.get("doc_type") or r.get("Doc Type") or "").lower()
        if dt == "pan":
            val = safe_get(r, "Full Name") or safe_get(r, "Name")
            if val: return val.replace(" ", "_")
    for r in results:
        dt = (r.get("doc_type") or r.get("Doc Type") or "").lower()
        if dt == "passport":
            val = safe_get(r, "Name") or safe_get(r, "Given Name") or safe_get(r, "Surname")
            if val: return val.replace(" ", "_")
    return "user_info"


# ---------------- UI: upload ----------------
# col_left, col_right = st.columns([3, 1])
col_left, col_right = st.columns(2)
with col_left:
    doc_type = st.selectbox("Select Document Type", ["Aadhaar", "PAN", "Passport"])
    
with col_right:
    uploaded_file = st.file_uploader(
        "Upload a document", type=["jpg", "jpeg", "png", "pdf"],
        key=f"uploader_{st.session_state.uploader_key}"
    )


if st.button("Upload & Process", width='stretch'):
    if not uploaded_file:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("⏳ Processing..."):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"doc_type": doc_type}
            try:
                response = requests.post(API_Upload_URL, files=files, data=data, timeout=120)
            except Exception as e:
                st.error(f"Request failed: {e}")
                response = None

            if response and response.status_code == 200:
                result = response.json()
                result["doc_type"] = doc_type
                st.session_state.results.append(result)
                st.success(f"✅ {doc_type} Processed Successfully!")
                st.session_state.uploader_key += 1
                st.rerun()
            else:
                st.error(f"❌ Error: {response.text if response else 'No response'}")

# ---------------- UI: results ----------------
if st.session_state.results:
    st.subheader("📊 Final Extracted Data")

    df = pd.DataFrame(st.session_state.results)
    edited_df = st.data_editor(df, width='stretch', num_rows="dynamic")
    st.session_state.results = edited_df.to_dict(orient="records")

    col_table, col_actions = st.columns([3, 1])
    col1, col2, col3, col4 = st.columns(4)
    
    
    with col_actions:
        primary_name = get_primary_username_from_results(st.session_state.results)
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = f"{primary_name}_{file_timestamp}"

        
        with col1:
            json_data = json.dumps(st.session_state.results, indent=4)
            st.download_button("📥 Download as JSON", json_data, f"{file_prefix}.json", mime="application/json",  width="content")

        with col2:
            buf = BytesIO()
            pd.DataFrame(st.session_state.results).to_excel(buf, index=False, engine="openpyxl")
            st.download_button("📥 Download as Excel", buf.getvalue(), f"{file_prefix}.xlsx")

        with col3:
            if st.button("♻️ Reset", type="secondary"):
                st.session_state.clear()
                st.success("Form reset successfully! Start uploading new documents.")
                st.rerun()
            
        with col4:
            if st.button("➡️ Save into Database"):
                extracted = build_extracted_data(st.session_state.results)
                st.session_state["extracted_data"] = extracted
                st.session_state["from_save"] = True
                st.switch_page("pages/confirm_page.py")