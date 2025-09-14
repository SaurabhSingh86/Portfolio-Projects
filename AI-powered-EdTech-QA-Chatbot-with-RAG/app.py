import streamlit as st
from utils.pdf_parser import extract_text_from_pdf
from utils.text_splitter import chunk_text
from utils.embeddings import build_vector_store
from utils.llm_groq import build_qa_chain, get_answer
import os
import roman
from utils.utility import parse_student_answers, parse_quiz, clean_quiz_text
from backend.quiz_generator import generate_quiz
from utils.export_utils import export_quiz_docx, export_quiz_pdf_bytes
from PyPDF2 import PdfReader
os.environ["STREAMLIT_WATCHER_TYPE"] = "poll"
from dotenv import load_dotenv
load_dotenv()

# Load Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # keep in .env or export manually

# Page config
st.set_page_config(page_title="EdTech Q&A + Quiz Bot", layout="wide")

# Title
# st.title("📚 EdTech Q&A + Quiz Generator")
# Title
st.markdown(
    "<h1 style='text-align: center; color: #2C3E50;'>📚 EdTech Q&A + Quiz Generator</h1>",
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Upload Document", "Ask Questions", "Generate Quiz"])

# Upload PDF
if menu == "Upload Document":
    st.header("📤 Upload Course Material (PDF)")
    uploaded_file = st.file_uploader("Upload your course PDF", type=["pdf"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        
        with st.spinner("Extracting text..."):
            text = extract_text_from_pdf(uploaded_file)
        
        if "⚠️" in text:
            st.error(text)
        else:
            st.subheader("📖 Extracted Text Preview:")
            st.text_area("Text", text[:1000], height=300)  # preview
            st.session_state["course_text"] = text
            
        if st.button("Split into Chunks"):
            chunks = chunk_text(text)
            st.session_state["chunks"] = chunks
            st.write(f"✅ Total Chunks Created: {len(chunks)}")
            st.write(chunks[:3])  # preview first 3 chunks

        if "chunks" in st.session_state:
            if st.button("Build Vector Store"):
                vector_store = build_vector_store(st.session_state["chunks"])
                st.session_state["vector_store"] = vector_store
                st.success("✅ Vector store created successfully!")

        if "vector_store" in st.session_state:
            query = st.text_input("Ask something from the document:")
            if query:
                docs = st.session_state["vector_store"].similarity_search(query, k=3)
                st.write("🔍 Top relevant chunks:")
                for i, doc in enumerate(docs, 1):
                    st.write(f"**Chunk {i}:** {doc.page_content[:500]}...")


# Ask Questions
elif menu == "Ask Questions":
    st.header("💬 Ask Questions")

    # Ensure vector store exists
    if "vector_store" not in st.session_state:
        st.warning("⚠️ Please upload and process a PDF first!")
    else:
        query = st.text_input("Enter your question")
        
        if st.button("Get Answer"):
            if not GROQ_API_KEY:
                st.error("❌ GROQ_API_KEY not found. Please set it in your environment.")
            else:
                # build QA chain
                qa_chain = build_qa_chain(st.session_state["vector_store"], GROQ_API_KEY)

                with st.spinner("Thinking... 🤔"):
                    answer, sources = get_answer(qa_chain, query)

                # Show results
                st.subheader("🤖 Answer")
                st.write(answer)

                st.subheader("📚 Sources")
                for i, src in enumerate(sources, 1):
                    st.write(f"**Source {i}:** {src}...")
                    

# Generate Quiz Section
elif menu == "Generate Quiz":
    st.header("📝 Generate Quiz from Course Material")

    if "course_text" not in st.session_state:
        st.warning("⚠️ Please upload a PDF first.")
    else:
        num_qs = st.slider("How many questions?", 3, 10, 5)

        # Generate Quiz
        if st.button("Generate Quiz"):
            import os
            with st.spinner("Generating quiz..."):
                raw_quiz = generate_quiz(st.session_state["course_text"], GROQ_API_KEY, num_qs)
                cleaned_quiz = clean_quiz_text(raw_quiz)
                st.session_state["quiz"] = parse_quiz(cleaned_quiz)
            st.success("✅ Quiz generated successfully!")

        # Display Quiz
        if "quiz" in st.session_state:
            st.subheader("📚 Take the Quiz")
            quiz_data = st.session_state["quiz"]

            # Dictionary to store user answers
            user_answers = {}

            for idx, q in enumerate(quiz_data, 1):
                roman_num = roman.toRoman(idx)
                # Show question with less spacing
                # st.write(f"**{roman_num}. {q['question']}**")
                st.markdown(f"**{roman_num}. {q['question']}**")

                # Show options directly (no placeholder)
                options_list = [f"{num}) {text}" for num, text in q["options"].items()]

                user_ans = st.radio(
                    # f"Q{idx}",  # hidden label for accessibility
                    label="[1 Mark]",
                    options=options_list,
                    key=f"q_{idx}",
                    index=None
                )

                # Save numeric answer ("1", "2", etc.)
                if user_ans:
                    user_answers[idx] = user_ans.split(")")[0]

            # Final Submit button
            if st.button("Submit", disabled=len(user_answers) < len(quiz_data), width="stretch"):
                score = 0
                st.subheader("📊 Results")

                for idx, q in enumerate(quiz_data, 1):
                    user_ans = user_answers.get(idx, None)
                    correct_ans = q["answer"]

                    st.markdown(f"**{roman.toRoman(idx)}. {q['question']}**")

                    if user_ans == correct_ans:
                        st.success(f"✅ Correct! ({correct_ans}) {q['options'][correct_ans]}")
                        st.info(f"Explanation: {q['explanation']}")
                        score += 1
                    else:
                        if not user_ans:
                            st.warning("⚠️ Not answered")
                        else:
                            st.error(
                                f"❌ Wrong. Your answer: ({user_ans}) {q['options'].get(user_ans, 'N/A')}"
                            )
                        st.info(f"Correct Answer: ({correct_ans}) {q['options'][correct_ans]}")
                        st.info(f"Explanation: {q['explanation']}")

                st.success(f"🏆 Final Score: {score}/{len(quiz_data)}")

            st.subheader("📥 Download Quiz")
            # Download buttons
            col1, col2 = st.columns(2)

            with col1:
                pdf_buf_no_ans = export_quiz_pdf_bytes(quiz_data, with_answers=False)
                if st.download_button(
                    "⬇️ Download Quiz (PDF - Without Answers)",
                    data=pdf_buf_no_ans.getvalue(),
                    # export_quiz_pdf(quiz_data, with_answers=False),
                    file_name="Quiz_Without_Answers.pdf",
                    mime="application/pdf"
                ):
                    st.success("PDF without answers downloaded!")

                if st.download_button(
                    "⬇️ Download Quiz (DOCX - Without Answers)",
                    export_quiz_docx(quiz_data, with_answers=False),
                    file_name="Quiz_Without_Answers.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ):
                    st.success("DOCX without answers downloaded!")

            with col2:
                pdf_buf = export_quiz_pdf_bytes(quiz_data, with_answers=True)
                if st.download_button(
                    "⬇️ Download Quiz (PDF - With Answers)",
                    data=pdf_buf.getvalue(),
                    # export_quiz_pdf(quiz_data, with_answers=True),
                    file_name="Quiz_With_Answers.pdf",
                    mime="application/pdf"
                ):
                    st.success("PDF with answers downloaded!")

                if st.download_button(
                    "⬇️ Download Quiz (DOCX - With Answers)",
                    export_quiz_docx(quiz_data, with_answers=True),
                    file_name="Quiz_With_Answers.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ):
                    
                    st.success("DOCX with answers downloaded!")

# # Upload Solved Quiz --------------------
# elif menu == "Upload Solved Quiz":
#     st.header("📤 Upload Solved Quiz for Evaluation")

#     if "quiz" not in st.session_state:
#         st.warning("⚠️ Please generate a quiz first.")
#     else:
#         uploaded_solved = st.file_uploader("Upload your solved quiz (PDF or TXT)", type=["pdf", "txt"])

#         if uploaded_solved:
#             # Extract text from PDF or TXT
#             if uploaded_solved.type == "application/pdf":
#                 pdf_reader = PdfReader(uploaded_solved)
#                 solved_text = ""
#                 for page in pdf_reader.pages:
#                     solved_text += page.extract_text() + "\n"
#             else:
#                 solved_text = uploaded_solved.read().decode("utf-8")

#             student_answers = parse_student_answers(solved_text)
#             quiz_data = st.session_state["quiz"]

#             # Auto-grade
#             score = 0
#             results = []

#             for idx, q in enumerate(quiz_data, 1):
#                 correct_ans = q["answer"]
#                 student_ans = student_answers.get(idx, "Not Answered")

#                 if student_ans == correct_ans:
#                     score += 1
#                     results.append(f"Q{idx}: ✅ Correct ({student_ans})")
#                 else:
#                     results.append(f"Q{idx}: ❌ Wrong (Your: {student_ans}, Correct: {correct_ans})")

#             st.subheader("📊 Evaluation Result")
#             st.write("\n".join(results))
#             st.success(f"🏆 Final Score: {score}/{len(quiz_data)}")