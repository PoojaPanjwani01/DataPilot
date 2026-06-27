from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from backend.app.utils.logger import logger


class DBService:
    def execute_select_query(self, db: Session, sql_query: str) -> list[dict]:
        """Runs validated SELECT queries, sanitizing results through Pandas for serialization safety."""
        try:
            logger.info(f"Submitting query statement to database driver: {sql_query}")

            result = db.execute(text(sql_query))
            columns = result.keys()
            rows = result.fetchall()

            # Load into Pandas for type sanitization
            df = pd.DataFrame(rows, columns=columns)

            # Scrub database Null types (NaN/NaT) which break Pydantic serialization
            df = df.where(pd.notnull(df), None)

            records = df.to_dict(orient="records")
            logger.info(
                f"Database execution succeeded. Fetched: {len(records)} records."
            )
            return records

        except Exception as e:
            logger.error(f"SQL execution error on database layer: {str(e)}")
            raise RuntimeError(f"Database execution exception: {str(e)}") from e


db_service = DBService()
