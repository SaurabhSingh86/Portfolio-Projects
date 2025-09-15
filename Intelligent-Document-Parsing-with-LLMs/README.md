# 📄✨ Intelligent Document Parsing with LLMs

## 📝 Problem Statement

An AI-powered system that uses **Google Gemini LLM** to intelligently parse and extract structured data from common identification documents like **Aadhaar, PAN Card, and Passport**.  
This project enables **automated, accurate, and scalable document data extraction** for real-world applications.

---

## 🚀 Features

- Supports **Aadhaar, PAN Card, and Passport**
- Uses **LLM (Gemini API)** for intelligent parsing
- Faster and more accurate than manual OCR-based approaches
- Modular design for easy extension to new document types
- Outputs **clean JSON** for integration with downstream systems

---

## 🛠️ Tech Stack

- Python 3.10+
- Streamlit (UI)
- Fast API
- OCR (Tesseract, Pyzbar, OpenCV)
- Google Gemini LLM API

---

## 📂 Project Structure

```
AI-Employee-Doc-Parser/
│── part1_employee_info/        # MCP server for employee info (future part)
│── part2_leave_mgmt/           # MCP server for leave management (future part)
│── part3_doc_ai/               # Document Intelligence + GenAI
│   │── main.py                  # FastAPI backend
│   │── routes/
│   │   └── upload.py            # API endpoints
│   │── services/
│   │   ├── extractor.py         # OCR + parsing logic
│   │   ├── llm_parser.py        # Gemini LLM parsing
│   │   ├── pancard.py           # PAN parsing logic
│   │   ├── passport.py          # Passport parsing logic
│   │── streamlit_app/
│   │   └── form_ui.py           # Streamlit UI
│   │── .env                     # API keys & DB credentials
│── requirements.txt             # Dependencies
│── README.md                    # Documentation
│── .gitignore                   # Ignore env & temp files


```

---

## ⚙️ Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/SaurabhSingh86/Portfolio-Projects.git
cd Portfolio-Projects/Intelligent-Document-Parsing-with-LLMs
```

2. **Create a virtual environment & activate it:**

```bash
python -m venv ed_env

# Linux / Mac
source ed_env/bin/activate

# Windows
ed_env\Scripts\activate

```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the app:**

```bash
streamlit run form_ui.py
uvicorn fast_api:app --port 8003
```

---

## 📸 Screenshots / Demo

**Version 1**

_Step 1_
![alt text](<UI-Images/UI Home.png>)

_Step 2_
![alt text](<UI-Images\Upload Aadhar.png>)

_Step 3_ (Optional PAN or Passport)
![alt text](<UI-Images/Upload Passport.png>)

_Step 4_
![alt text](<UI-Images/Save Into Database.png>)

_Step 5_
![alt text](<UI-Images/Confirm Save Into Database.png>)

---

## ⚙️ How It Works

1. Upload document text (Aadhaar, PAN, Passport).
2. Send to LLM parser (`llm_parser.py`).
3. LLM extracts **key fields** (Name, DOB, ID Number, etc.).
4. Returns **structured JSON** for storage or validation.

---

## 📊 Example Output

```json
{
  "document_type": "PAN",
  "name": "Saurabh Singh",
  "dob": "1995-08-20",
  "pan_number": "ABCDE1234F"
}
```

---

## 📊 Future Enhancements

- Add support for additional IDs (e.g., Driving License, Voter ID)
- Improve error handling & fallback logic
- Deploy as a web-based or mobile-ready API service

---

## 👨‍💻 Author

**Saurabh Singh**
🔗 [LinkedIn](https://www.linkedin.com/in/saurabh-singh-621388182/) |
[Project Link](https://github.com/SaurabhSingh86) |
YouTube

```

```
