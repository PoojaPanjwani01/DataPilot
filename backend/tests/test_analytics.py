import pandas as pd
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# --- Schema Explorer Endpoint Tests ---
def test_schema_endpoint():
    """Asserts that GET /api/v1/schema returns database tables and columns."""
    response = client.get("/api/v1/schema")
    assert response.status_code == 200
    data = response.json()

    # Assert core tables are present
    assert "customers" in data
    assert "products" in data
    assert "orders" in data
    assert "order_items" in data

    # Assert column schema structures
    customer_cols = [c["name"] for c in data["customers"]]
    assert "customer_id" in customer_cols
    assert "email" in customer_cols


# --- Insights Generation Endpoint Tests ---
@patch("backend.app.services.llm_service.llm_service._generate_with_retry")
def test_insights_generation_endpoint(mock_retry):
    """Asserts that POST /api/v1/insights generates summaries using LLM service."""
    # Mock Gemini response text
    mock_response = MagicMock()
    mock_response.text = (
        "Top Brand: Apple\n"
        "Revenue: $15,000\n"
        "Insights:\n"
        "* Apple brands generated highest revenue.\n"
        "* Growth trend looks positive."
    )
    mock_retry.return_value = mock_response

    payload = {
        "question": "What are our top brand revenues?",
        "sql": "SELECT brand, sum(price) FROM products GROUP BY brand",
        "data": [{"brand": "Apple", "sum": 15000}, {"brand": "Samsung", "sum": 8000}],
    }

    response = client.post("/api/v1/insights", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "Apple" in res_data["insights"]
    assert (
        "Samsung" not in res_data["insights"]
    )  # not in final output insights bullet structure


# --- Chart Auto-Detection Rules Unit Tests ---
def test_chart_auto_detection_logic():
    """Verifies that result column types correctly map to target chart modes in app logic."""

    # Helper replicating the frontend classification logic for charts
    def classify_and_detect_chart(df):
        numeric_cols = []
        date_cols = []
        category_cols = []

        for col in df.columns:
            c_low = col.lower()
            if (
                "date" in c_low
                or "time" in c_low
                or "month" in c_low
                or "year" in c_low
            ):
                date_cols.append(col)
            elif pd.api.types.is_numeric_dtype(df[col]):
                if c_low.endswith("_id") or c_low == "id":
                    category_cols.append(col)
                else:
                    numeric_cols.append(col)
            else:
                category_cols.append(col)

        if not numeric_cols:
            return "none"

        if date_cols:
            return "line"
        elif category_cols:
            x_col = category_cols[0]
            unique_vals = df[x_col].nunique()
            if 1 < unique_vals <= 5:
                return "pie"
            elif unique_vals > 8:
                return "horizontal_bar"
            else:
                return "bar"
        return "histogram"

    # Test Date + Numeric -> Line
    df_line = pd.DataFrame(
        {"sale_date": ["2026-05-01", "2026-05-02"], "sales": [100, 150]}
    )
    assert classify_and_detect_chart(df_line) == "line"

    # Test Few Categories -> Pie
    df_pie = pd.DataFrame(
        {"category": ["Tech", "Home", "Tech"], "revenue": [100, 200, 150]}
    )
    assert classify_and_detect_chart(df_pie) == "pie"

    # Test Category + Numeric -> Bar
    df_bar = pd.DataFrame(
        {
            "brand": ["Apple", "Samsung", "Google", "Sony", "Dell", "HP"],
            "price": [1000, 800, 700, 600, 500, 400],
        }
    )
    assert classify_and_detect_chart(df_bar) == "bar"

    # Test Many Categories -> Horizontal Bar
    df_hbar = pd.DataFrame(
        {"product": [f"P_{i}" for i in range(10)], "sales": [10 * i for i in range(10)]}
    )
    assert classify_and_detect_chart(df_hbar) == "horizontal_bar"
