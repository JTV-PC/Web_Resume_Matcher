from sqlalchemy import JSON, Column, ForeignKey, Integer, String, DateTime, LargeBinary
from sqlalchemy.sql import func
from database import Base
import uuid

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
 
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    file_data = Column(LargeBinary)
    file_size = Column(Integer)  # Size in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)            # Optional: e.g., "Senior Backend Engineer"
    content_type = Column(String)
    file_data = Column(LargeBinary)
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MatchLog(Base):
    __tablename__ = "match_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    jd_uuid = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    resume_uuid = Column(String, ForeignKey("pdf_documents.id"), nullable=False)
    resume_filename = Column(String, nullable=False)
    score_data = Column(JSON, nullable=False)  # includes name, email, score, analysis etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
