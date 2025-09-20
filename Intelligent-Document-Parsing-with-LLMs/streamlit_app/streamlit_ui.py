# streamlit_ui.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8003/doc-ai/upload/"

st.title("📑 Document Intelligence & GenAI")

# Allow multiple file uploads
uploaded_files = st.file_uploader(
    "Upload Documents (Aadhaar, PAN, Passport)", 
    type=["jpg", "png", "pdf"], 
    accept_multiple_files=True
)

# Select document type for each uploaded file
doc_types = []
if uploaded_files:
    st.subheader("Assign Document Type for Each File")
    for uploaded_file in uploaded_files:
        doc_type = st.selectbox(
            f"Select type for {uploaded_file.name}", 
            ["Aadhaar", "PAN", "Passport"], 
            key=uploaded_file.name
        )
        doc_types.append(doc_type)

# Submit button
if uploaded_files and st.button("Process Documents"):
    if len(uploaded_files) != len(doc_types):
        st.error("Please select a document type for each file")
    else:
        # Prepare files and form data
        files_payload = [
            ("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files
        ]
        data_payload = [
            ("doc_types", dt) for dt in doc_types
        ]

        with st.spinner("Processing documents..."):
            response = requests.post(API_URL, files=files_payload, data=data_payload)

        if response.status_code == 200:
            st.success("Documents processed successfully!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.status_code}")
            st.text(response.text)
