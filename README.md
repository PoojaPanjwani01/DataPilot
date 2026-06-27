# ⬡ DataPilot: Conversational AI Data Analyst

DataPilot is a production-grade, secure, and intuitive ChatGPT-style conversational AI data analyst platform. Built using **FastAPI**, **Streamlit**, **PostgreSQL**, and the **Google Gemini API**, it enables business stakeholders and technical developers alike to query databases using conversational English. DataPilot features automated Text-to-SQL translation, AST-based security validation, query execution performance tracking, and automatic SQL self-repair.

---

## Table of Contents
* [Project Overview](#-project-overview)
* [Features](#-features)
* [Screenshots](#-screenshots)
* [Architecture Overview](#-architecture-overview)
* [Technology Stack](#-technology-stack)
* [Installation Guide](#-installation-guide)
* [Usage Guide](#-usage-guide)
* [Dataset Upload Workflow](#-dataset-upload-workflow)
* [Future Improvements](#-future-improvements)
* [Detailed Documentation Links](#-detailed-documentation-links)

---

## Project Overview
DataPilot bridges the gap between conversational English query inputs and structured database queries. Users type questions (e.g., *"What is the average experience by industry?"*), and DataPilot translates the question to an optimized SQL statement, parses it using Abstract Syntax Tree (AST) validation to block unauthorized actions, executes the query against PostgreSQL using restricted read-only permissions, and renders results, charts, and AI-generated insights.

---

## Features
* **ChatGPT-Style Sidebar**: Fast switching between active and past conversation threads, with inline "+ New Analysis" buttons.
* **Persistent Dataset Upload**: A dedicated popover 옆 to the chat input enables immediate dataset preview, validation, and database import.
* **Execution Metadata**: Detailed telemetry including execution latency, row/column counts, and target database mappings displayed per message.
* **Collapsible Response Expanders**: Conversational answers contain nested, collapsible sections for the raw data tables, generated SQL, interactive Plotly charts, and business insights.
* **Automatic Self-Repair**: If SQL execution fails, DataPilot feeds the error back to Gemini to repair the query syntax and rerun it automatically.

---

## Screenshots

### Dashboard Overview
Displays platform KPIs (System Status, Datasets count, Schema Tables, Avg Latencies) along with query history logs and active dataset listings.
![Dashboard Overview](file:///C:/Users/POOJA/.gemini/antigravity/brain/35889443-d237-486a-ae2d-27cdf7e88031/dashboard_page_screenshot_1780232132683.png)

### AI Analyst Landing Page
The primary workspace displaying quick start suggestion chips and quick upload panels.
![AI Analyst Welcome](file:///C:/Users/POOJA/.gemini/antigravity/brain/35889443-d237-486a-ae2d-27cdf7e88031/ai_analyst_welcome_screenshot_1780232154727.png)

### Active Conversation Feed
Chronological user and assistant chat message thread highlighting Results, SQL, Charts, and Insights.
![Active Conversation](file:///C:/Users/POOJA/.gemini/antigravity/brain/35889443-d237-486a-ae2d-27cdf7e88031/active_conversation_screenshot_1780232171493.png)

### Dataset Upload Popover
Integrated drag-and-drop area next to the bottom chat input supporting CSV/XLSX uploads.
![Dataset Upload Flow](file:///C:/Users/POOJA/.gemini/antigravity/brain/35889443-d237-486a-ae2d-27cdf7e88031/dataset_upload_flow_screenshot_1780232189929.png)

### Schema Explorer
A two-panel table listing detailing column definitions and raw SQL datatypes.
![Schema Explorer](file:///C:/Users/POOJA/.gemini/antigravity/brain/35889443-d237-486a-ae2d-27cdf7e88031/schema_explorer_screenshot_1780232206415.png)

---

## Architecture Overview

The system runs on a decoupled client-server architecture:
1. **Frontend (Streamlit)**: Manages layout states, renders conversational message feeds, popovers, and Plotly visualization charts.
2. **Backend (FastAPI)**: Serves endpoints for SQL translation, file uploads, schema exploration, and insights generation.
3. **Database (PostgreSQL)**: Stores system data. Backend accesses the tables via a restricted read-only role (`db_readonly`) to guarantee data integrity.
4. **AI Gateway (Google Gemini)**: Translates natural language questions to SQL and translates query output to actionable insights.

For more details, see [ARCHITECTURE.md](file:///c:/Users/POOJA/Desktop/ai-sql-agent/ARCHITECTURE.md).

---

## Technology Stack
* **Frontend**: Streamlit, Plotly Express, Pandas, HTTPX
* **Backend**: FastAPI, Uvicorn, Pydantic, SQLAlchemy
* **Database**: PostgreSQL 15, SQLAlchemy, Psycopg2-binary
* **Security & Validation**: SQLGlot (AST Parsing), Python-multipart (Upload checks)
* **LLM**: Google GenAI SDK (Gemini 2.5 Flash)

---

## Installation Guide

### Prerequisites
* Docker and Docker Compose installed.
* Google Gemini API Key.

### Env Configuration
Create a `.env` file in the project root directory:
```ini
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql://db_readonly:readonly_user_pass@db:5432/ai_sql_agent
DATABASE_WRITE_URL=postgresql://dataset_manager:dataset_manager_pass@db:5432/ai_sql_agent
GEMINI_API_KEY=your_gemini_api_key_here
QUERY_TIMEOUT_SECONDS=10
MAX_ROWS_RETURNED=100
```

### Run with Docker (Recommended)
Launch the multi-service application stack:
```bash
docker compose up --build -d
```
* **DataPilot UI**: `http://localhost:8501`
* **API Documentation**: `http://localhost:8000/docs`

For details on local setups, check [DEPLOYMENT.md](file:///c:/Users/POOJA/Desktop/ai-sql-agent/DEPLOYMENT.md).

---

## Usage Guide
1. Open the browser at `http://localhost:8501`.
2. Navigate to **AI Analyst** in the sidebar.
3. Choose a suggestion chip or type your question in the chat input at the bottom (e.g. *"Show top 5 job titles by average salary"*).
4. Click and expand the response cards (Results, SQL, Charts, Insights) embedded directly in the message flow.
5. Create new chat threads by clicking **+ New Analysis** at the top of the sidebar.

---

## Dataset Upload Workflow
1. Click the **Upload Dataset** button next to the bottom chat input box.
2. Select a `.csv` or `.xlsx` file.
3. DataPilot validates metadata (max 50 MB, schema limits) and parses the file structure.
4. Preview the columns, detected datatypes, and first 10 rows.
5. Click **Confirm Import**. DataPilot automatically creates a database table (prefixed with `uploaded_`), grants read permissions, clears caches, and updates the LLM schema context so you can immediately query the dataset in the conversation.

---

## Future Improvements
* **Advanced Visualizations**: Support multi-axis line graphs, scatter plots, and correlation charts.
* **Vector Embeddings Cache**: Implement a semantic cache for past query translations to bypass the LLM for repeated questions.
* **Enhanced Multi-Schema Join**: Enable complex join generation across different database databases or uploaded tables.

---

## 📑 Detailed Documentation Links
* [Architecture & System Design](file:///c:/Users/POOJA/Desktop/ai-sql-agent/ARCHITECTURE.md)
* [API Reference Guide](file:///c:/Users/POOJA/Desktop/ai-sql-agent/API_REFERENCE.md)
* [Security Safeguards](file:///c:/Users/POOJA/Desktop/ai-sql-agent/SECURITY.md)
* [Deployment & Troubleshooting](file:///c:/Users/POOJA/Desktop/ai-sql-agent/DEPLOYMENT.md)
