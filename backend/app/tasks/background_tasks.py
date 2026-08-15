from app.workflows.engine import celery_app
import time


@celery_app.task
def process_meeting_transcript(transcript_id: str):
    # Mock AI summarization delay
    time.sleep(2)
    return {
        "status": "completed",
        "transcript_id": transcript_id,
        "summary": "Meeting analyzed",
    }


@celery_app.task
def update_deal_confidence(deal_id: str, new_score: float):
    # Mock database update
    time.sleep(1)
    return {"status": "success", "deal": deal_id, "score": new_score}
