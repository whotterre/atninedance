# AtNineDance - Face Recognition Attendance System

A real-time classroom attendance system using facial recognition with a standard webcam.

## What's Implemented

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/students/register` | Register student with face photo |
| `POST` | `/api/v1/attendance/sessions` | Create a new attendance session |
| `POST` | `/api/v1/attendance/sessions/{id}/recognize` | Recognize faces and record attendance |

### Features
- **Student Registration**: Upload face photo + student details → face detected → 512-dim embedding generated → stored in PostgreSQL with pgvector
- **Session Management**: Create timed attendance sessions with automatic expiration
- **Face Recognition**: Detect multiple faces in an image and match against registered students
- **Attendance Recording**: Automatically record attendance with confidence scores, prevent duplicates
- **Face Detection**: OpenCV Haar cascades for fast face detection
- **Face Embeddings**: DeepFace with FaceNet512 model (512-dimensional vectors)
- **Vector Storage**: PostgreSQL + pgvector for efficient similarity search
- **Cosine Similarity**: Match faces with >60% confidence threshold

### Database Models
- `students` — id, full_name, matric_no, registered_at, timestamps
- `student_faces` — id, student_id (FK), embedding (Vector(512)), image_path, timestamps
- `attendance_sessions` — id, title, course_code, scheduled_duration, start_time, end_time, status, counts, timestamps
- `attendance_records` — id, session_id (FK), student_id (FK), detected_time, confidence_score, status

---

## API Usage

### 1. Register a Student

```powershell
curl -X POST "http://localhost:8000/api/v1/students/register" `
  -F "matric_no=STU001" `
  -F "full_name=John Doe" `
  -F "file=@photo.jpg"
```

### 2. Create an Attendance Session

```powershell
curl -X POST "http://localhost:8000/api/v1/attendance/sessions" `
  -H "Content-Type: application/json" `
  -d '{"title": "CSC101 - Week 5", "duration_minutes": 45, "course_code": "CSC101"}'
```

Response:
```json
{
  "session_id": 1,
  "title": "CSC101 - Week 5",
  "start_time": "2026-02-03T10:00:00Z",
  "scheduled_duration": 45,
  "status": "active"
}
```

### 3. Recognize Faces and Record Attendance

```powershell
curl -X POST "http://localhost:8000/api/v1/attendance/sessions/1/recognize" `
  -F "image=@classroom.jpg"
```

Response:
```json
{
  "session_id": 1,
  "total_faces_detected": 3,
  "new_attendance_records": 2,
  "recognized_students": [
    {"student_id": 1, "matric_no": "STU001", "name": "John Doe", "confidence": 0.87},
    {"student_id": 2, "matric_no": "STU002", "name": "Jane Smith", "confidence": 0.92}
  ],
  "session_status": "active",
  "minutes_remaining": 42
}
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- PostgreSQL with pgvector extension
- (Optional) GPU for faster inference

### 1. Clone and create virtual environment

```powershell
git clone <repo-url>
cd atninedance
python -m venv dev_env
.\dev_env\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set up PostgreSQL

Create database and enable pgvector:

```sql
CREATE DATABASE face_db;
\c face_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Configure environment

Create a `.env` file or set the environment variable:

```powershell
$env:DATABASE_URL="postgresql://postgres:password@localhost:5432/face_db"
```

### 5. Run migrations

```powershell
alembic upgrade head
```

### 6. Start the server

```powershell
uvicorn main:app --reload
```

Server runs at http://localhost:8000

Open http://localhost:8000/docs for interactive Swagger UI.

---

## Project Structure

```
atninedance/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic config
├── alembic/               # Database migrations
├── api/
│   ├── db/
│   │   └── database.py    # SQLAlchemy engine & session
│   └── v1/
│       ├── models/        # SQLAlchemy ORM models
│       ├── routes/        # API endpoints
│       ├── schemas/       # Pydantic request/response models
│       └── services/      # Business logic (face_service.py)
└── ml/                    # ML models and training
```

---

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **Face Detection**: OpenCV Haar cascades
- **Face Embeddings**: DeepFace (FaceNet512)
- **Migrations**: Alembic
- **Face Embeddings**: DeepFace (FaceNet512)
- **Migrations**: Alembic

