from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

# Construct PostgreSQL options for statement execution timeouts (converted to milliseconds)
timeout_ms = settings.query_timeout_seconds * 1000
connect_args = {"options": f"-c statement_timeout={timeout_ms}"}

# Create connection pooler engine targeting read-only connection limits
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Exposes transactional database sessions using context isolation."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
