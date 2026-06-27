import os
import json
from datetime import datetime
from backend.app.utils.logger import logger


class HistoryService:
    def __init__(self):
        """Resolves target database context tracking parameters."""
        self.history_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "data",
                "query_history.json",
            )
        )
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

        if not os.path.exists(self.history_file):
            try:
                with open(self.history_file, "w", encoding="utf-8") as file:
                    json.dump([], file)
            except Exception as e:
                logger.error(f"Failed to create query history file template: {str(e)}")

    def record_query(
        self,
        user_question: str,
        generated_sql: str,
        status: str,
        execution_time_ms: float,
    ):
        """Appends query execution metadata to the local history file."""
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_question": user_question,
            "generated_sql": generated_sql,
            "status": status,
            "execution_time_ms": round(execution_time_ms, 2),
        }

        try:
            history_data = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as file:
                    try:
                        history_data = json.load(file)
                    except json.JSONDecodeError:
                        history_data = []

            history_data.append(record)

            with open(self.history_file, "w", encoding="utf-8") as file:
                json.dump(history_data, file, indent=2)
            logger.info("Query metrics logged in query_history.json.")
        except Exception as e:
            logger.error(f"Failed to log query telemetry metrics: {str(e)}")


history_service = HistoryService()
