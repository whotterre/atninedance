from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class StudentCreate(BaseModel):
    matric_no: str
    full_name: str
    email: Optional[EmailStr] = None
    dept: Optional[str] = None
    
class StudentRegisterRequest(BaseModel):
    student_data: StudentCreate

class FaceEmbeddingResponse(BaseModel):
    id: int
    student_id: int
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True
    
class StudentResponse(BaseModel):
    id: int
    matric_number: str
    full_name: str
    email: Optional[str]
    dept: Optional[str]
    face_embeddings: List[FaceEmbeddingResponse] = []
    created_at: datetime
    
    class Config: 
        from_attributes = True


