import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from urllib.parse import quote_plus
from langchain_community.utilities import SQLDatabase
from fastapi import FastAPI, HTTPException
import os
import json

load_dotenv()

# def db_connection():
#     db_user = "root"
#     db_password = "123456"
#     db_host = "127.0.0.1"
#     db_port = 3306
#     db_name = "atliq_tshirts"

#     # Encode password safely
#     encoded_password = quote_plus(db_password)

#     # Build connection string
#     uri = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

#     # Connect to DB
#     db = SQLDatabase.from_uri(uri, sample_rows_in_table_info=3)
#     print("📊 Tables Info:\n", db.get_table_info())
#     return db

# DB connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=os.getenv("DB_PORT", 3306),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "employee_mgmt")
        )
        return connection
        
    except mysql.connector.Error as e:
        print(f"❌ Database connection error: {e}")
        return None

def get_employees():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee_basic_info")
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return result

def save_emp_info(cleaned_data):
    con = get_db_connection()
    cur = con.cursor()
    
    # Extract keys and values from payload
    columns = ", ".join(cleaned_data.keys())
    placeholders = ", ".join(["%s"] * len(cleaned_data))
    values = list(cleaned_data.values())
    
    # Check Aadhaar, PAN, Passport
    for field in ["aadhaar_number", "pan_number", "passport_number"]:
        if field in cleaned_data:
            cur.execute(f"SELECT employee_id FROM employee_basic_info WHERE {field}=%s", (cleaned_data[field],))
            if cur.fetchone():
                raise ValueError(f"Duplicate {field.replace('_',' ').title()} found!")
    
    sql = f"""Insert into employee_basic_info ({columns}) VALUES ({placeholders})"""
    print(sql, values)
    cur.execute(sql, values)
    con.commit()
    
    employee_id  = cur.lastrowid
    cur.close()
    con.close()
    return employee_id


if __name__ == "__main__":
    # print(db_connection())
    # print()
    print(get_db_connection())
    print(get_employees())

# # Generic function to insert into a given table
# def insert_employee(employee_data):
#     """
#     Inserts data into employee table.
#     Returns employee_id
#     """
#     conn = get_db_connection()
#     if not conn:
#         return None

#     try:
#         cursor = conn.cursor()

#         query = """
#         INSERT INTO employees (full_name, dob, gender, father_name, address)
#         VALUES (%s, %s, %s, %s, %s)
#         """
#         values = (
#             employee_data.get("Name") or None,
#             employee_data.get("DOB") or None,
#             employee_data.get("Gender") or None,
#             employee_data.get("Father / Husband Name") or None,
#             employee_data.get("Address") or None,
#         )

#         cursor.execute(query, values)
#         conn.commit()
#         emp_id = cursor.lastrowid

#         cursor.close()
#         conn.close()
#         return emp_id

#     except Error as e:
#         print(f"Insert Employee Error: {e}")
#         return None


# def insert_aadhaar(emp_id, aadhaar_no):
#     """
#     Inserts Aadhaar details linked with employee_id
#     """
#     if not aadhaar_no:
#         return None  # skip empty values

#     conn = get_db_connection()
#     if not conn:
#         return None

#     try:
#         cursor = conn.cursor()
#         query = """
#         INSERT INTO aadhaar (employee_id, aadhaar_no)
#         VALUES (%s, %s)
#         """
#         cursor.execute(query, (emp_id, aadhaar_no))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return cursor.lastrowid
#     except Error as e:
#         print(f"Insert Aadhaar Error: {e}")
#         return None


# def insert_pan(emp_id, pan_no):
#     """
#     Inserts PAN details linked with employee_id
#     """
#     if not pan_no:
#         return None

#     conn = get_db_connection()
#     if not conn:
#         return None

#     try:
#         cursor = conn.cursor()
#         query = """
#         INSERT INTO pan (employee_id, pan_no)
#         VALUES (%s, %s)
#         """
#         cursor.execute(query, (emp_id, pan_no))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return cursor.lastrowid
#     except Error as e:
#         print(f"Insert PAN Error: {e}")
#         return None


# def insert_passport(emp_id, passport_no, expiry_date=None, nationality=None):
#     """
#     Inserts Passport details linked with employee_id
#     """
#     if not passport_no:
#         return None

#     conn = get_db_connection()
#     if not conn:
#         return None

#     try:
#         cursor = conn.cursor()
#         query = """
#         INSERT INTO passport (employee_id, passport_no, expiry_date, nationality)
#         VALUES (%s, %s, %s, %s)
#         """
#         cursor.execute(query, (emp_id, passport_no, expiry_date, nationality))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return cursor.lastrowid
#     except Error as e:
#         print(f"Insert Passport Error: {e}")
#         return None
