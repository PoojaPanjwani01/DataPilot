import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from backend.app.services.db_service import db_service
from backend.app.services.prompt_service import prompt_service
from backend.app.services.llm_service import llm_service
from backend.app.models.request import QueryRequest
from backend.app.models.response import QueryResponse


# --- DBService Unit Tests ---
def test_db_service_execute_valid(db_session):
    """Verifies that DBService executes valid SQL queries and formats results through Pandas."""
    sql = "SELECT COUNT(*) as count FROM customers"
    results = db_service.execute_select_query(db_session, sql)
    assert len(results) == 1
    assert results[0]["count"] == 100


def test_db_service_execute_invalid_syntax(db_session):
    """Verifies that DBService traps and wraps syntax errors correctly."""
    sql = "SELECT * FROM non_existent_table"
    with pytest.raises(RuntimeError, match="Database execution exception"):
        db_service.execute_select_query(db_session, sql)


# --- PromptService Unit Tests ---
def test_prompt_service_preloads():
    """Asserts that PromptService populates its templates into cache during initialization."""
    assert "system_prompt.txt" in prompt_service._cache
    assert "sql_generation.txt" in prompt_service._cache
    assert "sql_fixing.txt" in prompt_service._cache


def test_prompt_service_formatting():
    """Asserts variables are mapped into prompt generation templates."""
    schema = "CREATE TABLE t (id INT);"
    question = "List all rows"
    prompt = prompt_service.get_sql_generation_prompt(schema, question)
    assert schema in prompt
    assert question in prompt


# --- Request/Response Models Unit Tests ---
def test_query_request_validation():
    """Verifies boundary validations on API Input payload schemas."""
    # Valid question
    req = QueryRequest(question="Show me top products")
    assert req.question == "Show me top products"

    # Too short
    with pytest.raises(ValidationError):
        QueryRequest(question="Hi")

    # Too long
    with pytest.raises(ValidationError):
        QueryRequest(question="a" * 2001)


def test_query_response_validation():
    """Verifies serialization models on API response payloads."""
    res = QueryResponse(
        success=True,
        sql="SELECT * FROM customers",
        data=[{"id": 1, "name": "Liam"}],
        execution_time_ms=12.34,
    )
    assert res.success is True
    assert len(res.data) == 1
    assert res.execution_time_ms == 12.34


# --- Gemini Failure Unit Tests ---
@patch("google.genai.Client")
def test_gemini_empty_response(mock_client_class):
    """Verifies that empty string replies from Gemini trigger validation errors."""
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = ""
    with patch.object(llm_service, "client", mock_client):
        with pytest.raises(RuntimeError, match="Failed to generate query text"):
            llm_service.generate_sql("system", "prompt")


@patch("google.genai.Client")
def test_gemini_api_timeout(mock_client_class):
    """Verifies that Gemini API exception conditions are trapped gracefully."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception(
        "API Connection Timeout"
    )
    with patch.object(llm_service, "client", mock_client):
        with pytest.raises(RuntimeError, match="Failed to generate query text"):
            llm_service.generate_sql("system", "prompt")
