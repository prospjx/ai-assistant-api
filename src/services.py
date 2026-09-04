from typing import Dict, Any
from src.schemas import AIInsightsResponse

async def generate_ai_insights(student_profile: Dict[str, Any], schedule: Dict[str, Any]) -> AIInsightsResponse:
    """
    Mock AI Analysis Service.
    In a real implementation, this function would construct a prompt string
    from the student_profile and schedule, and send it to OpenAI, Gemini, or Azure AI.
    """
    # For now, we return a mock structured response
    # Real logic would involve:
    # 1. Formatting prompt based on preferences and course layout
    # 2. Call LLM API (e.g. openai.ChatCompletion.acreate)
    # 3. Parse LLM JSON output into AIInsightsResponse
    
    # Calculate simple heuristic for mock warnings
    total_classes = sum(len(classes) for classes in schedule.values())
    
    warnings = []
    suggestions = []
    
    # Basic dummy logic to simulate AI insights based on workload
    if total_classes > 4:
        warnings.append("This schedule has a heavy workload and might violate your difficulty tolerance.")
        suggestions.append("Consider dropping a class or moving one to a different term.")
    elif total_classes < 2:
        warnings.append("You are taking very few credits.")
        suggestions.append("Consider adding an elective.")
        
    summary = "This schedule looks well-balanced." if not warnings else "This schedule requires review."
    
    return AIInsightsResponse(
        summary=summary,
        warnings=warnings,
        suggestions=suggestions
    )
