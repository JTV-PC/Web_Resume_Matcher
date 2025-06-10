from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
 
 


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
 