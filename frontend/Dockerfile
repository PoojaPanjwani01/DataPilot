# Production-Grade Dockerfile for Streamlit Frontend Dashboard
FROM python:3.11-slim

WORKDIR /app

# Install runtime utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python package requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit config and frontend source
COPY .streamlit/ ./.streamlit/
COPY frontend/ ./frontend/

EXPOSE 8501

# Command configurations to run headless streamlit instance
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.maxUploadSize=50"]
