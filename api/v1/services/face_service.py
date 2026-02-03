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
import io


class FaceService:
    """Service for detecting faces and generating embeddings."""
    
    EMBEDDING_DIM = 512  # FaceNet512 outputs 512-dim vectors
    
    def __init__(self):
        """Initialize face detector. DeepFace model loads lazily on first use."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
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
            gray, 
            scaleFactor=1.1,  # more sensitive
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
        
        # Take largest face by area
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face = image[y:y+h, x:x+w]
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
                model_name="Facenet512",   # 512-dim output
                enforce_detection=True,     # raise if no face
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


# Singleton instance for reuse (avoids reloading model)
_face_service: Optional[FaceService] = None


def get_face_service() -> FaceService:
    """Get or create the singleton FaceService instance."""
    global _face_service
    if _face_service is None:
        _face_service = FaceService()
    return _face_service