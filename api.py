import shutil
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from pydantic import BaseModel
from typing import List
from psycopg2.extras import RealDictCursor
from matcher import ResumeMatcherCore
import os


app = FastAPI()

# Allow frontend (e.g., PyQt or browser) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For security, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ResumeScore(BaseModel):
    name: str
    final_score: float
    technical_skills_score: float
    experience_score: float
    education_score: float
    soft_skills_score: float
    certifications_score: float


@app.get("/scores", response_model=List[ResumeScore])
def get_scores(conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM resume_analysis;
            """)
            rows = cursor.fetchall()
        return rows
    except Exception as e:
        return {"error": str(e)}



@app.get("/scores/{name}", response_model=ResumeScore)
def get_score_by_name(name: str,conn=Depends(get_db)):
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
        else:
            raise HTTPException(status_code=404, detail="Candidate not found")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    


# @app.post("/evaluate_batch")
# async def evaluate_batch(
#     jd: UploadFile = File(...),
#     resumes: List[UploadFile] = File(...)
# ):
#     # Prepare temp folders
#     os.makedirs("temp/jd", exist_ok=True)
#     os.makedirs("temp/resumes", exist_ok=True)

#     # Save JD file
#     jd_path = f"temp/jd/{jd.filename}"
#     with open(jd_path, "wb") as f:
#         shutil.copyfileobj(jd.file, f)

#     # Save all resumes
#     resume_folder = "temp/resumes"
#     for resume in resumes:
#         resume_path = os.path.join(resume_folder, resume.filename)
#         with open(resume_path, "wb") as f:
#             shutil.copyfileobj(resume.file, f)

#     try:
#         matcher = ResumeMatcherCore()
#         result = matcher.run(jd_path, resume_folder)
#         return JSONResponse(content=result)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})



@app.post("/evaluate_batch")
async def evaluate_pair(
    jd: UploadFile = File(...),
    resume: UploadFile = File(...)
):
    os.makedirs("temp/jd", exist_ok=True)
    os.makedirs("temp/resume", exist_ok=True)

    # Save JD
    jd_path = f"temp/jd/{jd.filename}"
    with open(jd_path, "wb") as f:
        shutil.copyfileobj(jd.file, f)

    # Save Resume
    resume_path = f"temp/resume/{resume.filename}"
    with open(resume_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    try:
        matcher = ResumeMatcherCore()
        result = matcher.run_single(jd_path, resume_path)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})