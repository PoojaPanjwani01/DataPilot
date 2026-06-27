# DataPilot Deployment & Setup Guide

This document describes how to deploy, configure, run, and troubleshoot the DataPilot platform locally or within Docker containers.

---

## ⚙️ Environment Variables Reference

Create a `.env` configuration file in the project's root folder. The following keys are supported:

| Key | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Environment mode (`development` or `production`). |
| `DEBUG` | `true` | Enables detailed stack trace outputs and verbose logging. |
| `DATABASE_URL` | `postgresql://...` | Connection URI for the restricted read-only role (`db_readonly`). |
| `DATABASE_WRITE_URL` | `postgresql://...` | Connection URI for dataset managers to import dynamic data. |
| `GEMINI_API_KEY` | None | API Key required to authenticate requests against Google Gemini API. |
| `QUERY_TIMEOUT_SECONDS` | `10` | Hard latency threshold (seconds) for query execution sessions. |
| `MAX_ROWS_RETURNED` | `100` | Fallback limit size inserted into SELECT query statements. |
| `BACKEND_PORT` | `8000` | Port mapping for FastAPI backend server gateway. |
| `FRONTEND_PORT` | `8501` | Port mapping for the Streamlit web client. |

---

## 🐳 Docker Deployment (Recommended)

DataPilot includes a complete Docker Compose configuration to provision the backend, frontend, and PostgreSQL database automatically.

### Commands
1. **Launch Containers**:
   ```bash
   docker compose up -d --build
   ```
2. **Check Container Status**:
   ```bash
   docker compose ps
   ```
3. **Follow Application Logs**:
   ```bash
   docker compose logs -f
   ```
4. **Tear Down Stack**:
   ```bash
   docker compose down
   ```

---

## 💻 Manual Local Setup

If you prefer to run DataPilot outside of containers, follow these steps:

### 1. Database Setup
Ensure PostgreSQL is active. Connect as a superuser and execute the initialization and data seeding scripts:
```bash
# Connect and initialize database structures
psql -U postgres -d postgres -f db/init/01_init_db.sql

# Seed demo customer and order tables
psql -U postgres -d ai_sql_agent -f db/init/02_seed_data.sql
```

### 2. Python Environment Installation
DataPilot requires **Python 3.11**. Create and configure a local virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Backend Services
Start the FastAPI REST API gateway using Uvicorn:
```bash
uvicorn backend.app.main:app --port 8000 --reload
```

### 4. Start Frontend Client
Launch the Streamlit interface:
```bash
streamlit run frontend/app.py --server.port 8501
```

---

## 🔍 Troubleshooting Guide

### 1. Database Connection Failure
* **Problem**: The backend service fails to connect to the PostgreSQL instance or throws `OperationalError`.
* **Solutions**:
  - **Docker Setup**: Ensure `DATABASE_URL` in `.env` references `db` as the hostname (e.g., `postgresql://...@db:5432/...`) rather than `localhost`.
  - **Local Setup**: Verify that the PostgreSQL service is active (on Windows, check Services for `postgresql-x64-15`).
  - Check that the `db_readonly` and `dataset_manager` credentials defined in `.env` match those created by `db/init/01_init_db.sql`.

### 2. Google Gemini API Rate Limits (429 HTTP Error)
* **Problem**: API queries return `429 Resource Exhausted` error states.
* **Solutions**:
  - Google Gemini API free-tier keys enforce a limit of 15 Requests Per Minute (RPM). Wait 30-60 seconds for sliding windows to reset.
  - For unit tests, mocks are configured to bypass remote API calls. Ensure testing is triggered via standard `pytest` commands.

### 3. Port Allocation Conflicts
* **Problem**: Streamlit or FastAPI fails to start, displaying "Port 8501 or 8000 already in use" exceptions.
* **Solutions**:
  - Find and terminate processes running on these ports:
    - **Windows (PowerShell)**:
      ```powershell
      Get-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess | Stop-Process -Force
      ```
    - **Linux/macOS**:
      ```bash
      kill -9 $(lsof -t -i:8501)
      ```
