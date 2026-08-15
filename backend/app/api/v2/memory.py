from fastapi import APIRouter

router = APIRouter()


@router.get("/timeline/{customer_id}")
def get_customer_timeline(customer_id: str):
    # Mock Enterprise Memory response (Neo4j + pgvector)
    return {
        "status": "success",
        "customer_id": customer_id,
        "timeline": [
            {
                "timestamp": "2026-07-15T10:30:00Z",
                "type": "Email",
                "summary": "Follow-up Email Sent regarding contract negotiation.",
            },
            {
                "timestamp": "2026-07-14T14:00:00Z",
                "type": "Meeting",
                "summary": "Discovery Call. Customer interested in Workflow module.",
            },
        ],
    }
