import io
import pandas as pd
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.schema_service import schema_service

client = TestClient(app)


# Helper to create mock CSV files in-memory
def create_mock_csv(data: dict) -> bytes:
    df = pd.DataFrame(data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return stream.getvalue().encode("utf-8")


# Helper to create mock XLSX files in-memory
def create_mock_xlsx(data: dict) -> bytes:
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    df.to_excel(stream, index=False)
    return stream.getvalue()


def test_upload_invalid_format():
    """Asserts that uploading a file with an unsupported format returns HTTP 400."""
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/api/v1/upload/import", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_empty_file():
    """Asserts that uploading an empty file returns HTTP 400."""
    files = {"file": ("test.csv", b"", "text/csv")}
    response = client.post("/api/v1/upload/import", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_invalid_structure():
    """Asserts that uploading an invalid/malformed CSV structure returns HTTP 400."""
    # A CSV file without any column headers or data
    files = {"file": ("test.csv", b"\n\n\n", "text/csv")}
    response = client.post("/api/v1/upload/import", files=files)
    assert response.status_code == 400


def test_upload_duplicate_columns():
    """Asserts that uploading a dataset with duplicate column names is rejected with HTTP 400."""
    csv_bytes = b"col1,col1,col2\n1,2,3\n4,5,6\n"
    files = {"file": ("dup_cols.csv", csv_bytes, "text/csv")}
    response = client.post("/api/v1/upload/preview", files=files)
    assert response.status_code == 400
    assert "duplicate column" in response.json()["detail"].lower()


def test_upload_corrupted_csv():
    """Asserts that uploading a corrupted CSV triggers a structure parse error with HTTP 400."""
    # Invalid UTF-8 sequence or completely malformed CSV structure
    corrupted_bytes = b"\xff\xfe\x00\x00malformed_csv_no_headers"
    files = {"file": ("corrupted.csv", corrupted_bytes, "text/csv")}
    response = client.post("/api/v1/upload/preview", files=files)
    assert response.status_code == 400
    assert "corrupted or invalid" in response.json()["detail"].lower()


def test_upload_corrupted_xlsx():
    """Asserts that uploading a corrupted XLSX triggers a structural error with HTTP 400."""
    corrupted_bytes = b"not_a_valid_xlsx_zip_file_signature"
    files = {
        "file": (
            "corrupted.xlsx",
            corrupted_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    response = client.post("/api/v1/upload/preview", files=files)
    assert response.status_code == 400
    assert "corrupted or invalid" in response.json()["detail"].lower()


def test_upload_column_row_limits():
    """Asserts that uploading files that exceed row or column limits is rejected."""
    # Test exceeding column limit (setting max columns to 2 for test)
    with patch("backend.app.config.settings.max_dataset_columns", 2):
        data = {"col1": [1, 2], "col2": [3, 4], "col3": [5, 6]}
        csv_bytes = create_mock_csv(data)
        files = {"file": ("test.csv", csv_bytes, "text/csv")}
        response = client.post("/api/v1/upload/import", files=files)
        assert response.status_code == 400
        assert "column limit" in response.json()["detail"].lower()

    # Test exceeding row limit (setting max rows to 2 for test)
    with patch("backend.app.config.settings.max_dataset_rows", 2):
        data = {"col1": [1, 2, 3, 4]}
        csv_bytes = create_mock_csv(data)
        files = {"file": ("test.csv", csv_bytes, "text/csv")}
        response = client.post("/api/v1/upload/import", files=files)
        assert response.status_code == 400
        assert "row limit" in response.json()["detail"].lower()


def test_csv_upload_preview_workflow():
    """Asserts that the preview endpoint reads and returns metadata without writing to the database."""
    # Create test data
    data = {"name": ["Alice", "Bob"], "age": [25, 30]}
    csv_bytes = create_mock_csv(data)
    files = {"file": ("sales_data.csv", csv_bytes, "text/csv")}

    # Reset schema cache
    schema_service.clear_cache()

    # Run preview endpoint
    response = client.post("/api/v1/upload/preview", files=files)
    assert response.status_code == 200
    res_data = response.json()

    # Assert return structure
    assert res_data["rows"] == 2
    assert res_data["columns"] == 2
    assert "sales_data" in res_data["dataset_name"]
    assert "age" in res_data["column_names"]
    assert res_data["column_types"]["age"] == "INTEGER"
    assert len(res_data["preview"]) == 2

    # Assert that table was NOT created in the database by checking active datasets list
    list_response = client.get("/api/v1/datasets")
    assert not any(
        d["dataset_name"] == res_data["dataset_name"] for d in list_response.json()
    )


def test_xlsx_upload_and_import_workflow():
    """Asserts that a valid Excel file can be parsed, previewed, imported, and queried, then deleted."""
    data = {"category": ["Tech", "Home"], "revenue": [12000.50, 4500.00]}
    xlsx_bytes = create_mock_xlsx(data)
    files = {
        "file": (
            "q2_report.xlsx",
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    # 1. Test preview
    prev_resp = client.post("/api/v1/upload/preview", files=files)
    assert prev_resp.status_code == 200
    prev_data = prev_resp.json()
    dataset_name = prev_data["dataset_name"]
    assert "q2_report" in dataset_name

    # 2. Test import
    # Rewind file bytes
    files = {
        "file": (
            "q2_report.xlsx",
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    imp_resp = client.post("/api/v1/upload/import", files=files)
    assert imp_resp.status_code == 200
    imp_data = imp_resp.json()
    assert imp_data["dataset_name"] == dataset_name
    assert imp_data["rows"] == 2

    # 3. Verify it exists in dataset list
    list_resp = client.get("/api/v1/datasets")
    assert list_resp.status_code == 200
    assert any(d["dataset_name"] == dataset_name for d in list_resp.json())

    # 4. Verify preview endpoint for existing dataset
    single_prev_resp = client.get(f"/api/v1/datasets/{dataset_name}/preview")
    assert single_prev_resp.status_code == 200
    assert single_prev_resp.json()["rows"] == 2

    # 5. Check if the schema cache is cleared and picks it up
    from backend.app.database import SessionLocal

    db = SessionLocal()
    try:
        schema_context = schema_service.get_schema_context(db)
        assert dataset_name in schema_context
        assert "revenue NUMERIC" in schema_context or "revenue" in schema_context
    finally:
        db.close()

    # 6. E2E query verification on the imported dataset (mocking Gemini SQL reply)
    with patch(
        "backend.app.services.sql_generation_service.llm_service.generate_sql"
    ) as mock_generate:
        mock_generate.return_value = f'SELECT category, revenue FROM "{dataset_name}" ORDER BY revenue DESC LIMIT 1'
        payload = {"question": "What is our highest revenue category in Q2?"}
        query_resp = client.post("/api/v1/query", json=payload)
        assert query_resp.status_code == 200
        q_data = query_resp.json()
        assert q_data["success"] is True
        assert len(q_data["data"]) == 1
        assert q_data["data"][0]["category"] == "Tech"

    # 7. Test deletion
    del_resp = client.delete(f"/api/v1/datasets/{dataset_name}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"

    # 8. Check that it is removed from lists and schema
    list_resp = client.get("/api/v1/datasets")
    assert not any(d["dataset_name"] == dataset_name for d in list_resp.json())

    db = SessionLocal()
    try:
        schema_context = schema_service.get_schema_context(db)
        assert dataset_name not in schema_context
    finally:
        db.close()
