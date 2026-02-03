# AtNineDance - Face Recognition Attendance System

A real-time classroom attendance system using facial recognition with a standard webcam.

## What's Implemented

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/students/register` | Register student with face photo |

### Features
- **Student Registration**: Upload face photo + student details → face detected → 512-dim embedding generated → stored in PostgreSQL with pgvector
- **Face Detection**: OpenCV Haar cascades for fast face detection
- **Face Embeddings**: DeepFace with FaceNet512 model (512-dimensional vectors)
- **Vector Storage**: PostgreSQL + pgvector for efficient similarity search

### Database Models
- `students` — id, full_name, matric_no, registered_at, timestamps
- `student_faces` — id, student_id (FK), embedding (Vector(512)), image_path, timestamps
- `attendance_sessions` — id, title, course_code, duration, status, counts, timestamps
- `attendance_records` — id, session_id (FK), detected_time, confidence_score, status

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

### 7. Test the API

Open http://localhost:8000/docs for interactive Swagger UI.

Example registration request:

```powershell
curl -X POST "http://localhost:8000/api/v1/students/register" `
  -F "matric_no=STU001" `
  -F "full_name=John Doe" `
  -F "file=@photo.jpg"
```

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
└── ml/                    # ML models and training (future)
```

---

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **Face Detection**: OpenCV
- **Face Embeddings**: DeepFace (FaceNet512)
- **Migrations**: Alembic

