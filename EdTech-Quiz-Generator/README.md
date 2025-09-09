# 📚 EdTech Q&A + Quiz Generator

## 📝 Problem Statement

Education platforms need a way to automatically generate quizzes from course material. This project builds a Streamlit app that generates MCQ quizzes using LLMs, evaluates answers, and exports quizzes in PDF/DOCX formats.

---

## 🚀 Features

- Upload course text → auto-generate quiz questions
- Multiple-choice questions with explanations
- Interactive Streamlit interface
- Score evaluation in real-time
- Export quiz (with or without answers) → PDF / DOCX
- Clean UI for easy use

---

## 🛠️ Tech Stack

- Python 3.10+
- Streamlit (UI)
- LangChain / LLM API (Quiz generation)
- python-docx (DOCX export)
- reportlab (PDF export)

---

## 📂 Project Structure

```
EdTech-Quiz-Generator/
│── app.py                      # Main Streamlit app
│── backend/                    # LLM & quiz generation logic
│    ├── quiz_generator.py
│── utils/                      # Helper & utility modules
│    ├── embeddings.py
│    ├── export_utils.py
│    ├── pdf_parser.py
│    ├── llm_groq.py
│    ├── text_splitter.py
│    ├── utility.py
│── sample_files/               # Sample PDFs or course materials
│    ├── sql questions.pdf
│── requirements.txt            # Dependencies
│── README.md                   # Project documentation
│── architecture.png            # Architecture diagram
│── ed_env/                     # Virtual environment
│── .env                        # API keys
│── .gitignore

```

---

## ⚙️ Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/SaurabhSingh86/Portfolio-Projects.git
cd Portfolio-Projects/EdTech-Quiz-Generator
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
streamlit run app.py
```

---

## 🎯 Example Usage

- Upload your course material (.txt or .pdf file).
- Click Generate Quiz → Questions & options will appear.
- Select answers and click Submit → Get your score.
- Download quiz as PDF/DOCX (with or without answers).

---

## 📸 Screenshots / Demo

---

## 📊 Future Enhancements

- Add support for multiple subjects at once
- Allow image-based question generation
- Track user performance across quizzes
- Export to Excel

---

## 👨‍💻 Author

**Saurabh Singh**
🔗 [LinkedIn](https://www.linkedin.com/in/saurabh-singh-621388182/) |
[Project Link](https://github.com/SaurabhSingh86) |
YouTube
