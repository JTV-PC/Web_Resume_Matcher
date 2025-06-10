import mimetypes
import os
import uuid
import psycopg2
from typing import List
from fastapi import Depends, FastAPI, File, Form, Response, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from matcher import ResumeMatcherCore
import models
import schemas
from database import engine,get_db as getdb


models.Base.metadata.create_all(bind=engine)

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
    email: str
    contact_no: str
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
            cursor.execute("""
                SELECT name, email, contact_no, final_score, 
                       technical_skills_score, experience_score,
                       education_score, soft_skills_score, certifications_score
                FROM resume_analysis;
            """)
            return cursor.fetchall()
    except Exception as e:
        return {"error": str(e)}

@app.get("/scores/{name}", response_model=ResumeScore)
def get_score_by_name(name: str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, email, contact_no, final_score, 
                       technical_skills_score, experience_score,
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
    

# @app.post("/evaluate_batch")
# async def evaluate_batch(
#     jd: UploadFile = File(...),
#     resumes: List[UploadFile] = File(...)
# ):
#     matcher = ResumeMatcherCore()
#     os.makedirs("uploads", exist_ok=True)

#     jd_path = f"./uploads/{jd.filename}"
#     with open(jd_path, "wb") as f:
#         f.write(await jd.read())

#     results = []
#     for resume in resumes:
#         resume_path = f"./uploads/{resume.filename}"
#         with open(resume_path, "wb") as f:
#             f.write(await resume.read())

#         result = matcher.run_single(jd_path, resume_path)
#         results.append(result)

#     return results


@app.post("/evaluate_batch")
async def evaluate_batch(
    jd: UploadFile = File(...),
    jd_uuid: str = Form(...),
    resumes: List[UploadFile] = File(...),
    resume_uuids: List[str] = Form(...)
):
    matcher = ResumeMatcherCore()
    os.makedirs("uploads", exist_ok=True)

    jd_path = f"./uploads/{jd_uuid}_{jd.filename}"
    with open(jd_path, "wb") as f:
        f.write(await jd.read())

    results = []
    for resume, uuid in zip(resumes, resume_uuids):
        resume_path = f"./uploads/{uuid}_{resume.filename}"
        with open(resume_path, "wb") as f:
            f.write(await resume.read())

        result = matcher.run_single(jd_path, resume_path,uuid)
        result["resume_uuid"] = uuid  # optional: include uuid in result
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

        jd_path = "./uploads/{jd.filename}"
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



@app.get("/get_resume_delta/", )
def get_score_by_name(conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM resume_analysis;
            """)
            row = cursor.fetchall()
            if row:
                return row
            raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]

# @app.post("/pdf/upload/", response_model=schemas.PDFDocument)
# async def upload_pdf(
#     file: UploadFile = File(...),
#     db: Session = Depends(getdb)
# ):
#     # Validate file size
#     file_size = 0
#     content = await file.read()
#     file_size = len(content)
   
#     if file_size > MAX_FILE_SIZE:
#         raise HTTPException(
#             status_code=400,
#             detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024}MB"
#         )
   
#     # Validate file type
#     content_type = mimetypes.guess_type(file.filename)[0]
#     if content_type not in ALLOWED_CONTENT_TYPES:
#         raise HTTPException(
#             status_code=400,
#             detail=f"File type {content_type} not allowed. Only PDF files are accepted."
#         )
   
#     # Create PDF document record
#     db_pdf = models.PDFDocument(
#         filename=file.filename,
#         content_type=content_type,
#         file_data=content,
#         file_size=file_size
#     )
   
#     db.add(db_pdf)
#     db.commit()
#     db.refresh(db_pdf)
   
#     return db_pdf
 

@app.post("/pdf/upload/", response_model=List[schemas.PDFDocument])
async def upload_multiple_pdfs(
    files: List[UploadFile] = File(...),
    uuids: List[str] = Form(...),
    db: Session = Depends(getdb)
):
    uploaded_docs = []

    for file, uuid in zip(files, uuids):
        content = await file.read()
        content_type = mimetypes.guess_type(file.filename)[0]
        file_size = len(content)

        db_pdf = models.PDFDocument(
            id=uuid,  # <-- set UUID from frontend
            filename=file.filename,
            content_type=content_type,
            file_data=content,
            file_size=file_size,
        )
        db.add(db_pdf)
        db.commit()
        db.refresh(db_pdf)
        uploaded_docs.append(db_pdf)

    return uploaded_docs


@app.get("/pdf/{pdf_id}", response_model=schemas.PDFDocument)
def get_pdf_metadata(pdf_id: int, db: Session = Depends(getdb)):
    db_pdf = db.query(models.PDFDocument).filter(models.PDFDocument.id == pdf_id).first()
    if db_pdf is None:
        raise HTTPException(status_code=404, detail="PDF document not found")
    return db_pdf
 
@app.get("/pdf/{pdf_id}/download")
def download_pdf(pdf_id: str, db: Session = Depends(getdb)):
    db_pdf = db.query(models.PDFDocument).filter(models.PDFDocument.id == pdf_id).first()
    if db_pdf is None:
        raise HTTPException(status_code=404, detail="PDF document not found")
    return Response(
        content=db_pdf.file_data,
        media_type=db_pdf.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={db_pdf.filename}"
        }
    )
 
    