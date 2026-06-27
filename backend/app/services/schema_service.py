from sqlalchemy import inspect
from sqlalchemy.orm import Session
from backend.app.utils.logger import logger


class SchemaService:
    def __init__(self):
        self._cached_schema = None

    def get_schema_context(self, db: Session) -> str:
        """Introspects database metadata and caches its text representation for prompt injections."""
        if self._cached_schema:
            return self._cached_schema

        try:
            logger.info("Initializing schema metadata introspection.")
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()

            schema_blocks = []
            for table in tables:
                # Extract basic column names, types, and constraints
                columns = inspector.get_columns(table)
                col_defs = []
                for col in columns:
                    col_name = col["name"]
                    col_type = str(col["type"])
                    nullable = "NULL" if col["nullable"] else "NOT NULL"
                    default = (
                        f" DEFAULT {col['default']}"
                        if col.get("default") is not None
                        else ""
                    )
                    col_defs.append(f"  {col_name} {col_type} {nullable}{default}")

                # Extract primary key structures
                pk_constraint = inspector.get_pk_constraint(table)
                pk_cols = pk_constraint.get("constrained_columns", [])
                if pk_cols:
                    col_defs.append(f"  PRIMARY KEY ({', '.join(pk_cols)})")

                # Extract foreign key structures
                fk_constraints = inspector.get_foreign_keys(table)
                for fk in fk_constraints:
                    ref_table = fk["referred_table"]
                    ref_cols = fk["referred_columns"]
                    const_cols = fk["constrained_columns"]
                    col_defs.append(
                        f"  FOREIGN KEY ({', '.join(const_cols)}) REFERENCES {ref_table}({', '.join(ref_cols)})"
                    )

                # Format table definition context block for prompts injection
                table_ddl = f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n);"
                schema_blocks.append(table_ddl)

            # Format and cache schema representation
            self._cached_schema = "\n\n".join(schema_blocks)
            logger.info("Introspection complete. Database schema cached successfully.")
            return self._cached_schema

        except Exception as e:
            logger.error(f"Error during schema introspection: {str(e)}")
            raise RuntimeError(f"Failed to extract database metadata: {str(e)}") from e

    def clear_cache(self):
        """Invalidates schema cache to support schema migration events."""
        self._cached_schema = None
        logger.info("Schema cache cleared.")


schema_service = SchemaService()
