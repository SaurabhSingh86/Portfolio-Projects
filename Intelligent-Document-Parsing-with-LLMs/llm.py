import json
import os
from dotenv import load_dotenv
from google import genai
import json5
import re

# Load environment variables
load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("Please set the environment variable GOOGLE_API_KEY")

# Initialize Google GenAI client
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def clean_json(raw_output: str):
    # Remove markdown fences like ```json ... ```
    cleaned = re.sub(r"```(json)?", "", raw_output, flags=re.IGNORECASE).strip()
    return cleaned

def parse_with_llm(doc_type: str, raw_text: str) -> dict:
    """
    Parse document text using Gemini LLM and return structured JSON
    based on document type.
    """
    doc_type = doc_type.lower()
    print("doc_type: ", doc_type)
    print("raw_text: ", raw_text)

    # Define schemas for each document type
    schemas = {
        "aadhaar": [
            "Name", "Gender", "DOB", "Aadhaar Number", 
            "S/O (Son Of)", "Address", "Mobile Number", "Aadhaar Issue Date"
        ],
        "pan": [
            "Name", "Father Name", "DOB", "PAN Number"
        ],
        "passport": [
            "Name", "DOB", "Passport Number", "Expiry Date", "Nationality"
        ]
    }

    if doc_type not in schemas:
        return {"error": f"Unsupported doc_type: {doc_type}"}

    # Build schema JSON structure (keys with null values)
    schema_example = {field: "string or null" for field in schemas[doc_type]}

    # Prompt for Gemini
    prompt = f"""
    You are a strict JSON generator for document parsing.

    Task:
    Extract information from the provided {doc_type} text and return ONLY a valid JSON object.

    Required fields:
    {json.dumps(schema_example, indent=2)}

    Text:
    {raw_text}

    Rules:
    1. Return only valid JSON (no extra text, no markdown, no explanations).
    2. JSON must start with {{ and end with }}.
    3. If a field is missing, set its value to null.
    4. Do not include any fields outside the required list.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        print("Raw LLM Output:", text)
        
        # clean markdown fences
        cleaned_output = clean_json(text)

        # Try parsing as JSON
        parsed = json5.loads(cleaned_output)
        print("PARSED: ", parsed)
        return parsed

    except Exception as e:
        return {"error": f"Failed to parse JSON: {str(e)}", "raw_output": text if 'text' in locals() else None}


    # except json.JSONDecodeError:
    #     # Fallback: try simple extraction from Markdown-like output
    #     import re
    #     parsed = {}
    #     for field in fields:
    #         match = re.search(rf"\*\*{field}\*\*:\s*(.+)", text)
    #         parsed[field] = match.group(1).strip() if match else None


if __name__ == "__main__":
    # pass
    # print(os.getenv("GOOGLE_API_KEY"))
    
    from pyzbar.pyzbar import decode
    import cv2
      
    # ada = r"D:\LLM Projects\AI_Powered_Employee_Information_Management_System\Doc_AI_Part_3\Input1\Adhar.jpg"
    pan = r"D:\LLM Projects\AI_Powered_Employee_Information_Management_System\Doc_AI_Part_3\Input1\Pancard.jpg"
    # passp = r"D:\LLM Projects\AI_Powered_Employee_Information_Management_System\Doc_AI_Part_3\Input1\Passport.png"
    doc_type = "pan"
    
    img = cv2.imread(pan)
    print(len(decode(img)))
    raw_text = ""
    for item in decode(img):
        my_data = item.data.decode("utf-8")
        raw_text += my_data
        print("my_data: ", my_data)
    
    # doc_type = "aadhaar"
    # parsed = parse_with_llm(doc_type.lower(), raw_text)
    # print("parsed: ", parsed)
