from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AnalyzeRequest(BaseModel):
    student_profile: Dict[str, Any]
    schedule: Dict[str, Any]

class AIInsightsResponse(BaseModel):
    summary: str
    warnings: List[str]
    suggestions: List[str]

# --- Screenshot Extraction Schemas ---
class ExtractedClass(BaseModel):
    course_id: str
    title: str
    day: str             # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    start_time: str      # HH:MM (24-hour)
    end_time: str        # HH:MM (24-hour)
    location: Optional[str] = "TBD"

class ExtractScheduleResponse(BaseModel):
    success: bool
    message: str
    extracted_classes: List[ExtractedClass]

# --- Full Life Routine Schedule Schemas ---
class RoutineBlock(BaseModel):
    day: str             # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    start_time: str      # HH:MM
    end_time: str        # HH:MM
    activity_type: str   # Class, Transit, Study, Gym, Sleep, Wakeup, Meal, Personal
    title: str           # e.g., "CS-3410 Lecture", "Transit to Campus", "Morning Gym", "Deep Study: Algorithms"
    location: Optional[str] = None
    description: Optional[str] = None

# Concrete model instead of Dict[str, ...] to comply with Gemini Developer API schema constraints
class DayRoutine(BaseModel):
    day: str
    activities: List[RoutineBlock]

class FullLifeScheduleGenaiResponse(BaseModel):
    days: List[DayRoutine]
    ai_insights: AIInsightsResponse

class FullLifeScheduleRequest(BaseModel):
    student_profile: Dict[str, Any]
    enrolled_classes: List[ExtractedClass]

class FullLifeScheduleResponse(BaseModel):
    weekly_routine: Dict[str, List[RoutineBlock]]
    ai_insights: AIInsightsResponse
