# Production-Grade Dockerfile for FastAPI Backend Gateway
FROM python:3.11-slim

WORKDIR /app

# Install runtime utilities (curl is required for docker health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python package requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and configurations to match workspace absolute layout
COPY backend/ ./backend/
COPY prompts/ ./prompts/
COPY data/ ./data/

EXPOSE 8000

# Set Python search path to include workdir root
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
