import re

ROMAN_NUMS = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]

# -------------------- Clean LLM Output --------------------
def clean_quiz_text(text: str):
    """
    Clean LLM-generated quiz text:
    - Fix missing letters in "Answer" or "Explanation"
    - Replace fancy quotes
    - Remove extra newlines
    """
    text = text.replace("nswer:", "Answer:").replace("xplanation:", "Explanation:")
    text = text.replace("\u201c", '"').replace("\u201d", '"')  # fancy quotes
    text = re.sub(r'\n{2,}', '\n\n', text)  # normalize multiple newlines
    return text.strip()


# -------------------- Parse LLM Quiz --------------------
import re

def parse_quiz(quiz_text: str):
    """
    Parse quiz text in strict format:
    
    I. Question text
        1) Option 1
        2) Option 2
        3) Option 3
        4) Option 4
    Answer: <1/2/3/4>
    Explanation: <why correct>
    
    Returns: list of dicts with question, options, answer, explanation
    """
    quiz_data = []

    # Split on Roman numeral pattern (I. II. III. etc.)
    questions = re.split(r"\n(?=[IVXLCDM]+\.)", quiz_text.strip())
    
    for q in questions:
        q = q.strip()
        if not q:
            continue

        # Extract question text
        q_match = re.match(r"^[IVXLCDM]+\.\s*(.+)", q)
        if not q_match:
            continue
        question = q_match.group(1).strip()

        # Extract options (1–4)
        options = {}
        opt_matches = re.findall(r"(\d\))\s*(.+)", q)
        for opt in opt_matches:
            num = opt[0].replace(")", "").strip()  # "1)", "2)" → "1"
            options[num] = opt[1].strip()

        # Extract answer
        ans_match = re.search(r"Answer:\s*([1-4])", q)
        answer = ans_match.group(1) if ans_match else ""

        # Extract explanation
        exp_match = re.search(r"Explanation:\s*(.+)", q, re.DOTALL)
        explanation = exp_match.group(1).strip() if exp_match else ""

        # Skip malformed questions
        if not (question and len(options) == 4 and answer):
            continue

        quiz_data.append({
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation
        })

    return quiz_data


# -------------------- Parse Student Answers --------------------
def parse_student_answers(text: str):
    """
    Extract student answers from uploaded text (PDF/TXT).
    Matches numeric options (1-4).
    Returns: dict {question_number: answer_number}
    """
    answers = {}
    matches = re.findall(r'(?:Q?(\d+))\s*[\)\.:]?\s*([1-4])', text)

    for q_num, ans in matches:
        answers[int(q_num)] = ans

    return answers
