from typing import Any

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    student_profile: dict[str, Any]
    schedule: dict[str, Any]


class AIInsightsResponse(BaseModel):
    summary: str
    warnings: list[str]
    suggestions: list[str]


# --- Screenshot Extraction Schemas ---
class ExtractedClass(BaseModel):
    course_id: str
    title: str
    day: str  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    start_time: str  # HH:MM (24-hour)
    end_time: str  # HH:MM (24-hour)
    location: str | None = "TBD"


class ExtractScheduleResponse(BaseModel):
    success: bool
    message: str
    extracted_classes: list[ExtractedClass]


# --- Full Life Routine Schedule Schemas ---
class RoutineBlock(BaseModel):
    day: str  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    activity_type: str  # Class, Transit, Study, Gym, Sleep, Wakeup, Meal, Personal
    title: str  # e.g., "CS-3410 Lecture", "Transit to Campus", "Morning Gym", "Deep Study: Algorithms"
    location: str | None = None
    description: str | None = None


# Concrete model instead of Dict[str, ...] to comply with Gemini Developer API schema constraints
class DayRoutine(BaseModel):
    day: str
    activities: list[RoutineBlock]


class FullLifeScheduleGenaiResponse(BaseModel):
    days: list[DayRoutine]
    ai_insights: AIInsightsResponse


class FullLifeScheduleRequest(BaseModel):
    student_profile: dict[str, Any]
    enrolled_classes: list[ExtractedClass]


class FullLifeScheduleResponse(BaseModel):
    weekly_routine: dict[str, list[RoutineBlock]]
    ai_insights: AIInsightsResponse
