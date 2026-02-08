FROM python:3.12

WORKDIR /app

COPY requirements.txt .

# Install dependencies, then force headless OpenCV (removes GUI version if deepface installed it)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null || true && \
    pip install --no-cache-dir --force-reinstall opencv-python-headless && \
    python -c "import cv2; print(f'OpenCV {cv2.__version__} installed successfully')"

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
