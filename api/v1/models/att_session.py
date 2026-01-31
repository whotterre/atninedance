from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.v1.models.base_model import BaseModel

if TYPE_CHECKING:
    from api.v1.models.att_record import AttendanceRecord

class AttendanceSession(BaseModel):
    __tablename__ = "attendance_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    
    # Session information
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    course_code: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Duration & timing
    scheduled_duration: Mapped[int] = mapped_column(Integer, default=60, nullable=False)  # minutes
    actual_duration: Mapped[int] = mapped_column(Integer, nullable=True)  
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True) 
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), 
        default='scheduled',  #'active', 'completed', 'cancelled'
        nullable=False
    )
    
    
    # Statistics (computed)
    total_students: Mapped[int] = mapped_column(Integer, default=0)
    present_count: Mapped[int] = mapped_column(Integer, default=0)
    late_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="session")
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        if self.status != 'active':
            return False
        if not self.start_time:
            return False
        
        # Session is active if within scheduled duration (or manually stopped)
        if self.end_time:
            return False  # Already ended
            
        # Auto-end after scheduled duration
        auto_end_time = self.start_time + timedelta(minutes=self.scheduled_duration)
        return datetime.now(timezone.utc) < auto_end_time
    
    @property
    def elapsed_minutes(self) -> int:
        """How many minutes have passed since start."""
        if not self.start_time or self.end_time:
            return 0
        elapsed = datetime.now(timezone.utc) - self.start_time
        return int(elapsed.total_seconds() // 60)
    
    @property
    def remaining_minutes(self) -> int:
        """How many minutes until auto-end."""
        if not self.is_active:
            return 0
        remaining = (self.start_time + timedelta(minutes=self.scheduled_duration)) - datetime.now(timezone.utc)
        return max(0, int(remaining.total_seconds() // 60))