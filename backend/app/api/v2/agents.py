from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat_with_agents(request: ChatRequest):
    # Mock LangGraph multi-agent response
    return {
        "status": "success",
        "response": {
            "root_cause": (
                "The recent SSO update is causing friction during enterprise "
                "onboarding, directly leading to churn."
            ),
            "recommended_action": (
                "Revert SSO module and issue proactive apologies to affected "
                "customers."
            ),
            "agents_involved": ["Sales", "Support", "Executive"],
        },
    }
