from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from api.v1.models.base_model import BaseModel


class Student(BaseModel):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, autoincrement=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    matric_no: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))



