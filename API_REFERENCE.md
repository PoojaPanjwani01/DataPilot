# DataPilot API Reference Guide

This document describes all API endpoints hosted on the FastAPI backend gateway, including schema payloads and response models.

---

## 🚦 Endpoints Summary

| Method | Endpoint | Description | Rate Limit |
| :--- | :--- | :--- | :--- |
| **GET** | `/health` | API general status | None |
| **GET** | `/health/db` | Database pool connectivity | None |
| **POST** | `/api/v1/query` | Translate, validate, and execute questions | 30 requests/min |
| **POST** | `/api/v1/insights` | Generate AI insights from data rows | 30 requests/min |
| **POST** | `/api/v1/upload/preview` | Preview file layout without DB import | 10 uploads/hour |
| **POST** | `/api/v1/upload/import` | Validate and import CSV/XLSX into DB | 10 uploads/hour |
| **GET** | `/api/v1/datasets` | List dynamically imported datasets | None |
| **GET** | `/api/v1/datasets/{name}/preview` | Get preview metadata of a specific dataset | None |
| **DELETE** | `/api/v1/datasets/{name}` | Drop dynamic dataset table | None |
| **GET** | `/api/v1/schema` | Browse active schemas, tables, and columns | None |

---

## 📝 Request & Response Details

### 1. Execute Conversational Query
- **Endpoint**: `POST /api/v1/query`
- **Request Body (JSON)**:
```json
{
  "question": "Average salary of each job title"
}
```
- **Response (200 OK - Success)**:
```json
{
  "success": true,
  "sql": "SELECT job_title, AVG(salary) AS avg_salary FROM employees GROUP BY job_title LIMIT 100",
  "data": [
    { "job_title": "Software Engineer", "avg_salary": 95000.00 },
    { "job_title": "Data Analyst", "avg_salary": 72000.00 }
  ],
  "error": null,
  "execution_time_ms": 142.15
}
```
- **Response (200 OK - Blocked/AST Injection Guard)**:
```json
{
  "success": false,
  "sql": null,
  "data": null,
  "error": "Query validation failed: Write and schema alterations are prohibited.",
  "execution_time_ms": 5.23
}
```

---

### 2. Generate AI Insights
- **Endpoint**: `POST /api/v1/insights`
- **Request Body (JSON)**:
```json
{
  "question": "Average salary of each job title",
  "sql": "SELECT job_title, AVG(salary) AS avg_salary FROM employees GROUP BY job_title LIMIT 100",
  "data": [
    { "job_title": "Software Engineer", "avg_salary": 95000.00 },
    { "job_title": "Data Analyst", "avg_salary": 72000.00 }
  ]
}
```
- **Response (200 OK)**:
```json
{
  "insights": "* Software Engineers earn the highest average salary ($95,000) among the listed roles.\n* Data Analysts follow with an average salary of $72,000."
}
```

---

### 3. File Upload Preview
- **Endpoint**: `POST /api/v1/upload/preview`
- **Request Body**: Multipart form data with a single binary `file`.
- **Response (200 OK)**:
```json
{
  "dataset_name": "uploaded_sales_data",
  "rows": 1000,
  "columns": 4,
  "column_types": {
    "order_id": "INTEGER",
    "product": "TEXT",
    "amount": "DECIMAL",
    "order_date": "DATE"
  },
  "preview": [
    { "order_id": 1, "product": "Laptop", "amount": 1200.00, "order_date": "2026-05-01" }
  ]
}
```

---

### 4. File Upload Import
- **Endpoint**: `POST /api/v1/upload/import`
- **Request Body**: Multipart form data with a single binary `file`.
- **Response (200 OK)**:
```json
{
  "status": "success",
  "dataset_name": "uploaded_sales_data",
  "rows_imported": 1000,
  "columns": 4
}
```

---

### 5. Schema Definitions
- **Endpoint**: `GET /api/v1/schema`
- **Response (200 OK)**:
```json
{
  "employees": [
    { "name": "employee_id", "type": "INTEGER" },
    { "name": "job_title", "type": "VARCHAR(100)" },
    { "name": "salary", "type": "NUMERIC(12,2)" }
  ],
  "uploaded_sales_data": [
    { "name": "order_id", "type": "INTEGER" },
    { "name": "amount", "type": "NUMERIC(12,2)" }
  ]
}
```
