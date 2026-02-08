FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    libxcb1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies, then ensure only headless OpenCV is installed
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y opencv-python 2>/dev/null || true

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
