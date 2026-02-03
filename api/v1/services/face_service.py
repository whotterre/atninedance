"""
Face detection and embedding service for student registration.

This module provides:
- Face detection using OpenCV Haar cascades (fast, no GPU needed)
- Face embedding generation using DeepFace (uses FaceNet model by default)

Usage:
    from api.v1.services.face_service import FaceService

    service = FaceService()
    embedding = service.process_image_bytes(image_bytes)
"""

import cv2
import numpy as np
from typing import Optional, List
from sqlalchemy.orm import Session

from api.v1.models.student import Student


class FaceService:
    """Service for detecting faces and generating embeddings."""

    EMBEDDING_DIM = 512  # FaceNet512 outputs 512-dim vectors

    def __init__(self):
        """Initialize face detector. DeepFace model loads lazily on first use."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._deepface_model = None

    def _load_deepface(self):
        """Lazy-load DeepFace to avoid slow startup."""
        if self._deepface_model is None:
            try:
                from deepface import DeepFace

                self._deepface_model = DeepFace
            except ImportError:
                raise ImportError(
                    "DeepFace not installed. Run: pip install deepface tf-keras"
                )
        return self._deepface_model

    def bytes_to_cv2(self, image_bytes: bytes) -> np.ndarray:
        """Convert raw image bytes to OpenCV BGR image array."""
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode image bytes")
        return image

    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect and extract the largest face from an image.

        Args:
            image: BGR image as numpy array (from cv2)

        Returns:
            160x160 cropped face image, or None if no face found
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)  # more sensitive
        )

        if len(faces) == 0:
            return None

        # Take largest face by area
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face = image[y : y + h, x : x + w]
        face = cv2.resize(face, (160, 160))

        return face

    def get_embedding(self, image: np.ndarray) -> List[float]:
        """
        Generate a 512-dimensional face embedding using DeepFace/FaceNet.

        Args:
            image: BGR image as numpy array (full image or cropped face)

        Returns:
            List of 512 floats representing the face embedding

        Raises:
            ValueError: If no face is detected in the image
        """
        DeepFace = self._load_deepface()

        # Convert BGR to RGB for DeepFace
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        try:
            # DeepFace.represent returns list of dicts with 'embedding' key
            result = DeepFace.represent(
                img_path=rgb_image,
                model_name="Facenet512",  # 512-dim output
                enforce_detection=True,  # raise if no face
                detector_backend="opencv",  # fast detection
            )
            embedding = result[0]["embedding"]
            return embedding
        except Exception as e:
            raise ValueError(f"Face embedding failed: {e}")

    def process_image_bytes(self, image_bytes: bytes) -> List[float]:
        """
        Full pipeline: bytes -> detect face -> generate embedding.

        This is the main method to call from routes.

        Args:
            image_bytes: Raw image file bytes (JPEG, PNG, etc.)

        Returns:
            512-dimensional face embedding as list of floats

        Raises:
            ValueError: If image cannot be decoded or no face detected
        """
        # Decode bytes to OpenCV image
        image = self.bytes_to_cv2(image_bytes)

        # Get embedding (DeepFace handles detection internally)
        embedding = self.get_embedding(image)

        return embedding

    def recognize_faces(self, image: np.ndarray, db: Session):
        """
        Finds faces in image and match with registered students.

        Args:
            image: BGR image as numpy array
            db: SQLAlchemy database session

        Returns:
            List of dicts with student_id, matric_no, name, confidence, bbox
        """
        from api.v1.models.student_face_record import StudentFace

        gray_version = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect all faces in the image
        faces = self.face_cascade.detectMultiScale(
            gray_version, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        recognized_students = []

        for x, y, w, h in faces:
            face_img = image[y : y + h, x : x + w]
            face_img = cv2.resize(face_img, (160, 160))

            try:
                embedding = self.get_embedding(face_img)
            except ValueError:
                # Skip faces that can't be embedded
                continue

            best_match = None
            best_similarity = 0.0

            # Query all registered face embeddings with their students
            all_faces = db.query(StudentFace).all()

            for face_record in all_faces:
                similarity = self.cosine_similarity(
                    embedding, list(face_record.embedding)
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = face_record.student

            # Accept matches with confidence > 60%
            if best_match and best_similarity > 0.6:
                recognized_students.append(
                    {
                        "student_id": best_match.id,
                        "matric_no": best_match.matric_no,
                        "name": best_match.full_name,
                        "confidence": round(float(best_similarity), 4),
                        "bbox": [int(x), int(y), int(w), int(h)],
                    }
                )
        return recognized_students

    def cosine_similarity(self, vec_one: List[float], vec_two: List[float]) -> float:
        """Calculates how similar two embeddings are (0 to 1)"""
        vec_one = np.array(vec_one)
        vec_two = np.array(vec_two)

        # Compute the dot product
        dot_product = np.dot(vec_one, vec_two)

        # Compute the magnitude of both vectors
        norm_one = np.linalg.norm(vec_one)
        norm_two = np.linalg.norm(vec_two)

        # Prevent zero division error
        if norm_one == 0 or norm_two == 0:
            return 0.0

        cos_similarity = dot_product / (norm_one * norm_two)

        return (cos_similarity + 1) / 2


# Singleton instance for reuse (avoids reloading model)
_face_service: Optional[FaceService] = None


def get_face_service() -> FaceService:
    """Get or create the singleton FaceService instance."""
    global _face_service
    if _face_service is None:
        _face_service = FaceService()
    return _face_service
