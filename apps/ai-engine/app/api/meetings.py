"""Meeting Intelligence endpoints — processes and summarizes customer meetings."""

import json
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.llm import get_llm
from app.prompts.crm_copilot import MEETING_INTELLIGENCE_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

router = APIRouter()


class MeetingRequest(BaseModel):
    title: str = "Client Call"
    date: str = "Today"
    participants: str = "Account Executive, Customer"
    duration_minutes: int = 30
    transcript: str


class ActionItem(BaseModel):
    task: str
    owner: str
    due_date: Optional[str] = None


class MeetingAnalysisResponse(BaseModel):
    summary: str
    key_points: List[str]
    action_items: List[ActionItem]
    sentiment: str
    follow_up: str


@router.post("/analyze", response_model=MeetingAnalysisResponse)
async def analyze_meeting(payload: MeetingRequest):
    """Analyze a meeting transcript to extract summary, action items, and sentiment."""
    if not payload.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty"
        )

    # Format the prompt to ask the LLM for JSON structure
    prompt_text = MEETING_INTELLIGENCE_PROMPT.format(
        meeting_title=payload.title,
        meeting_date=payload.date,
        participants=payload.participants,
        duration_minutes=payload.duration_minutes,
        transcript=payload.transcript
    )

    # Inject JSON output instruction
    prompt_text += """
    
    CRITICAL: You MUST return ONLY a valid JSON object matching this schema. Do not return markdown, html, or conversational filler.
    JSON Schema:
    {
      "summary": "2-3 sentences overview",
      "key_points": ["point 1", "point 2"],
      "action_items": [
        {"task": "the action item", "owner": "name of owner", "due_date": "YYYY-MM-DD or null"}
      ],
      "sentiment": "positive|neutral|negative",
      "follow_up": "Next step description"
    }
    """

    llm = get_llm()
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt_text)])
        output_text = response.content.strip()

        # strip markdown code blocks if the LLM wrapped it
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
        output_text = output_text.strip()

        parsed = json.loads(output_text)
        return MeetingAnalysisResponse(
            summary=parsed.get("summary", ""),
            key_points=parsed.get("key_points", []),
            action_items=[
                ActionItem(
                    task=item.get("task", ""),
                    owner=item.get("owner", "unknown"),
                    due_date=item.get("due_date")
                )
                for item in parsed.get("action_items", [])
            ],
            sentiment=parsed.get("sentiment", "neutral"),
            follow_up=parsed.get("follow_up", "")
        )
    except json.JSONDecodeError as e:
        # Fallback parsing in case model doesn't return clean JSON
        return MeetingAnalysisResponse(
            summary="Unable to parse summary JSON. Output raw content: " + output_text[:200],
            key_points=[],
            action_items=[],
            sentiment="neutral",
            follow_up=""
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running meeting analysis: {str(e)}"
        )
