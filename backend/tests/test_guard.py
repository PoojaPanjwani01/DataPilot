import pytest
from backend.app.services.guard_service import guard_service


def test_guard_valid_select():
    """Asserts that normal SELECT queries pass safety audits."""
    sql = "SELECT * FROM customers LIMIT 10"
    sanitized = guard_service.validate_and_sanitize_sql(sql)
    assert "LIMIT 10" in sanitized
    assert "SELECT" in sanitized


def test_guard_limit_injection():
    """Asserts that query limits are injected programmatically if omitted."""
    sql = "SELECT * FROM customers"
    sanitized = guard_service.validate_and_sanitize_sql(sql)
    assert "LIMIT 100" in sanitized


def test_guard_limit_override():
    """Asserts that limits larger than the maximum cap are reduced to 100."""
    sql = "SELECT * FROM customers LIMIT 500"
    sanitized = guard_service.validate_and_sanitize_sql(sql)
    assert "LIMIT 100" in sanitized


def test_guard_multi_statement_blocked():
    """Asserts that stacked/multi-statement SQL queries are blocked."""
    sql = "SELECT * FROM customers; DROP TABLE customers;"
    with pytest.raises(ValueError, match="Only single statements are permitted"):
        guard_service.validate_and_sanitize_sql(sql)


@pytest.mark.parametrize(
    "query",
    [
        "DROP TABLE customers;",
        "DELETE FROM orders WHERE order_id = 1;",
        "UPDATE products SET price = 0.00;",
        "INSERT INTO customers (first_name) VALUES ('Hacked');",
        "ALTER TABLE order_items ADD COLUMN hack VARCHAR(100);",
        "TRUNCATE TABLE orders;",
    ],
)
def test_guard_mutations_blocked(query):
    """Asserts that DDL/DML mutation queries are caught and blocked by the AST parser."""
    with pytest.raises(
        ValueError,
        match="Write and schema alterations are prohibited|Only SELECT statements are permitted",
    ):
        guard_service.validate_and_sanitize_sql(query)
