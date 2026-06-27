import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.request import QueryRequest
from backend.app.models.response import QueryResponse
from backend.app.services.sql_generation_service import sql_generation_service
from backend.app.services.guard_service import guard_service
from backend.app.services.db_service import db_service
from backend.app.services.history_service import history_service
from backend.app.utils.logger import logger
from backend.app.utils.rate_limiter import rate_limit_query

router = APIRouter()


@router.post(
    "/query", response_model=QueryResponse, dependencies=[Depends(rate_limit_query)]
)
def run_natural_language_query(payload: QueryRequest, db: Session = Depends(get_db)):
    """Orchestrates Text-to-SQL generation, AST validation, execution, and automatic SQL self-repair."""
    start_time = time.time()
    user_question = payload.question
    generated_sql = None
    sanitized_sql = None

    try:
        # 1. Translate question to SQL statement
        generated_sql = sql_generation_service.generate_query(db, user_question)

        if "UNSUPPORTED_QUERY" in generated_sql:
            raise ValueError(
                "The requested query is not supported by the current database schema."
            )

        # 2. Check query format and apply row caps using AST parser
        sanitized_sql = guard_service.validate_and_sanitize_sql(generated_sql)

        # 3. Submit SELECT query statement to PostgreSQL engine
        query_results = db_service.execute_select_query(db, sanitized_sql)

        duration_ms = (time.time() - start_time) * 1000
        history_service.record_query(
            user_question, sanitized_sql, "SUCCESS", duration_ms
        )

        return QueryResponse(
            success=True,
            sql=sanitized_sql,
            data=query_results,
            execution_time_ms=duration_ms,
        )

    except Exception as primary_error:
        # If execution fails, attempt automatic query self-healing
        error_msg = str(primary_error)
        logger.warning(
            f"Primary execution pipeline failed: {error_msg}. Triggering automatic SQL repair..."
        )

        if generated_sql and "UNSUPPORTED_QUERY" not in generated_sql:
            try:
                # Generate repaired SQL statement using context schemas
                repaired_sql = sql_generation_service.repair_query(
                    db, generated_sql, error_msg
                )

                # Re-validate corrected SQL statement
                sanitized_sql = guard_service.validate_and_sanitize_sql(repaired_sql)

                # Re-execute corrected SELECT query
                query_results = db_service.execute_select_query(db, sanitized_sql)

                duration_ms = (time.time() - start_time) * 1000
                history_service.record_query(
                    user_question, sanitized_sql, "REPAIRED_SUCCESS", duration_ms
                )

                return QueryResponse(
                    success=True,
                    sql=sanitized_sql,
                    data=query_results,
                    execution_time_ms=duration_ms,
                )
            except Exception as repair_error:
                logger.error(
                    f"Automatic query repair operation failed: {str(repair_error)}"
                )
                error_msg = (
                    f"Primary Error: {error_msg} | Repair Error: {str(repair_error)}"
                )

        duration_ms = (time.time() - start_time) * 1000
        history_service.record_query(
            user_question,
            sanitized_sql or generated_sql or "N/A",
            "FAILED",
            duration_ms,
        )

        return QueryResponse(
            success=False,
            sql=sanitized_sql or generated_sql,
            error=error_msg,
            execution_time_ms=duration_ms,
        )
