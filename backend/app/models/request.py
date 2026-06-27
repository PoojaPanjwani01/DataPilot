from pydantic import BaseModel, Field
from typing import List, Dict, Any


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language question to convert into SQL and run.",
    )


class InsightsRequest(BaseModel):
    question: str = Field(
        ..., max_length=2000, description="The original natural language question."
    )
    sql: str
    data: List[Dict[str, Any]]
