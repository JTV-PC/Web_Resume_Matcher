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
#     jd_uuid: str = Form(...),
#     resumes: List[UploadFile] = File(...),
#     resume_uuids: List[str] = Form(...)
# ):
#     matcher = ResumeMatcherCore()
#     os.makedirs("uploads", exist_ok=True)

#     jd_path = f"./uploads/{jd_uuid}_{jd.filename}"
#     with open(jd_path, "wb") as f:
#         f.write(await jd.read())

#     results = []
#     for resume, uuid in zip(resumes, resume_uuids):
#         resume_path = f"./uploads/{uuid}_{resume.filename}"
#         with open(resume_path, "wb") as f:
#             f.write(await resume.read())

#         result = matcher.run_single(jd_path, resume_path,uuid)
#         result["resume_uuid"] = uuid  # optional: include uuid in result
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

    # Save JD file
    jd_path = f"./uploads/{jd_uuid}_{jd.filename}"
    with open(jd_path, "wb") as f:
        f.write(await jd.read())

    results = []

    # Evaluate each resume
    for resume, uuid in zip(resumes, resume_uuids):
        resume_path = f"./uploads/{resume.filename}"
        with open(resume_path, "wb") as f:
            f.write(await resume.read())

        # Run the match
        match_result = matcher.run_single(jd_path, resume_path, uuid)

        # Build a clean response entry
        results.append({
            "jd_uuid": jd_uuid, 
            "resume_uuid": uuid,
            **{k: v for k, v in match_result.items() if k not in {"score"}}  # add optional metadata
        })

    return results





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

@app.post("/jd/upload/", response_model=List[schemas.JobDescription])
async def upload_jds(
    files: List[UploadFile] = File(...),
    uuids: List[str] = Form(...),
    titles: List[str] = Form(...),
    db: Session = Depends(getdb)
):
    uploaded_jds = []

    for file, uuid, title in zip(files, uuids, titles):
        content = await file.read()
        content_type = mimetypes.guess_type(file.filename)[0]
        file_size = len(content)

        # Skip if this JD is already uploaded
        existing = db.query(models.JobDescription).filter_by(id=uuid).first()
        if existing:
            continue

        jd = models.JobDescription(
            id=uuid,
            title=title,
            content_type=content_type,
            file_data=content,
            file_size=file_size,
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)
        uploaded_jds.append(jd)

    return uploaded_jds

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




@app.get("/jd/{jd_id}", response_model=schemas.JobDescription)
def get_jd_by_id(jd_id: str, db: Session = Depends(getdb)):
    db_jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if db_jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return db_jd

@app.get("/jd/{jd_id}/download")
def download_jd(jd_id: str, db: Session = Depends(getdb)):
    db_jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if db_jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return Response(
        content=db_jd.file_data,
        media_type=db_jd.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={db_jd.title or jd_id}.pdf"
        }
    )

@app.get("/jds/", response_model=List[schemas.JobDescription])
def list_all_jds(db: Session = Depends(getdb)):
    return db.query(models.JobDescription).all()



@app.post("/logs/save/")
def save_match_logs(logs: List[schemas.MatchLogEntry], db: Session = Depends(getdb)):
    saved = []
    for log in logs:
        existing = db.query(models.MatchLog).filter_by(
            jd_uuid=log.jd_uuid,
            resume_uuid=log.resume_uuid
        ).first()

        if existing:
            continue  # Skip duplicate log

        entry = models.MatchLog(
            jd_uuid=log.jd_uuid,
            resume_uuid=log.resume_uuid,
            resume_filename=log.filename,
            score_data=log.score_data
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        saved.append(entry)

    return {"saved": len(saved)}
    