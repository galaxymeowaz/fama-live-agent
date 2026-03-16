# Use a lightweight official Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory
WORKDIR /app

# Install system dependencies (e.g., for Pillow or reCAPTCHA requests if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install via pip
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose the API port
EXPOSE 8000

# Start the FastAPI Uvicorn server
# Bind to the dynamic $PORT injected by Google Cloud Run
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"
