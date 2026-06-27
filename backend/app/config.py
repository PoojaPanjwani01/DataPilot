from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    database_url: str = Field(..., alias="DATABASE_URL")
    database_write_url: str = Field(default="", alias="DATABASE_WRITE_URL")
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    query_timeout_seconds: int = Field(default=10, alias="QUERY_TIMEOUT_SECONDS")
    max_rows_returned: int = Field(default=100, alias="MAX_ROWS_RETURNED")
    max_dataset_rows: int = Field(default=100000, alias="MAX_DATASET_ROWS")
    max_dataset_columns: int = Field(default=200, alias="MAX_DATASET_COLUMNS")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
