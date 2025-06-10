import os
import json
import re
import time
import threading
import psycopg2
from crewai import Agent
from groq_llm import GroqLLM
from utils import extract_text
from dotenv import load_dotenv
import uuid
load_dotenv()

class ResumeMatcherCore:
    def __init__(self):
        self.llm = GroqLLM(api_key=os.getenv("GEMINI_API_KEY"))
        self.db_config = {
            "dbname": "Resume_JD",
            "user": "postgres",
            "password": "admin",
            "host": "localhost",
            "port": 5433
        }

        self.job_parser_agent = Agent(
            role="JobParser",
            goal="Extract key requirements and structured info from the job description.",
            backstory="Expert in job analysis and recruitment strategy.",
            llm=self.llm
        )

        self.resume_analyzer_agent = Agent(
            role="ResumeAnalyzer",
            goal="Evaluate resumes against job description using transparent scoring per system prompt.",
            backstory="Expert in resume parsing and hiring best practices.",
            llm=self.llm
        )

        self.init_db()

    def init_db(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_analysis (
                    id uuid unique,
                    name TEXT,
                    email TEXT,
                    contact_no TEXT,
                    final_score FLOAT,
                    technical_skills_score FLOAT,
                    technical_skills TEXT,
                    experience_score FLOAT,
                    experience TEXT,
                    education_score FLOAT,
                    education TEXT,
                    soft_skills_score FLOAT,
                    soft_skills TEXT,
                    certifications_score FLOAT,
                    certifications TEXT,
                    strengths TEXT,
                    weaknesses TEXT,
                    suggestions TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_parse_errors (
                    filename TEXT PRIMARY KEY,
                    raw_error TEXT,
                    retry_count INT DEFAULT 0
                );
            """)

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print("DB Init Error:", e)

    def fix_json_issues(self, raw_str: str) -> str:
        raw_str = raw_str.strip()

        # Remove markdown code block if present
        raw_str = re.sub(r"^```json\s*", "", raw_str)
        raw_str = re.sub(r"\s*```$", "", raw_str)

        # Fix "matched": [... "missing": []] → separate matched and missing keys
        raw_str = re.sub(
            r'"matched": \[(.*?)\](\s*),\s*"missing": \[\]',
            r'"matched": [\1], "missing": []',
            raw_str,
            flags=re.DOTALL
        )

        # Fix "score": 43" → remove erroneous quote
        raw_str = re.sub(r'("score"\s*:\s*\d+)"', r'\1', raw_str)

        # Remove any trailing commas before closing brackets
        raw_str = re.sub(r',\s*([\]}])', r'\1', raw_str)

        return raw_str

    def insert_into_db(self, result):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            data = result.get("score_data", {})
            name = data.get("name", "")
            email = data.get("email", "")
            contact_no = data.get("contact no", "")  # Note the space in the key
            record_id = result.get("uuid","")
            score = data.get("score", {})
            components = score.get("components", {})
            row = (
                record_id,
                name,
                email,
                contact_no,
                score.get("value", 0.0),
                components.get("technical_skills", {}).get("score", 0.0),
                ", ".join(skill.get("skill", "") if isinstance(skill, dict) else str(skill)
                        for skill in components.get("technical_skills", {}).get("matched", [])),
                components.get("experience", {}).get("score", 0.0),
                components.get("experience", {}).get("field", ""),
                components.get("education", {}).get("score", 0.0),
                components.get("education", {}).get("degree", ""),
                components.get("soft_skills", {}).get("score", 0.0),
                ", ".join(skill.get("skill", "") if isinstance(skill, dict) else str(skill)
                        for skill in components.get("soft_skills", {}).get("matched", [])),
                components.get("certifications", {}).get("score", 0.0),
                ", ".join(cert.get("name", "") if isinstance(cert, dict) else str(cert)
                        for cert in components.get("certifications", {}).get("items", [])),
                ", ".join(data.get("analysis", {}).get("strengths", [])),
                ", ".join(data.get("analysis", {}).get("weaknesses", [])),
                ", ".join(data.get("analysis", {}).get("suggestions", [])),
            )

            cursor.execute("""
                INSERT INTO resume_analysis (
                    id, name, email, contact_no, final_score, 
                    technical_skills_score, technical_skills,
                    experience_score, experience, education_score, education,
                    soft_skills_score, soft_skills, certifications_score, certifications,
                    strengths, weaknesses, suggestions
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, row)

            cursor.execute("DELETE FROM resume_parse_errors WHERE filename = %s;", (result["filename"],))

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print("DB Insert Error:", e)

    def log_parse_error(self, filename, raw):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO resume_parse_errors (filename, raw_error, retry_count)
                VALUES (%s, %s, 1)
                ON CONFLICT (filename) DO UPDATE SET
                    raw_error = EXCLUDED.raw_error,
                    retry_count = resume_parse_errors.retry_count + 1;
            """, (filename, raw[:2000]))

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print("Error Logging Failed:", e)

    def run_single(self, jd_file, resume_file,uuid):
        job_text = extract_text(jd_file)
        resume_text = extract_text(resume_file)

        prompt = (
           "SYSTEM PROMPT: Use the system prompt embedded in GroqLLM. "
            f"Job Description: {job_text} "
            f"Candidate Resume: {resume_text} "
            "Ensure the JSON output does not contain escaped characters like \\n, \\\\, or \\/. "
            "The response must be plain, readable JSON with standard characters only. "
            "Output only a clean and valid JSON object. "
            "Do not include markdown formatting (like json). "
            "Do not include explanations or extra text before or after the JSON. "
            "Ensure all brackets, quotes, and commas are properly placed. "
            "Make sure the 'name' field contains the candidate's full name. "
            "Return the name of the university along with the degree of the candidate. "
            "Avoid duplicate keys. Ensure each section (e.g., soft_skills, certifications, analysis) "
            "appears only once and is correctly structured. "
            "Return only the JSON object. "
            "Please analyze and score this candidate as per the criteria in the system prompt. "
            "Return a detailed JSON with score components, red flags, bonus points, and analysis."
        
        )

        try:
            llm_response = self.llm._call(prompt)
        except Exception as e:
            return {
                "filename": os.path.basename(resume_file),
                "score_data": {
                    "error": f"[ERROR] LLM call failed: {e}"
                }
            }

        fixed_raw = self.fix_json_issues(llm_response)

        try:
            parsed = json.loads(fixed_raw)
            result = {
                "filename": os.path.basename(resume_file),
                "uuid":uuid,
                "score_data": parsed
            }
            self.insert_into_db(result)
            return result
        except Exception as e:
            raw_name = os.path.basename(resume_file)
            self.log_parse_error(raw_name, fixed_raw)
            return {
                "filename": raw_name,
                "score_data": {
                    "error": "[ERROR] Could not parse JSON",
                    "raw": fixed_raw
                }
            }

    def run_background_retry(self, jd_path, folder="uploads"):
        def retry_loop():
            print("Background retry thread started...")
            while True:
                try:
                    conn = psycopg2.connect(**self.db_config)
                    cursor = conn.cursor()
                    cursor.execute("SELECT filename FROM resume_parse_errors;")
                    rows = cursor.fetchall()
                    for (filename,) in rows:
                        resume_path = os.path.join(folder, filename)
                        if os.path.exists(resume_path):
                            self.run_single(jd_path, resume_path)
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Retry loop error: {e}")
                time.sleep(60)  # Retry every 60 seconds

        thread = threading.Thread(target=retry_loop, daemon=True)
        thread.start()