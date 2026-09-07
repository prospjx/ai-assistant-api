import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types

from src.schemas import (
    AIInsightsResponse,
    ExtractScheduleResponse,
    ExtractedClass,
    FullLifeScheduleResponse,
    FullLifeScheduleGenaiResponse,
    RoutineBlock
)
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
        
        if response.text:
            parsed_data = json.loads(response.text)
            return AIInsightsResponse(**parsed_data)
        else:
            raise ValueError("Empty response received from Gemini model.")

    except ValueError as ve:
        logger.warning(f"Configuration / Validation error: {ve}")
        return AIInsightsResponse(
            summary="Schedule analysis is running in offline mode (API key not configured).",
            warnings=[str(ve)],
            suggestions=["Set your GEMINI_API_KEY in the .env file to enable live AI insights."]
        )
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return AIInsightsResponse(
            summary="Unable to generate full AI insights at this time.",
            warnings=[f"AI Service Error: {str(e)}"],
            suggestions=["Please verify your Gemini API key and network connection, then try again."]
        )


async def extract_schedule_from_image(image_bytes: bytes, mime_type: str = "image/png") -> ExtractScheduleResponse:
    """
    Extracts class schedule information from an uploaded timetable screenshot using Gemini multimodal vision.
    """
    try:
        client = _get_genai_client()

        prompt = """
You are an AI timetable and schedule parser. Carefully examine the provided image of a student's class schedule or timetable.
Extract all scheduled classes and sections.

For each class, extract:
- course_id: Course code/number (e.g., 'CS-3410', 'MATH-2310', 'CHEM-101')
- title: Name or title of the course (e.g., 'Computer Systems', 'Calculus I'). If not explicitly listed, use the course_id.
- day: Standardized day of the week ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
- start_time: 24-hour time format HH:MM (e.g. '09:00', '13:30', '10:00')
- end_time: 24-hour time format HH:MM (e.g. '10:15', '14:45', '11:15')
- location: Room or building name if visible, otherwise 'TBD' or 'Main Campus'.

Ensure multiple meetings of the same course on different days (e.g. Mon/Wed/Fri) are extracted as separate entries.
Return strictly the JSON matching the ExtractScheduleResponse schema.
"""

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractScheduleResponse,
                temperature=0.1,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            return ExtractScheduleResponse(**data)
        else:
            raise ValueError("No text response from Gemini vision model.")

    except Exception as e:
        logger.error(f"Error extracting schedule from image: {e}", exc_info=True)
        return ExtractScheduleResponse(
            success=False,
            message=f"Failed to extract schedule from image: {str(e)}",
            extracted_classes=[]
        )


async def generate_full_life_schedule(
    student_profile: Dict[str, Any],
    enrolled_classes: List[ExtractedClass]
) -> FullLifeScheduleResponse:
    """
    Synthesizes a complete daily and weekly life schedule integrating academic classes with:
    - Wake up and sleep routines
    - Transit to and from campus
    - Study/homework blocks
    - Gym / workout routines
    - Meals and personal time
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    try:
        client = _get_genai_client()

        prompt = f"""
You are an elite student life and productivity planner AI.
Your goal is to build a complete, realistic, healthy 7-day routine schedule for a student that seamlessly integrates their enrolled academic classes with all their personal life preferences.

Student Profile & Life Preferences:
{json.dumps(student_profile, indent=2)}

Enrolled Academic Classes:
{json.dumps([c.model_dump() for c in enrolled_classes], indent=2)}

Scheduling Rules to Strictly Follow:
1. FIXED CLASSES: The student's academic classes MUST be placed at their exact scheduled day and times. Do not move them. Activity type = "Class".
2. WAKE UP & SLEEP:
   - Schedule wake up around the student's `wake_up_time` preference.
   - Schedule wind-down and sleep around `sleep_time`.
3. COMMUTE / TRANSIT:
   - On days the student has in-person classes, schedule "Transit to Campus" ({student_profile.get('preferences', {}).get('transit_time_minutes', 45)} mins) right before their first class of the day.
   - Schedule "Transit Home" ({student_profile.get('preferences', {}).get('transit_time_minutes', 45)} mins) immediately following their last class of the day.
4. STUDY SESSIONS:
   - Allocate approximately {student_profile.get('preferences', {}).get('study_hours_per_day', 3)} hours of study blocks per day.
   - Place them during logical windows (e.g., in gaps between classes or in the afternoon/evening).
   - Activity type = "Study".
5. WORKOUT / GYM:
   - According to `gym_time_preference` ('{student_profile.get('preferences', {}).get('gym_time_preference', 'afternoon')}') and `gym_duration_minutes` ({student_profile.get('preferences', {}).get('gym_duration_minutes', 60)} mins), place gym sessions on regular workout days without conflicting with classes or transit.
   - Activity type = "Gym".
6. MEALS & DOWNTIME:
   - Include Lunch and Dinner / Relaxation breaks.
   - Activity type = "Meal" or "Personal".
7. NO OVERLAPS: Ensure no activities overlap in time on any given day.
8. FORMAT: All times must be in 24-hour HH:MM format. Days must be one of: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.

Also generate comprehensive AI insights (summary, warnings, and suggestions) analyzing the balance, sleep health, and study pacing of this full routine.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FullLifeScheduleGenaiResponse,
                temperature=0.3,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            genai_resp = FullLifeScheduleGenaiResponse(**data)
            
            # Convert days array into standard weekly_routine mapping
            routine_map: Dict[str, List[RoutineBlock]] = {d: [] for d in days}
            for day_obj in genai_resp.days:
                day_name = day_obj.day.capitalize()
                if day_name in routine_map:
                    routine_map[day_name] = day_obj.activities
                else:
                    routine_map[day_name] = day_obj.activities

            return FullLifeScheduleResponse(
                weekly_routine=routine_map,
                ai_insights=genai_resp.ai_insights
            )
        else:
            raise ValueError("No text response from Gemini model.")

    except Exception as e:
        logger.error(f"Error generating full life schedule: {e}", exc_info=True)
        # Fallback heuristic schedule generation
        weekly_routine: Dict[str, List[RoutineBlock]] = {d: [] for d in days}
        prefs = student_profile.get("preferences", {})
        wake = prefs.get("wake_up_time", "07:00")
        sleep = prefs.get("sleep_time", "23:00")
        transit_mins = prefs.get("transit_time_minutes", 45)

        # Populate classes
        for c in enrolled_classes:
            day = c.day.capitalize()
            if day in weekly_routine:
                weekly_routine[day].append(RoutineBlock(
                    day=day,
                    start_time=c.start_time,
                    end_time=c.end_time,
                    activity_type="Class",
                    title=f"{c.course_id} - {c.title}",
                    location=c.location
                ))

        # Basic fallback routine blocks
        for day in days:
            routine = weekly_routine[day]
            routine.insert(0, RoutineBlock(
                day=day,
                start_time=wake,
                end_time="08:00",
                activity_type="Wakeup",
                title="Morning Routine & Breakfast"
            ))
            routine.append(RoutineBlock(
                day=day,
                start_time="17:00",
                end_time="18:30",
                activity_type="Study",
                title="Focused Study & Review"
            ))
            routine.append(RoutineBlock(
                day=day,
                start_time="19:00",
                end_time="20:00",
                activity_type="Gym",
                title="Workout / Fitness"
            ))
            routine.append(RoutineBlock(
                day=day,
                start_time=sleep,
                end_time="23:59",
                activity_type="Sleep",
                title="Night Sleep"
            ))

        return FullLifeScheduleResponse(
            weekly_routine=weekly_routine,
            ai_insights=AIInsightsResponse(
                summary="Full routine generated with fallback heuristics.",
                warnings=[f"AI note: {str(e)}"],
                suggestions=["Ensure wake and sleep times are adhered to consistently."]
            )
        )
