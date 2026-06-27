from backend.app.services.schema_service import schema_service


def test_schema_introspection_caching(db_session):
    """Asserts that schema introspection extracts target structures and utilizes cache memory."""
    # Reset schema state
    schema_service.clear_cache()
    assert schema_service._cached_schema is None

    # Populate schema DDL using db session
    schema = schema_service.get_schema_context(db_session)
    assert "customers" in schema
    assert "products" in schema
    assert "orders" in schema
    assert "order_items" in schema

    # Assert cache verification holds true
    assert schema_service._cached_schema == schema

    # Re-retrieve and check equality without querying database catalog metadata
    cached_schema = schema_service.get_schema_context(db_session)
    assert cached_schema == schema
