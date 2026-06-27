import os
import re
import time
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.utils.logger import logger


class DatasetService:
    def __init__(self):
        # Determine the write URL targeting the dataset_manager role
        self.db_write_url = settings.database_write_url
        if not self.db_write_url:
            db_url = settings.database_url
            if "db_readonly:readonly_user_pass" in db_url:
                self.db_write_url = db_url.replace(
                    "db_readonly:readonly_user_pass",
                    "dataset_manager:dataset_manager_pass",
                )
            else:
                self.db_write_url = db_url

        logger.info(
            "Initializing DatasetService with privileged write engine connection."
        )
        self.write_engine = create_engine(self.db_write_url, pool_pre_ping=True)

    def sanitize_table_name(self, filename: str) -> str:
        """Converts filename to a safe, sanitized SQL table name starting with 'uploaded_'."""
        # Get base name without extension
        base_name = os.path.splitext(os.path.basename(filename))[0]
        # Replace non-alphanumeric sequences with an underscore
        sanitized = re.sub(r"[^a-zA-Z0-9]+", "_", base_name)
        # Strip leading/trailing underscores and lowercase
        sanitized = sanitized.strip("_").lower()

        # Ensure it has a valid length/structure
        if not sanitized:
            sanitized = "dataset"

        return f"uploaded_{sanitized}"

    def get_unique_table_name(self, base_table_name: str) -> str:
        """Appends a timestamp suffix to a table name if it conflicts with an existing table."""
        inspector = inspect(self.write_engine)
        existing_tables = inspector.get_table_names()

        if base_table_name not in existing_tables:
            return base_table_name

        # Collision: Append timestamp to guarantee uniqueness
        timestamp = int(time.time())
        unique_name = f"{base_table_name}_{timestamp}"

        # Keep appending counter if somehow timestamp collides in rapid testing
        counter = 1
        while unique_name in existing_tables:
            unique_name = f"{base_table_name}_{timestamp}_{counter}"
            counter += 1

        return unique_name

    def import_dataset(self, df: pd.DataFrame, filename: str) -> dict:
        """Creates a table using the privileged write engine, imports data, and grants read permissions."""
        base_table_name = self.sanitize_table_name(filename)
        table_name = self.get_unique_table_name(base_table_name)

        logger.info(f"Importing dataset from file '{filename}' to table '{table_name}'")

        # Write to database using context manager
        with self.write_engine.begin() as conn:
            # Map columns to lowercase and replace spaces/special chars to prevent query generation bugs
            df_db = df.copy()
            df_db.columns = [
                re.sub(r"[^a-zA-Z0-9]+", "_", str(c)).strip("_").lower()
                for c in df_db.columns
            ]

            # Convert unsupported object types safely to text/string
            for col in df_db.columns:
                if df_db[col].dtype == "object":
                    df_db[col] = df_db[col].apply(
                        lambda x: None if pd.isna(x) else str(x)
                    )

            # Write rows in chunks
            df_db.to_sql(
                name=table_name, con=conn, index=False, if_exists="fail", chunksize=1000
            )

            # Explicitly grant read access to db_readonly user
            grant_query = f'GRANT SELECT ON TABLE public."{table_name}" TO db_readonly;'
            logger.info(f"Granting SELECT permission: {grant_query}")
            conn.execute(text(grant_query))

        logger.info(f"Dataset successfully imported. Table: {table_name}")

        return self.get_dataset_summary(table_name, df_db)

    def get_dataset_summary(self, table_name: str, df: pd.DataFrame) -> dict:
        """Helper to structure the dataset upload preview/summary response."""
        col_names = list(df.columns)

        def format_dtype(col):
            s = str(df[col].dtype).lower()
            if "int" in s:
                return "INTEGER"
            elif "float" in s or "double" in s or "decimal" in s or "numeric" in s:
                return "NUMERIC"
            elif "bool" in s:
                return "BOOLEAN"
            elif "datetime" in s or "timestamp" in s:
                return "TIMESTAMP"
            else:
                return "VARCHAR"

        column_types = {col: format_dtype(col) for col in col_names}

        # Construct preview (replace NaN values with None for JSON serialization)
        preview_df = df.head(10).where(pd.notnull(df), None)
        preview = preview_df.to_dict(orient="records")

        return {
            "dataset_name": table_name,
            "rows": len(df),
            "columns": len(col_names),
            "column_names": col_names,
            "column_types": column_types,
            "preview": preview,
        }

    def list_datasets(self, db: Session) -> list[dict]:
        """Lists metadata of all uploaded datasets from read-only perspective."""
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()
        uploaded_tables = [t for t in all_tables if t.startswith("uploaded_")]

        datasets = []
        for table in uploaded_tables:
            try:
                # Use PostgreSQL statistics for fast row estimation (Performance Optimization)
                count_res = db.execute(
                    text(
                        f"SELECT reltuples::bigint FROM pg_class WHERE relname = '{table}'"
                    )
                ).scalar()
                if count_res is None or count_res < 0:
                    count_res = db.execute(
                        text(f'SELECT COUNT(*) FROM "{table}"')
                    ).scalar()

                columns = inspector.get_columns(table)
                col_names = [c["name"] for c in columns]
                col_types = {c["name"]: str(c["type"]) for c in columns}

                # Fetch preview rows
                preview_rows = db.execute(
                    text(f'SELECT * FROM "{table}" LIMIT 10')
                ).fetchall()
                preview = [dict(zip(col_names, row)) for row in preview_rows]
                # Scrub null values
                preview = [
                    {k: (None if pd.isna(v) else v) for k, v in row.items()}
                    for row in preview
                ]

                datasets.append(
                    {
                        "dataset_name": table,
                        "rows": count_res,
                        "columns": len(col_names),
                        "column_names": col_names,
                        "column_types": col_types,
                        "preview": preview,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Failed to introspect uploaded dataset '{table}': {str(e)}"
                )

        return datasets

    def get_single_dataset_preview(self, db: Session, table_name: str) -> dict:
        """Retrieves summary and preview of a single uploaded table."""
        if not table_name.startswith("uploaded_"):
            raise ValueError("Only uploaded datasets can be previewed.")

        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Dataset '{table_name}' does not exist.")

        count_res = db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
        columns = inspector.get_columns(table_name)
        col_names = [c["name"] for c in columns]
        col_types = {c["name"]: str(c["type"]) for c in columns}

        preview_rows = db.execute(
            text(f'SELECT * FROM "{table_name}" LIMIT 10')
        ).fetchall()
        preview = [dict(zip(col_names, row)) for row in preview_rows]
        preview = [
            {k: (None if pd.isna(v) else v) for k, v in row.items()} for row in preview
        ]

        return {
            "dataset_name": table_name,
            "rows": count_res,
            "columns": len(col_names),
            "column_names": col_names,
            "column_types": col_types,
            "preview": preview,
        }

    def delete_dataset(self, table_name: str):
        """Drops the table using the privileged write engine."""
        if not table_name.startswith("uploaded_"):
            raise ValueError(
                "Only uploaded tables starting with 'uploaded_' can be deleted."
            )

        logger.info(f"Deleting dataset table: {table_name}")

        with self.write_engine.begin() as conn:
            # Ensure name safety by checking database inspector
            inspector = inspect(self.write_engine)
            if table_name in inspector.get_table_names():
                drop_query = f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'
                logger.info(f"Executing: {drop_query}")
                conn.execute(text(drop_query))
                logger.info(f"Dropped table {table_name}")
            else:
                logger.warning(f"Table '{table_name}' not found for deletion.")


dataset_service = DatasetService()
