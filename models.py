from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.sql import func
from database import Base
 

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
 
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    file_data = Column(LargeBinary)
    file_size = Column(Integer)  # Size in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
 