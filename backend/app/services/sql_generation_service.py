from sqlalchemy.orm import Session
from backend.app.services.schema_service import schema_service
from backend.app.services.prompt_service import prompt_service
from backend.app.services.llm_service import llm_service
from backend.app.utils.logger import logger


class SQLGenerationService:
    def generate_query(self, db: Session, user_question: str) -> str:
        """Retrieves cached database schema metadata and processes queries using Gemini."""
        logger.info(f"Generating query command for: '{user_question}'")

        # Extract metadata structures context
        schema_context = schema_service.get_schema_context(db)

        # Retrieve externalized prompt settings
        system_prompt = prompt_service.get_system_prompt()
        prompt_content = prompt_service.get_sql_generation_prompt(
            schema_context, user_question
        )

        # Direct generation payload call to Gemini API key connection
        generated_sql = llm_service.generate_sql(system_prompt, prompt_content)
        return generated_sql

    def repair_query(self, db: Session, failed_sql: str, error_message: str) -> str:
        """Generates revised SELECT statements after database execution failures."""
        logger.info("Executing self-correction logic on failed SQL string.")

        schema_context = schema_service.get_schema_context(db)
        system_prompt = prompt_service.get_system_prompt()
        prompt_content = prompt_service.get_sql_fixing_prompt(
            schema_context, failed_sql, error_message
        )

        repaired_sql = llm_service.generate_sql(system_prompt, prompt_content)
        return repaired_sql


sql_generation_service = SQLGenerationService()
