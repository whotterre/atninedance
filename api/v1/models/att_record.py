from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, String, ForeignKey, Numeric
from api.v1.models.base_model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from api.v1.models.att_session import AttendanceSession
    from api.v1.models.student import Student


class AttendanceRecord(BaseModel):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    session_id: Mapped[int] = mapped_column(ForeignKey("attendance_sessions.id"), nullable=False, index=True)
    session: Mapped["AttendanceSession"] = relationship("AttendanceSession", back_populates="attendance_records")

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    student: Mapped["Student"] = relationship("Student")

    detected_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="absent", nullable=False)

    
