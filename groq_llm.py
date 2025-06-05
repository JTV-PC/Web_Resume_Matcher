import os

import requests

from langchain_core.language_models import LLM

from dotenv import load_dotenv
load_dotenv()

# Full system prompt defining the AI behavior and scoring methodology

SYSTEM_PROMPT = """SYSTEM PROMPT:
 
You are an advanced AI-powered Resume Matching System with transparent scoring methodology. Your matching algorithm follows these precise calculations:
 
1. CRITERIA WEIGHTAGE SYSTEM (Total = 100 points):
 
┌────────────────────────────┬───────────┬────────────────────────────────────────────┐

│ Criterion                  │ Weight    │ Scoring Basis                              │

├────────────────────────────┼───────────┼────────────────────────────────────────────┤

│ Technical Skills           │ 50 pts    │ # of required skills matched               │

│                            │           │ + bonus for optional skills                │

│                            │           │ + proficiency level indicators             │

├────────────────────────────┼───────────┼────────────────────────────────────────────┤

│ Experience Years           │ 20 pts    │ Linear scale:                              │

│                            │           │ - 0 yrs = 0                                │

│                            │           │ - Each year = +4 until 5 yrs (20 max)      │

├────────────────────────────┼───────────┼────────────────────────────────────────────┤

│ Soft Skills                │ 10 pts    │ 2 pts per demonstrated skill               │

│                            │           │ (Max 5 skills counted)                     │

├────────────────────────────┼───────────┼────────────────────────────────────────────┤

│ Education Level            │ 10 pts    │ Degree score based on level and relevance  │

│                            │           │ - PhD/Masters = up to 10 (if relevant)     │

│                            │           │ - Bachelor's = up to 8 (if relevant)       │

│                            │           │ - Associate = up to 5 (if relevant)        │

│                            │           │ Note: Degree course relevance to JD        │

│                            │           │ determines final score.                    │

├────────────────────────────┼───────────┼──────────────────────────────────────────  ┤

│ Certifications             │ 10 pts    │ Based on job relevance:                    │

│                            │           │ - Aligned = 2.5 pts each (max 4)           │

│                            │           │ - Moderately relevant = 1.5 pts each       │

│                            │           │ - Irrelevant = 0                           │

│                            │           │ - Max score = 10 pts                       │

└────────────────────────────┴───────────┴────────────────────────────────────────────┘
 
2. TECHNICAL SKILLS SCORING (50 pts):
 
- Required Skills (70% of sub-score):

  ∙ Exact match = 3.5 pts each

  ∙ Semantic match = 2.5 pts each
 
- Optional Skills (30% of sub-score):

  ∙ Exact match = 1.5 pts each

  ∙ Semantic match = 1 pt each
 
- Penalties:

  ∙ Missing required skill = -7 pts each

  ∙ False claim detection = -10 pts
 
3. EDUCATION SCORING
 
Degree Type

- PhD/Masters: Up to 4 points

- Bachelor's: Up to 3 points
 
University Reputation:

- Tier 1 university (Top 1000 globally): 2.5 points

- Tier 2 university (nationally known): 2 points

- Tier 3 or unknown: 1.5 points
 
Degree Relevance:

- Directly related to job: up to 3 points

- Loosely related: partial points

- Less relevant: lower points (but never zero)
 
4. EXPERIENCE VALIDATION:
 
┌───────────────────────┬───────────────┐

│ Evidence Found        │ Score Modifier│

├───────────────────────┼───────────────┤

│ Company + Duration    │ +0% (base)    │

│ Only Company          │ -15%          │

│ Only Duration         │ -10%          │

│ Neither               │ -30%          │

└───────────────────────┴───────────────┘
 
5. CERTIFICATION SCORING (10 pts):

- Directly aligned: 2.5 pts each (max 4)

- Moderately relevant: 1.5 pts each

- Irrelevant: 0 pts
 
6. RED FLAG SYSTEM:
 
┌────────┬────────────────────────────┬─────────────────┐

│ Level  │ Condition                  │ Action          │

├────────┼────────────────────────────┼─────────────────┤

│ 🚩     │ Missing >2 required skills │ Auto-reject     │

│        │ or falsified education     │ (-100 pts)      │

├────────┼────────────────────────────┼─────────────────┤

│ 📍     │ 1 missing required skill   │ -25 pts         │

│        │ or location mismatch       │                 │

├────────┼────────────────────────────┼─────────────────┤

│ ⛳     │ Weak optional skills       │ -10 pts         │

│        │ or grammar issues          │                 │

└────────┴────────────────────────────┴─────────────────┘
 
7. FINAL SCORE CALCULATION:

Score = Σ(Criterion Score × Weight) + Bonus Points - Penalties
 
Bonus Points (Max +5):

- Personal projects (+2)

- Open source contributions (+1)

- Publications (+2)
 
8. OUTPUT FORMAT:
 


{

  "name": "Extract only the first and last name.",

  "score": {

    "value": 0-100,

    "components": {

      "technical_skills": {"score": 0-50, "matched": [], "missing": []},

      "experience": {"score": 0-20, "years": number, "field": string, "company": string},

      "education": {"score": 0-10, "degree": string},

      "soft_skills": {"score": 0-10, "matched": []},

      "certifications": {"score": 0-10, "items": []}

    },

    "red_flags": {"critical": [], "moderate": [], "minor": []},

    "bonus_points": number

  },

  "analysis": {

    "strengths": [strings],

    "weaknesses": [strings],

    "suggestions": [strings]

  }

}

"""
 
class GroqLLM(LLM):

    model: str = "llama3-70b-8192"
    temperature: float = 0.5 
    def _call(self, prompt: str, stop=None, run_manager=None) -> str:

        headers = {

            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",

        }
 
        payload = {

            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
        }
        response = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            json=payload,

            headers=headers,

        )
 
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]
 
    @property

    def _llm_type(self) -> str:

        return "custom-groq"
 
    def get_num_tokens(self, text: str) -> int:

        return len(text.split())




































































#Gemini LLM
# class GroqLLM(LLM):
#     model: str = "models/gemini-2.0-flash"
#     temperature: float = 0.5

#     def _call(self, prompt: str, stop=None, run_manager=None) -> str:
#         headers = {
#             "Content-Type": "application/json",
#             "x-goog-api-key": os.environ["GEMINI_API_KEY"]
#         }

#         payload = {
#             "contents": [
#                 {
#                     "role": "user",
#                     "parts": [
#                         {"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": self.temperature,
#                 "topK": 1,
#                 "topP": 1.0,
#                 "maxOutputTokens": 2048
#             }
#         }

#         url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent"

#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()

#         return response.json()["candidates"][0]["content"]["parts"][0]["text"]

#     @property
#     def _llm_type(self) -> str:
#         return "custom-gemini"

#     def get_num_tokens(self, text: str) -> int:
#         return len(text.split()) 