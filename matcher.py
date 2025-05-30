import os
import json
import re

from crewai import Agent
from groq_llm import GroqLLM
from utils import extract_text

from dotenv import load_dotenv
load_dotenv()

class ResumeMatcherCore:

    def __init__(self):
        self.llm = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))

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

    def try_fix_json(self, raw_str):
        cleaned = re.sub(r"```json|```", "", raw_str, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        cleaned = re.sub(r'("[-\w]+":\s*)(-?\d+(\.\d+)?|null|true|false)"', r'\1\2', cleaned)
        cleaned = cleaned.replace('\n', ' ').replace('\t', ' ')
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing failed after cleanup: {e}")
            print(f"Cleaned JSON string:\n{cleaned}")
            return None

    def run(self, jd_file, resume_folder):
        job_text = extract_text(jd_file)
        output = []

        for file in os.listdir(resume_folder):
            if not file.lower().endswith(('.pdf', '.docx', '.txt')):
                continue

            path = os.path.join(resume_folder, file)
            resume_text = extract_text(path)

            prompt = (
                "SYSTEM PROMPT: Use the system prompt embedded in GroqLLM.\n\n"
                f"Job Description:\n{job_text}\n\n"
                f"Candidate Resume:\n{resume_text}\n\n"
                "Output only a clean and valid JSON object. "
                "Do not include markdown formatting (like ```json). "
                "Do not include explanations or extra text before or after the JSON. "
                "Use JSON format. Ensure that all brackets, quotes, and commas are properly placed. Do not place objects inside arrays unless they are properly nested."
                "Make sure the 'name' field contains the candidate's full name. "
                "Return the name of the university also along with the degree of the candidate. "
                "Avoid duplicate keys. Ensure each section (e.g., soft_skills, certifications, analysis) appears only once and is correctly structured. "
                "Return only the JSON object."
                "Please analyze and score this candidate as per the criteria in the system prompt. "
                "Return a detailed JSON with score components, red flags, bonus points, and analysis."
            )

            try:
                llm_response = self.llm._call(prompt)
            except Exception as e:
                error_data = {
                    "filename": file,
                    "score_data": {
                        "error": f"[ERROR] LLM call failed: {e}"
                    }
                }
                output.append(error_data)
                continue

            score_data = self.try_fix_json(llm_response)

            if score_data is None:
                error_data = {
                    "filename": file,
                    "score_data": {
                        "error": f"[ERROR] Failed to parse JSON.",
                        "raw_response": llm_response
                    }
                }
                output.append(error_data)
                continue

            output.append({
                "filename": file,
                "score_data": score_data
            })

        return output
