import os
import json
import re
from crewai import Agent
from groq_llm import GroqLLM
from utils import extract_text
import demjson3     
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


    # def try_fix_json(self, raw_str):
    #     try:
    #         return json.loads(raw_str)
    #     except json.JSONDecodeError:
    #         pass

    #     # Clean up common formatting issues
    #     raw_str = re.sub(r"```(?:json)?|```", "", raw_str, flags=re.IGNORECASE).strip()
    #     raw_str = re.sub(r'("score"\s*:\s*\d+)"', r'\1', raw_str)  # Fix quote after number
    #     raw_str = re.sub(r',(\s*[}\]])', r'\1', raw_str)  # Remove trailing commas
    #     raw_str = raw_str.replace('\n', ' ').replace('\t', ' ')
    #     raw_str = re.sub(r'\s{2,}', ' ', raw_str)

    #     try:
    #         return json.loads(raw_str)
    #     except json.JSONDecodeError as e:
    #         return None

    # def try_fix_json(self, raw_str):
    #     import demjson3  # forgiving JSON parser, install with: pip install demjson3

    #     # Step 1: Try native JSON parsing first
    #     try:
    #         return json.loads(raw_str)
    #     except json.JSONDecodeError:
    #         pass

    #     # Step 2: Clean common formatting issues
    #     raw_str = raw_str.strip()

    #     # Remove markdown code block markers
    #     raw_str = re.sub(r"```(?:json)?|```", "", raw_str, flags=re.IGNORECASE).strip()

    #     # Remove trailing commas
    #     raw_str = re.sub(r",(\s*[}\]])", r"\1", raw_str)

    #     # Fix misquoted numbers like "score": 87"
    #     raw_str = re.sub(r'("score"\s*:\s*\d+)"', r"\1", raw_str)

    #     # Remove duplicate keys (crude but prevents overwriting in json.loads)
    #     raw_str = re.sub(r',\s*"(\w+)"\s*:\s*("[^"]*"|\d+)', '', raw_str)
        
    #     # Fix missing closing brackets before a key
    #     raw_str = re.sub(r'("weaknesses"\s*:\s*\[[^\]]+?)(\s*"[\w_]+?"\s*:)', r'\1], \2', raw_str)


    #     # Normalize whitespace
    #     raw_str = raw_str.replace('\n', ' ').replace('\t', ' ')
    #     raw_str = re.sub(r'\s{2,}', ' ', raw_str)

    #     # Step 3: Try demjson3 (very lenient)
    #     try:
    #         return demjson3.decode(raw_str)
    #     except Exception:
    #         pass

    #     # Step 4: Final fallback
    #     return {
    #         "error": "[ERROR] Could not parse JSON",
    #         "raw": raw_str[:3000]  # avoid logging huge texts
    #     }

    # def try_fix_json(self, raw_str):
    #     # Step 1: Try native JSON parsing
    #     try:
    #         return json.loads(raw_str)
    #     except json.JSONDecodeError:
    #         pass

    #     raw_str = raw_str.strip()

    #     # Step 2: Clean markdown or formatting issues
    #     raw_str = re.sub(r"```(?:json)?|```", "", raw_str, flags=re.IGNORECASE).strip()
    #     raw_str = re.sub(r",(\s*[}\]])", r"\1", raw_str)
    #     raw_str = re.sub(r'("score"\s*:\s*\d+)"', r"\1", raw_str)
    #     raw_str = re.sub(r'("weaknesses"\s*:\s*\[[^\]]+?)(\s*"[\w_]+?"\s*:)', r'\1], \2', raw_str)
    #     raw_str = raw_str.replace('\n', ' ').replace('\t', ' ')
    #     raw_str = re.sub(r'\s{2,}', ' ', raw_str)

    #     # Step 3: Try decoding escaped JSON
    #     try:
    #         unescaped = bytes(raw_str, "utf-8").decode("unicode_escape")
    #         return json.loads(unescaped)
    #     except Exception:
    #         pass

    #     # Step 4: Try demjson3 as fallback
    #     try:
    #         return demjson3.decode(raw_str)
    #     except Exception:
    #         pass

    #     # Step 5: Final fallback
    #     return {
    #         "error": "[ERROR] Could not parse JSON",
    #         "raw": raw_str[:3000]
    #     }

    # def try_fix_json(self,raw_str):
    #     """
    #     Attempt to clean and parse a broken JSON string.
    #     Returns a dictionary if successful, or a dict with an error and the raw string if not.
    #     """

    #     # Step 1: Try standard JSON parse first
    #     try:
    #         return json.loads(raw_str)
    #     except json.JSONDecodeError:
    #         pass

    #     # Step 2: Clean up common formatting issues
    #     raw_str = raw_str.strip()

    #     # Remove Markdown code block markers (```json or ```)
    #     raw_str = re.sub(r"```(?:json)?|```", "", raw_str, flags=re.IGNORECASE).strip()

    #     # Remove trailing commas before closing brackets/braces
    #     raw_str = re.sub(r",(\s*[}\]])", r"\1", raw_str)

    #     # Fix misquoted numeric values like: "score": 92"
    #     raw_str = re.sub(r'("score"\s*:\s*\d+(\.\d+)?)"', r"\1", raw_str)

    #     # Fix missing closing brackets before next key (common in arrays)
    #     raw_str = re.sub(r'("weaknesses"\s*:\s*\[[^\]]+?)(\s*"[\w_]+?"\s*:)', r'\1], \2', raw_str)

    #     # Fix unmatched double quotes in list items, e.g., "items": ["a", "b]
    #     raw_str = re.sub(
    #         r'("items"\s*:\s*\[\s*"[^"]+",\s*"[^"\]]+)\]\}',
    #         lambda m: m.group(1) + '"]}', raw_str
    #     )

    #     # Normalize whitespace
    #     raw_str = raw_str.replace('\n', ' ').replace('\t', ' ')
    #     raw_str = re.sub(r'\s{2,}', ' ', raw_str)

    #     # Step 3: Try demjson3 parser (very lenient)
    #     try:
    #         return demjson3.decode(raw_str)
    #     except Exception:
    #         pass

    #     # Step 4: Fallback — return the raw string with an error
    #     return {
    #         "error": "[ERROR] Could not parse JSON",
    #         "raw": raw_str[:3000]  # Truncate to avoid huge dumps
    #     }

    def try_fix_json(self,raw_str):
        # Step 1: Try native JSON
        try:
            return json.loads(raw_str)
        except json.JSONDecodeError:
            pass

        raw_str = raw_str.strip()
        raw_str = re.sub(r"```(?:json)?|```", "", raw_str, flags=re.IGNORECASE).strip()
        raw_str = re.sub(r",(\s*[}\]])", r"\1", raw_str)
        raw_str = re.sub(r'("score"\s*:\s*\d+(\.\d+)?)"', r"\1", raw_str)
        raw_str = re.sub(r'("weaknesses"\s*:\s*\[[^\]]+?)(\s*"[\w_]+?"\s*:)', r'\1], \2', raw_str)

        # Fix unmatched quotes in lists
        raw_str = re.sub(
            r'("items"\s*:\s*\[\s*"[^"]+",\s*"[^"\]]+)\]\}',
            lambda m: m.group(1) + '"]}', raw_str
        )

        raw_str = raw_str.replace('\n', ' ').replace('\t', ' ')
        raw_str = re.sub(r'\s{2,}', ' ', raw_str)

        # Fix deeply nested 'analysis' inside 'score'
        raw_str = re.sub(
            r'("score"\s*:\s*\{.*?)(,\s*"analysis"\s*:\s*\{)',
            lambda m: m.group(1) + '}' + m.group(2),
            raw_str,
            flags=re.DOTALL
        )

        # Step 3: Try demjson3
        try:
            return demjson3.decode(raw_str)
        except Exception:
            pass

        return {
            "error": "[ERROR] Could not parse JSON",
            "raw": raw_str[:3000]
        }
    # def run(self, jd_file, resume_folder):
    #     job_text = extract_text(jd_file)
    #     output = []

    #     for file in os.listdir(resume_folder):
    #         if not file.lower().endswith(('.pdf', '.docx', '.txt')):
    #             continue

    #         path = os.path.join(resume_folder, file)
    #         resume_text = extract_text(path)

    #         prompt = (
    #             "SYSTEM PROMPT: Use the system prompt embedded in GroqLLM.\n\n"
    #             f"Job Description:\n{job_text}\n\n"
    #             f"Candidate Resume:\n{resume_text}\n\n"
    #             "Output only a clean and valid JSON object. "
    #             "Do not include markdown formatting (like ```json). "
    #             "Do not include explanations or extra text before or after the JSON. "
    #             "Use JSON format. Ensure that all brackets, quotes, and commas are properly placed. "
    #             "Do not place objects inside arrays unless they are properly nested. "
    #             "Make sure the 'name' field contains the candidate's full name. "
    #             "Return the name of the university also along with the degree of the candidate. "
    #             "Avoid duplicate keys. Ensure each section (e.g., soft_skills, certifications, analysis) "
    #             "appears only once and is correctly structured. "
    #             "Return only the JSON object. "
    #             "Please analyze and score this candidate as per the criteria in the system prompt. "
    #             "Return a detailed JSON with score components, red flags, bonus points, and analysis."
    #         )

    #         try:
    #             llm_response = self.llm._call(prompt)
    #         except Exception as e:
    #             output.append({
    #                 "filename": file,
    #                 "score_data": {
    #                     "error": f"[ERROR] LLM call failed: {e}"
    #                 }
    #             })
    #             continue

    #         score_data = self.try_fix_json(llm_response)

    #         if score_data is None:
    #             output.append({
    #                 "filename": file,
    #                 "score_data": {
    #                     "error": "[ERROR] Failed to parse JSON.",
    #                     "raw_response": llm_response
    #                 }
    #             })
    #             continue

    #         output.append({
    #             "filename": file,
    #             "score_data": score_data
    #         })

    #     return output
    
    def run_single(self, jd_file, resume_file):
        job_text = extract_text(jd_file)
        resume_text = extract_text(resume_file)

        prompt = (
            "SYSTEM PROMPT: Use the system prompt embedded in GroqLLM."
            f"Job Description:{job_text}"
            f"Candidate Resume:{resume_text}"
            "Ensure the JSON output does not contain escaped characters like \\n, \\\\, or \\/. The response must be plain, readable JSON with standard characters only."

           
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

        score_data = self.try_fix_json(llm_response)

        if score_data is None:
            return {
                "filename": os.path.basename(resume_file),
                "score_data": {
                    "error": "[ERROR] Failed to parse JSON.",
                    "raw_response": llm_response
                }
            }

        return {
            "filename": os.path.basename(resume_file),
            "score_data": score_data
        }





