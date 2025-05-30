import os
import re
import pymupdf
import docx
import requests
 
def extract_text(file_path):

    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""

def extract_text_from_pdf(path):
    doc = pymupdf.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
 
def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
 
def serpapi_search(query):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not found in environment variables")
    params = {

        "engine": "google",

        "q": query,

        "api_key": api_key,

        "num": 3

    }
 
    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()
    snippets = []

    for result in data.get("organic_results", []):
        snippet = result.get("snippet")
        if snippet:
            snippets.append(snippet)
    return " ".join(snippets) if snippets else ""
 
def extract_colleges(resume_text):
    pattern = re.compile(
        r'(?i)\b((?:[A-Z][a-z&,\.\-]*(?:\s+|\.))*'
        r'(?:University|College|Institute|Polytechnic|School|Academy)'
        r'(?:\s+of\s+[A-Z][a-z&,\.\-]*(?:\s+[A-Z][a-z&,\.\-]*)*)?)\b'

    )

    lines = resume_text.split('\n')
    college_names = set()
    for line in lines:
        matches = pattern.findall(line)
        for match in matches:
            college_names.add(match.strip())
    return list(college_names)

 






































































































