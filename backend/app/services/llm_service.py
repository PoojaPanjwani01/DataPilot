from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.app.config import settings
from backend.app.utils.logger import logger


class LLMService:
    def __init__(self):
        """Initializes the Google GenAI SDK Client using config settings."""
        try:
            logger.info("Initializing Google GenAI Client.")
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.model_name = "gemini-2.5-flash"
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client context: {str(e)}")
            raise RuntimeError(f"GenAI startup exception: {str(e)}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    def _generate_with_retry(self, system_prompt: str, prompt_content: str):
        """Internal call wrapper equipped with exponential retry logic for transient API issues."""
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            ),
        )

    def generate_sql(self, system_prompt: str, prompt_content: str) -> str:
        """Sends system instructions and prompts to Gemini API for SQL extraction with error retries."""
        try:
            logger.info("Submitting text-to-SQL query payload to Gemini.")
            response = self._generate_with_retry(system_prompt, prompt_content)
            raw_text = response.text
            if not raw_text:
                raise ValueError("Received empty response string from Gemini.")

            raw_text = raw_text.strip()

            # Defensive clean up of Markdown wrappers (e.g. ```sql ... ```)
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            return raw_text
        except Exception as e:
            logger.error(f"Gemini execution failure after retry attempts: {str(e)}")
            raise RuntimeError(f"Failed to generate query text: {str(e)}") from e

    def generate_insights(self, question: str, sql: str, data: list[dict]) -> str:
        """Generates concise business insights from query results using Gemini."""
        try:
            logger.info("Submitting query results to Gemini for insights extraction.")
            # Trim the data size to prevent token limits (first 50 rows)
            trimmed_data = data[:50]

            system_prompt = (
                "You are an expert business analyst and data analyst. "
                "Analyze the provided query execution result to formulate actionable business insights."
            )

            prompt_content = f"""Analyze this query execution result.
User Question: {question}
SQL Query: {sql}
Results Data (JSON): {trimmed_data}

Provide:
1. One key metric or primary finding name (e.g. "Top Brand: Apple" or "Highest Category: Tech")
2. Primary metric value (e.g. "Revenue: $15,000" or "Count: 42")
3. 3-5 bullet points of concise, clear business insights from this dataset.

IMPORTANT: Your entire response must not exceed 500 words.

Format your output exactly as follows:
[Primary Finding Name]
[Primary Value]
Insights:
* Insight bullet 1
* Insight bullet 2
* Insight bullet 3
"""
            response = self._generate_with_retry(system_prompt, prompt_content)
            raw_text = response.text
            if not raw_text:
                raise ValueError("Received empty insights response from Gemini.")
            return raw_text.strip()
        except Exception as e:
            logger.error(
                f"Gemini insights generation failure after retry attempts: {str(e)}"
            )
            raise RuntimeError(f"Failed to generate insights: {str(e)}") from e


llm_service = LLMService()
