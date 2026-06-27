import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar

# Context variable for request tracing
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")

# Define log path relative to project workspace root
log_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "application.log")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True


logger = logging.getLogger("ai_sql_agent")
logger.setLevel(logging.INFO)

# Prevent registering duplicate handlers upon double imports
if not logger.handlers:
    # Structured JSON log format
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "request_id": "%(request_id)s", "module": "%(module)s", "message": "%(message)s"}'
    )

    logger.addFilter(RequestIdFilter())

    # Console Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
