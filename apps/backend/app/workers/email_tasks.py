"""Celery tasks: async email delivery through Resend."""

import structlog
import httpx
from celery import shared_task

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, recipient: str, subject: str, body: str):
    """Deliver an HTML email asynchronously using the Resend API."""
    from app.core.config import settings

    if not settings.RESEND_API_KEY:
        logger.info("Skip sending email — RESEND_API_KEY is not configured", recipient=recipient)
        return {"status": "skipped", "reason": "not_configured"}

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.EMAIL_FROM,
                "to": [recipient],
                "subject": subject,
                "html": body,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        result = response.json()
        logger.info("Email sent through Resend", recipient=recipient, subject=subject)
        return {"status": "success", "recipient": recipient, "id": result.get("id")}
    except Exception as exc:
        logger.error("Failed to send email asynchronously", recipient=recipient, error=str(exc))
        raise self.retry(exc=exc)
