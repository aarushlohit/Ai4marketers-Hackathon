from fastapi import APIRouter
from pydantic import BaseModel
from app.tasks.background_tasks import process_meeting_transcript

router = APIRouter()


class MeetingPayload(BaseModel):
    transcript_id: str


@router.post("/trigger/meeting_summary")
def trigger_meeting_workflow(payload: MeetingPayload):
    # Trigger Celery workflow
    task = process_meeting_transcript.delay(payload.transcript_id)
    return {
        "status": "success",
        "task_id": task.id,
        "message": "Workflow triggered successfully",
    }
