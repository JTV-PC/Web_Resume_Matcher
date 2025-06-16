from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional
 
 


class PDFDocumentBase(BaseModel):
    filename: str
 
class PDFDocumentCreate(PDFDocumentBase):
    pass
 
class PDFDocument(PDFDocumentBase):
    id: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: Optional[datetime] = None
 
    class Config:
        from_attributes = True
    
class JobDescriptionBase(BaseModel):
    title: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescription(JobDescriptionBase):
    id: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True



class MatchLogEntry(BaseModel):
    jd_uuid: str
    resume_uuid: str
    filename: str
    score_data: Dict
