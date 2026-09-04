from fastapi import APIRouter
from src.schemas import AnalyzeRequest, AIInsightsResponse
from src.services import generate_ai_insights

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
