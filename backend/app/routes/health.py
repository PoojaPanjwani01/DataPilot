from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.app.database import get_db
from backend.app.utils.logger import logger

router = APIRouter(prefix="/health", tags=["system-health"])


@router.get("", status_code=200)
def check_general_health():
    """Returns general health status of the application API."""
    logger.info("General API health check requested.")
    return {"status": "healthy"}


@router.get("/db", status_code=200)
def check_db_health(db: Session = Depends(get_db)):
    """Verifies operational connectivity of target database pool."""
    logger.info("Database connectivity health check requested.")
    try:
        # Validate query execution capability using basic SELECT statement
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "database": "disconnected",
                "error": "Unable to communicate with the database.",
            },
        )
