from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from api.v1.schemas.student import StudentRegisterRequest, StudentCreate
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.models.student import Student as StudentModel
from api.v1.models.student_face_record import StudentFace
from api.v1.services.face_service import get_face_service

router = APIRouter(tags=["Students"])


@router.post("/register", response_model=StudentRegisterRequest)
async def register_student_face(
    matric_no: str = Form(..., description="Student matriculation number"),
    full_name: str = Form(..., description="Student full name"),
    email: str | None = Form(None, description="Student email (optional)"),
    dept: str | None = Form(None, description="Department (optional)"),
    file: UploadFile = File(..., description="Face photo (JPEG/PNG, max 4MB)"),
    db: Session = Depends(get_db),
):
    """
    Register a student with their face photo.
    
    This endpoint:
    1. Validates the uploaded image (type and size)
    2. Detects a face in the image
    3. Generates a 512-dim embedding using FaceNet512
    4. Creates/updates the student record
    5. Stores the face embedding for future recognition
    
    Returns the registered student data.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uploaded file must be an image (JPEG, PNG, etc.)"
        )
    
    contents = await file.read((1 << 22) + 1)
    if len(contents) > (1 << 22):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail="Image too large. Maximum size is 4MB."
        )
    
    # 3. Detect face and generate embedding
    face_service = get_face_service()
    try:
        embedding = face_service.process_image_bytes(contents)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Face processing failed: {e}"
        )
    
    image_path = file.filename
    
    student = StudentModel.fetch_unique(db, matric_no=matric_no)
    if student is None:
        student = StudentModel(matric_no=matric_no, full_name=full_name)
        student.insert(db, commit=True)
    
    # 6. Check if student already has a face registered
    existing_face = StudentFace.fetch_unique(db, student_id=student.id)
    if existing_face:
        existing_face.embedding = embedding
        existing_face.image_path = image_path
        existing_face.update(db, commit=True)
    else:
        # Create new face record
        face = StudentFace(student_id=student.id, embedding=embedding, image_path=image_path)
        face.insert(db, commit=True)
    
    student_data = StudentCreate(
        matric_no=matric_no, 
        full_name=full_name, 
        email=email, 
        dept=dept
    )
    return StudentRegisterRequest(student_data=student_data)