import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.database_url)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provides a transaction-isolated database session for integration testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    """Resets rate limiter in-memory storage before each test function execution."""
    from backend.app.utils.rate_limiter import _rate_limits
    _rate_limits.clear()
