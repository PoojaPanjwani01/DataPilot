from pydantic import BaseModel
from typing import List, Optional


class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[dict]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class InsightsResponse(BaseModel):
    insights: str
