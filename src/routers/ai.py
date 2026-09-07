from fastapi import APIRouter, UploadFile, File, HTTPException
from src.schemas import (
    AnalyzeRequest,
    AIInsightsResponse,
    ExtractScheduleResponse,
    FullLifeScheduleRequest,
    FullLifeScheduleResponse
)
from src.services import (
    generate_ai_insights,
    extract_schedule_from_image,
    generate_full_life_schedule
)

router = APIRouter(
    prefix="/analyze",
    tags=["AI Analysis"]
)

@router.post("", response_model=AIInsightsResponse)
async def analyze_schedule(request: AnalyzeRequest):
    """
    Receives a proposed schedule and student profile, and returns AI-generated suggestions.
    """
    insights = await generate_ai_insights(request.student_profile, request.schedule)
    return insights

@router.post("/extract-schedule", response_model=ExtractScheduleResponse)
async def extract_schedule(file: UploadFile = File(...)):
    """
    Parses a schedule screenshot (PNG, JPEG, WEBP) using Gemini Multimodal Vision,
    extracting structured course details and weekly timeslots.
    """
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    content_type = file.content_type or "image/png"
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Please upload a PNG, JPEG, or WEBP image."
        )

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return await extract_schedule_from_image(image_bytes, content_type)

@router.post("/full-schedule", response_model=FullLifeScheduleResponse)
async def create_full_life_schedule(request: FullLifeScheduleRequest):
    """
    Synthesizes a 7-day comprehensive daily and weekly life schedule integrating
    academic classes with transit, study blocks, gym routines, sleep, and meals.
    """
    return await generate_full_life_schedule(request.student_profile, request.enrolled_classes)
