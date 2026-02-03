from fastapi import APIRouter
from .student import router as student_router
from .attendance import router as attendance_router
central_router = APIRouter()

central_router.include_router(student_router, prefix="/students")
central_router.include_router(attendance_router, prefix="/attendance")
