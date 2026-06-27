import sqlglot
from sqlglot import exp
from backend.app.config import settings
from backend.app.utils.logger import logger


class GuardService:
    def __init__(self):
        self.max_rows = settings.max_rows_returned

    def validate_and_sanitize_sql(self, sql_query: str) -> str:
        """Parses raw SQL using AST walking to block write statements and enforce LIMIT clauses."""
        try:
            logger.info("Executing SQL Abstract Syntax Tree (AST) safety inspection.")
            # Standardize and parse queries using postgres dialect mapping
            statements = sqlglot.parse(sql_query, read="postgres")

            # 1. Enforce single-statement queries to block stacked injections
            if len(statements) != 1 or not statements[0]:
                logger.warning("SQL validation failed: Multi-statement query detected.")
                raise ValueError(
                    "Query validation failed: Only single statements are permitted."
                )

            expression = statements[0]

            # 2. Assert SELECT/UNION statement formats
            if not isinstance(expression, (exp.Select, exp.Union)):
                logger.warning(
                    f"SQL validation failed: Blocked statement type: {type(expression).__name__}"
                )
                raise ValueError(
                    "Query validation failed: Only SELECT statements are permitted."
                )

            # 3. Walk the AST recursively to scan for write elements
            for node in expression.walk():
                if isinstance(
                    node,
                    (
                        exp.Insert,
                        exp.Update,
                        exp.Delete,
                        exp.Drop,
                        exp.Create,
                        exp.Command,
                    ),
                ) or type(node).__name__.startswith("Alter"):
                    logger.warning(
                        f"SQL validation failed: Blocked mutating statement node: {type(node).__name__}"
                    )
                    raise ValueError(
                        "Query validation failed: Write and schema alterations are prohibited."
                    )

            # 4. Programmatically inject or limit SELECT row bounds
            limit_node = expression.args.get("limit")
            if limit_node:
                try:
                    limit_val = int(str(limit_node.expression))
                    if limit_val > self.max_rows:
                        logger.info(
                            f"Modifying query LIMIT: Capping from {limit_val} to {self.max_rows}."
                        )
                        expression.set(
                            "limit",
                            exp.Limit(expression=exp.Literal.number(self.max_rows)),
                        )
                except (ValueError, TypeError):
                    # Force overwrite if limit format is unparseable
                    expression.set(
                        "limit", exp.Limit(expression=exp.Literal.number(self.max_rows))
                    )
            else:
                logger.info(f"Injecting standard SELECT limit: LIMIT {self.max_rows}.")
                expression = expression.limit(self.max_rows)

            sanitized_sql = expression.sql(dialect="postgres")
            logger.info("SQL query validation completed. Query safety approved.")
            return sanitized_sql

        except Exception as e:
            if not isinstance(e, ValueError):
                logger.error(f"SQL parsing compilation error: {str(e)}")
                raise ValueError(f"Query compilation failure: {str(e)}") from e
            raise e


guard_service = GuardService()
