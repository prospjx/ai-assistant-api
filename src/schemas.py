from pydantic import BaseModel
from typing import Dict, Any, List

class AnalyzeRequest(BaseModel):
    student_profile: Dict[str, Any]
    schedule: Dict[str, Any]

class AIInsightsResponse(BaseModel):
    summary: str
    warnings: List[str]
    suggestions: List[str]
