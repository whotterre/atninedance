from fastapi import APIRouter
from .student import router as student_router

central_router = APIRouter()

central_router.include_router(student_router)

