# quiz_generator.py

from langchain_groq import ChatGroq

def generate_quiz(course_text: str, api_key: str, num_questions: int = 5):
    """
    Generate a quiz from course text using Groq LLaMA model.
    """
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.5
    )
    
    prompt = f"""
            You are an educational quiz generator. 
            Based on the following course material, generate {num_questions} multiple choice questions.  

            ⚠️ Output must strictly follow this format:

            I. <Question text>
                1) <Option 1>
                2) <Option 2>
                3) <Option 3>
                4) <Option 4>
            Answer: <1/2/3/4>
            Explanation: <Why this option is correct>

            Course Material:
            {course_text}
            """

    response = llm.invoke(prompt)
    return response.content



