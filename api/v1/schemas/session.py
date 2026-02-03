from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    title: str
    duration_minutes: int
    course_code: Optional[str] = None
