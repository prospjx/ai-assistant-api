import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types

from src.schemas import AIInsightsResponse
from src.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

def _get_genai_client() -> genai.Client:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set or still has the placeholder value. "
            "Please add your actual Gemini API key to your .env file."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


async def generate_ai_insights(student_profile: Dict[str, Any], schedule: Dict[str, Any]) -> AIInsightsResponse:
    """
    Analyzes student profile and proposed schedule using Google Gemini,
    returning structured insights (summary, warnings, and suggestions).
    """
    try:
        client = _get_genai_client()
        
        prompt = f"""
You are an expert academic advisor AI. Analyze the following student profile and proposed course schedule.
Provide actionable, intelligent insights on workload balance, degree progression, prerequisite concerns, and study stress.

Student Profile:
{json.dumps(student_profile, indent=2)}

Proposed Schedule:
{json.dumps(schedule, indent=2)}

Provide your analysis strictly matching the requested JSON schema with:
- summary: A concise 1-2 sentence overview of how well-balanced or risky this schedule is.
- warnings: A list of potential concerns, pitfalls, or heavy workloads (empty list if none).
- suggestions: Concrete, actionable recommendations to improve or balance the schedule.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIInsightsResponse,
                temperature=0.2,
            ),
        )
        
        # Parse the structured response
        if response.text:
            parsed_data = json.loads(response.text)
            return AIInsightsResponse(**parsed_data)
        else:
            raise ValueError("Empty response received from Gemini model.")

    except ValueError as ve:
        logger.warning(f"Configuration / Validation error: {ve}")
        # Graceful fallback if API key is missing
        return AIInsightsResponse(
            summary="Schedule analysis is running in offline mode (API key not configured).",
            warnings=[str(ve)],
            suggestions=["Set your GEMINI_API_KEY in the .env file to enable live AI insights."]
        )
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        # Graceful fallback with error details
        return AIInsightsResponse(
            summary="Unable to generate full AI insights at this time.",
            warnings=[f"AI Service Error: {str(e)}"],
            suggestions=["Please verify your Gemini API key and network connection, then try again."]
        )
