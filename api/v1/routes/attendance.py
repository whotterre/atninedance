from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.att_record import AttendanceRecord
from api.v1.models.att_session import AttendanceSession
from api.v1.schemas.session import SessionCreate
from api.v1.services.face_service import get_face_service

router = APIRouter(tags=["Attendance"])


@router.get("/sessions", status_code=200)
async def list_sessions(
    db: Session = Depends(get_db)
):
    """Get all attendance sessions."""
    sessions = db.query(AttendanceSession).order_by(AttendanceSession.start_time.desc()).all()
    return [
        {
            "session_id": s.id,
            "title": s.title,
            "start_time": s.start_time,
            "scheduled_duration": s.scheduled_duration,
            "status": s.status,
            "course_code": s.course_code,
            "present_count": s.present_count or 0
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}", status_code=200)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific attendance session by ID."""
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    
    if not session:
        raise HTTPException(404, "Session not found")
    
    return {
        "session_id": session.id,
        "title": session.title,
        "description": session.description,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "scheduled_duration": session.scheduled_duration,
        "actual_duration": session.actual_duration,
        "status": session.status,
        "course_code": session.course_code,
        "total_students": session.total_students or 0,
        "present_count": session.present_count or 0,
        "late_count": session.late_count or 0
    }


@router.post("/sessions", status_code=201)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    Start a new attendance session.
    
    Example request:
    {
        "title": "CSC101 - Week 5",
        "duration_minutes": 45,
        "course_code": "CSC101"
    }
    """
    session = AttendanceSession(
        title=session_data.title,
        scheduled_duration=session_data.duration_minutes,
        course_code=session_data.course_code,
        start_time=datetime.now(timezone.utc),
        status='active'
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "title": session.title,
        "start_time": session.start_time,
        "scheduled_duration": session.scheduled_duration,
        "status": session.status
    }
    
@router.post("/sessions/{session_id}/end", status_code=200)
async def end_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """End an active attendance session."""
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.status == "completed":
        raise HTTPException(400, "Session is already ended")
    
    if session.status == "cancelled":
        raise HTTPException(400, "Session was cancelled")
    
    session.status = "completed"
    session.end_time = datetime.now(timezone.utc)
    
    if session.start_time:
        elapsed = session.end_time - session.start_time
        session.actual_duration = int(elapsed.total_seconds() // 60)
    
    db.commit()
    
    return {
        "session_id": session.id,
        "status": session.status,
        "end_time": session.end_time,
        "actual_duration": session.actual_duration
    }


@router.post("/sessions/{session_id}/recognize", status_code=200)
async def recognize_and_record(
    session_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in image and record attendance for a specific session.
    
    Upload an image containing one or more faces. The system will:
    1. Detect all faces in the image
    2. Generate embeddings and match against registered students
    3. Create attendance records for recognized students
    
    Returns list of recognized students and session status.
    """
    
    # Get the session record if it's active and exists
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id,
        AttendanceSession.status == "active"
    ).first()
    
    if not session:
        raise HTTPException(404, "Session not found or not active")

    
    # Check if session has expired
    sesh_end_time = session.start_time + timedelta(minutes=session.scheduled_duration)
    if datetime.now(timezone.utc) > sesh_end_time:
        session.status = "completed"
        db.commit()
        raise HTTPException(400, "Session has ended")
    
    # Read and validate image
    contents = await image.read()
    if len(contents) > (1 << 22):
        raise HTTPException(413, "Image too large. Maximum 4MB.")
    
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    # Process image and recognize faces
    face_service = get_face_service()
    try:
        cv2_image = face_service.bytes_to_cv2(contents)
        recognized = face_service.recognize_faces(cv2_image, db)
    except ValueError as e:
        raise HTTPException(400, f"Face processing failed: {e}")
    
    new_records = []
    
    for person in recognized:
        # Check if student already marked present in this session
        existing = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == person["student_id"]
        ).first()
        
        if not existing:
            record = AttendanceRecord(
                session_id=session_id,
                student_id=person["student_id"],
                confidence_score=person["confidence"],
                detected_time=datetime.now(timezone.utc),
                status="present"
            )
            db.add(record)
            new_records.append(person)
    
    # Update session counts
    if new_records:
        session.present_count = (session.present_count or 0) + len(new_records)
    
    db.commit()
    
    time_left_in_session = max(0, (sesh_end_time - datetime.now(timezone.utc)).seconds // 60)
    
    return {
        "session_id": session_id,
        "total_faces_detected": len(recognized),
        "new_attendance_records": len(new_records),
        "recognized_students": recognized,
        "session_status": session.status,
        "minutes_remaining": time_left_in_session
    }
        
        
    
    
    
    