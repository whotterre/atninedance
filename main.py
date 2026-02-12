from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import central_router
from api.config import get_settings
import logging


settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title=settings.APP_NAME,
    description="A facial recognition attendance system using computer vision",
    version="1.0.0",
    docs_url="/docs",
)

# Parse allowed origins from settings
if settings.ALLOWED_ORIGINS == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Specific origins: allow credentials
    allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount router
app.include_router(central_router, prefix="/api/v1")
