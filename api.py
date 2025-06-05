import os
import psycopg2
from typing import List
from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from matcher import ResumeMatcherCore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeScore(BaseModel):
    name: str
    final_score: float
    technical_skills_score: float
    experience_score: float
    education_score: float
    soft_skills_score: float
    certifications_score: float

def get_db():
    conn = psycopg2.connect(
        dbname="Resume_JD",
        user="postgres",
        password="admin",
        host="localhost",
        port=5433,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

@app.get("/scores", response_model=List[ResumeScore])
def get_scores(conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM resume_analysis;")
            return cursor.fetchall()
    except Exception as e:
        return {"error": str(e)}

@app.get("/scores/{name}", response_model=ResumeScore)
def get_score_by_name(name: str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, final_score, technical_skills_score, experience_score,
                       education_score, soft_skills_score, certifications_score
                FROM resume_analysis
                WHERE name = %s;
            """, (name,))
            row = cursor.fetchone()
            if row:
                return row
            raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/evaluate_batch")
async def evaluate_batch(
    jd: UploadFile = File(...),
    resumes: List[UploadFile] = File(...)
):
    matcher = ResumeMatcherCore()
    os.makedirs("uploads", exist_ok=True)

    jd_path = f"./uploads/{jd.filename}"
    with open(jd_path, "wb") as f:
        f.write(await jd.read())

    results = []
    for resume in resumes:
        resume_path = f"./uploads/{resume.filename}"
        with open(resume_path, "wb") as f:
            f.write(await resume.read())

        result = matcher.run_single(jd_path, resume_path)
        results.append(result)

    return results

@app.post("/retry_failed_resumes")
def retry_failed_resumes():
    matcher = ResumeMatcherCore()

    try:
        conn = psycopg2.connect(
            dbname="Resume_JD",
            user="postgres",
            password="admin",
            host="localhost",
            port=5433
        )
        cursor = conn.cursor()

        cursor.execute("SELECT filename FROM resume_parse_errors;")
        rows = cursor.fetchall()

        if not rows:
            return {"message": "No failed resumes to retry."}

        jd_path = "temp/jd/job_description.pdf"
        results = []

        for (filename,) in rows:
            resume_path = f"temp/resumes/{filename}"
            if not os.path.exists(resume_path):
                continue
            result = matcher.run_single(jd_path, resume_path)
            results.append(result)

        cursor.close()
        conn.close()

        return {"retries_attempted": len(rows)}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
