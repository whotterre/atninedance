from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import central_router
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="AtNineDance - Facial recognition attendance system",
    description="A facial recognition attendance system using computer vision",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount router
app.include_router(central_router, prefix="/api/v1")
