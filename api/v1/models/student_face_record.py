from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from api.v1.models.base_model import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
     from api.v1.models.student import Student

class StudentFace(BaseModel):
     __tablename__ = "student_faces"
    
     id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
     student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, unique=True)
     student: Mapped["Student"] = relationship("Student", back_populates="face", uselist=False)

     embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=False)
     image_path: Mapped[str] = mapped_column(String(512), nullable=True)
     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))