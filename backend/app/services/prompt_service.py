import os
from backend.app.utils.logger import logger


class PromptService:
    def __init__(self):
        """Resolves prompts location and caches prompt templates in-memory at initialization."""
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts")
        )
        self._cache = {}
        self._preload_templates()

    def _preload_templates(self):
        """Preloads prompt files into memory to avoid synchronous disk I/O on API request reruns."""
        templates = ["system_prompt.txt", "sql_generation.txt", "sql_fixing.txt"]
        for filename in templates:
            filepath = os.path.join(self.prompts_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        self._cache[filename] = file.read().strip()
                    logger.info(f"Successfully cached prompt template: {filename}")
                except Exception as e:
                    logger.error(
                        f"Failed to cache prompt file {filename} during startup: {str(e)}"
                    )
            else:
                logger.warning(
                    f"Prompt template file not found for caching: {filename}"
                )

    def _read_prompt_file(self, filename: str) -> str:
        """Reads target prompt files synchronously, checking cache first."""
        if filename in self._cache:
            return self._cache[filename]

        # Fallback reading logic if templates are created dynamically after startup
        filepath = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(filepath):
            logger.error(f"Failed to locate prompt template file at: {filepath}")
            raise FileNotFoundError(f"Missing prompt resource: {filename}")

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().strip()
                self._cache[filename] = content
                return content
        except Exception as e:
            logger.error(f"Error accessing file {filename}: {str(e)}")
            raise IOError(f"Failed to read prompt: {filename}") from e

    def get_system_prompt(self) -> str:
        """Retrieves system identity prompt rules."""
        return self._read_prompt_file("system_prompt.txt")

    def get_sql_generation_prompt(self, schema_context: str, user_question: str) -> str:
        """Loads and formats variables into the text-to-SQL prompt template."""
        template = self._read_prompt_file("sql_generation.txt")
        return template.format(
            schema_context=schema_context, user_question=user_question
        )

    def get_sql_fixing_prompt(
        self, schema_context: str, failed_sql: str, error_message: str
    ) -> str:
        """Loads and formats parameters into the SQL self-correction template."""
        template = self._read_prompt_file("sql_fixing.txt")
        return template.format(
            schema_context=schema_context,
            failed_sql=failed_sql,
            error_message=error_message,
        )


prompt_service = PromptService()
